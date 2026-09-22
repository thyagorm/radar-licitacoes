import os
import re
import json
import time
import unicodedata
from io import BytesIO
from typing import List, Dict, Any
import pandas as pd
from pydantic import BaseModel, Field
from pypdf import PdfReader
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from google import genai
from google.genai import types

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_PORTFOLIO = os.path.join(BASE_DIR, "portfolio_laboratorios.xlsx")

STOP_WORDS_FARMA = {
    "ACETATO", "CLORIDRATO", "SULFATO", "FOSFATO", "DIPROPIONATO", "BROMETO", 
    "CITRATO", "SODICO", "SODICA", "POTASSICO", "POTASSICA", "MALEATO", 
    "SUCCINATO", "HEMISSULFATO", "MESILATO", "TARTARATO", "GLICONATO", "PO", 
    "SOLUCAO", "INJETAVEL", "COMPRIMIDO", "SUSPENSAO", "GOTAS", "CAPSULA", 
    "FRASCO", "AMPOLA", "BISNAGA", "CREME", "POMADA", "XAROPE"
}

MAPEAMENTO_LABS = {
    "Pint Pharma": ["PINT", "PINT PHARMA"],
    "Sanofi": ["SANOFI", "AVENTIS", "WINTHROP", "SANOFI MEDLEY", "SANOFI-AVENTIS"],
    "Blau": ["BLAU"],
    "Eurofarma": ["EUROFARMA"],
    "Baxter": ["BAXTER"],
    "Biocon": ["BIOCON"],
    "Accord": ["ACCORD"],
    "Halex Istar": ["HALEX", "ISTAR"],
    "United Medical": ["UNITED MEDICAL", "UNITED"],
    "GSK": ["GSK", "GLAXO", "GLAXOSMITHKLINE"],
    "Aspen": ["ASPEN"]
}

class ItemLicitacao(BaseModel):
    numero_item: str = Field(description="Número do item na licitação (ex: '1', '2', '3')")
    descricao: str = Field(description="Descrição completa do medicamento com dosagem e forma")
    principio_ativo: str = Field(description="Substância ativa / Princípio Ativo (DCI/DCB)")
    unidade: str = Field(default="UN", description="Unidade de fornecimento (ex: COMP, AMPOLA, FRASCO)")
    quantidade: float = Field(default=1.0, description="Quantidade solicitada")
    valor_referencia_unitario: float = Field(default=0.0, description="Preço unitário de referência (ou 0.0)")

class ExtracaoEdital(BaseModel):
    itens: list[ItemLicitacao]

def normalizar_texto(texto: Any) -> str:
    if not texto or pd.isna(texto):
        return ""
    nfkd = unicodedata.normalize('NFKD', str(texto))
    texto_sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    texto_limpo = re.sub(r'[^A-Z0-9\s]', ' ', texto_sem_acento.upper())
    return " ".join(texto_limpo.split())

def carregar_portfolio() -> pd.DataFrame:
    if not os.path.exists(ARQUIVO_PORTFOLIO):
        return None
    try:
        df = pd.read_excel(ARQUIVO_PORTFOLIO)
        df.columns = [str(c).strip().upper() for c in df.columns]
        for col in ["SUBSTÂNCIA", "LABORATÓRIO", "PRODUTO", "APRESENTAÇÃO"]:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        return df
    except Exception:
        return None

def isolar_paginas_tabela(bytes_arquivo: bytes) -> str:
    """
    PRÉ-PROCESSADOR LOCAL (Custo Zero Tokens):
    - Identifica início dos Anexos / Termo de Referência
    - Corta sumariamente após início de Minutas de Contrato ou Declarações
    - Extrai apenas páginas que contêm dados de itens/quantitativos
    """
    leitor = PdfReader(BytesIO(bytes_arquivo))
    total_pags = len(leitor.pages)
    print(f"📄 PDF carregado com {total_pags} páginas. Iniciando corte inteligente...")

    SECOES_CORTE = [
        "MINUTA DE CONTRATO", "MINUTA DO CONTRATO", "MODELO DE PROCURACAO",
        "MODELO DE DECLARACAO", "DECLARACOES MODELO", "SANCOES ADMINISTRATIVAS",
        "CLAUSULAS CONTRATUAIS", "DA RESCISAO"
    ]

    TERMOS_ITENS = [
        "TERMO DE REFERENCIA", "ANEXO I", "ESPECIFICACAO DOS ITENS", 
        "ESPECIFICACOES DOS ITENS", "RELACAO DE ITENS", "QUANTITATIVO", 
        "MEDICAMENTO", "APRESENTACAO", "VALOR ESTIMADO", "VALOR DE REFERENCIA",
        "VALOR UNITARIO", "PRECO ESTIMADO"
    ]

    paginas_uteis = []
    corte_encontrado = False

    for idx, pagina in enumerate(leitor.pages):
        raw = pagina.extract_text() or ""
        norm = normalizar_texto(raw)

        # 1. Checa gatilho de interrupção (descarte das minutas e anexos jurídicos posteriores)
        if any(corte in norm for corte in SECOES_CORTE):
            # Se a página tiver quantitativos claros de itens antes do texto da minuta, ainda aproveita a página
            if not ("QUANTIDADE" in norm and ("VALOR UNITARIO" in norm or "MEDICAMENTO" in norm)):
                print(f"✂️ Corte efetuado na página {idx+1} devido à seção jurídica final.")
                corte_encontrado = True
                break

        # 2. Avaliação de relevância da página
        score = sum(1 for termo in TERMOS_ITENS if termo in norm)
        tem_padrao_item = bool(re.search(r'\b(ITEM|LOTE)\s*\d+\b', norm))

        # Se tem densidade de tabela de medicamentos ou especificações
        if score >= 2 or (tem_padrao_item and ("QUANTIDADE" in norm or "UNIDADE" in norm)):
            paginas_uteis.append(f"--- PÁGINA {idx+1} ---\n{raw}")

    # Fallback de segurança se o PDF for muito curto ou os cabeçalhos variarem
    if not paginas_uteis:
        print("⚠️ Gatilhos específicos não pontuaram. Usando fallback das primeiras páginas.")
        limite = min(15, total_pags)
        for i in range(limite):
            paginas_uteis.append(leitor.pages[i].extract_text() or "")

    print(f"🎯 Redução concluída: de {total_pags} páginas para {len(paginas_uteis)} páginas enviadas ao Gemini.")
    return "\n\n".join(paginas_uteis)

def extrair_tabela_com_ia(texto_tabela: str, api_key: str) -> List[Dict[str, Any]]:
    client = genai.Client(api_key=api_key)
    modelos_candidatos = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3.6-flash"]

    prompt = f"""
    Voce deve analisar o texto de um edital de compras publicas hospitalares e extrair TODOS os itens, medicamentos, insumos ou principios ativos citados na cotação.

    TEXTO DO EDITAL:
    {texto_tabela}

    INSTRUCOES:
    - Encontre qualquer mencao a medicamento, farmaco ou principio ativo (como ENOXAPARINA, DIPIRONA, etc.).
    - Se encontrar o item, preencha:
      - numero_item: o identificador (ex: '1', '01', 'LOTE 1', ou '1' se nao explicitado)
      - descricao: a descricao do produto com dosagem/apresentacao
      - principio_ativo: o nome da substancia farmaceutica ativa (ex: 'ENOXAPARINA SODICA')
      - unidade: 'UN', 'FRASCO', 'SERINGA', 'AMPOLA', etc.
      - quantidade: a quantidade física/numérica solicitada para o item (ex: 5000, 10000, 500). Procure em colunas como 'QTD', 'QUANTIDADE', 'QUANT.', 'DEMANDA' ou logo após a apresentação. Se encontrar termos com ponto (ex: '10.000'), converta para o float 10000.0. Apenas se for totalmente omitida no edital, use 1.0.
      - valor_referencia_unitario: valor estimado unitario em reais (se nao houver, coloque 0.0)
    - Extraia todos os itens que representem produtos licitados.
    """

    ultimo_erro = None
    for modelo in modelos_candidatos:
        for tentativa in range(3):
            try:
                resposta = client.models.generate_content(
                    model=modelo,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ExtracaoEdital,
                        temperature=0.0
                    )
                )
                dados = ExtracaoEdital.model_validate_json(resposta.text)
                return [item.model_dump() for item in dados.itens]
            except Exception as e:
                ultimo_erro = e
                msg = str(e)
                if "503" in msg or "UNAVAILABLE" in msg or "429" in msg:
                    time.sleep(2 * (tentativa + 1))
                    continue
                else:
                    break

    raise Exception(f"Falha na extracao por IA: {str(ultimo_erro)}")

def enriquecer_com_portfolio(itens_extraidos: List[Dict[str, Any]], labs_escolhidos: List[str]) -> pd.DataFrame:
    df_port = carregar_portfolio()
    if df_port is None or df_port.empty or not itens_extraidos:
        return pd.DataFrame()

    base = df_port.copy()
    base["SUBSTANCIA_NORM"] = base["SUBSTÂNCIA"].apply(normalizar_texto)
    base["LABORATORIO_NORM"] = base["LABORATÓRIO"].apply(normalizar_texto)
    base["PRODUTO_NORM"] = base["PRODUTO"].apply(normalizar_texto)
    base["APRESENTACAO_NORM"] = base["APRESENTAÇÃO"].apply(normalizar_texto) if "APRESENTAÇÃO" in base.columns else ""

    # Exclui Medley
    # Identifica produtos de marca e exclusivos da Sanofi (Não são cópias genéricas)
    eh_produto_generico = (
        base["PRODUTO_NORM"].str.contains(r"\bGENERIC", na=False, regex=True) |
        base["APRESENTACAO_NORM"].str.contains(r"\bGENERIC", na=False, regex=True) |
        (
            # Caso em que o produto comercial não tem marca e é apenas o nome da molécula (genérico puro da Medley)
            base["LABORATORIO_NORM"].str.contains("MEDLEY", na=False) &
            (base["PRODUTO_NORM"] == base["SUBSTANCIA_NORM"])
        )
    )
    
    # Se o produto for uma marca conhecida de referência da Sanofi, NUNCA é descartado como genérico
    marcas_referencia_sanofi = [
        "CLEXANE", "LANTUS", "TOUJEO", "PLAVIX", "AMARYL", "APIDRA", 
        "SULIQUA", "VALPAKINE", "SABRIL", "RIFOCINA", "TARCEVA", "TAXOTERE", "ELOXATIN"
    ]
    eh_referencia_sanofi = base["PRODUTO_NORM"].apply(lambda p: any(m in p for m in marcas_referencia_sanofi))
    
    # Aplica o descarte estritamente sobre os genéricos/cópias
    base_valida = base[~eh_produto_generico | eh_referencia_sanofi]
    
    termos_busca_labs = []
    for lab in labs_escolhidos:
        termos_busca_labs.extend(MAPEAMENTO_LABS.get(lab, [normalizar_texto(lab)]))

    base_valida = base_valida[base_valida["LABORATORIO_NORM"].apply(
        lambda lab_nome: any(t in lab_nome for t in termos_busca_labs)
    )]

    itens_finais = []

    for it in itens_extraidos:
        substancia_edital = normalizar_texto(it.get("principio_ativo", ""))
        desc_completa = normalizar_texto(it.get("descricao", ""))

        if not substancia_edital or len(substancia_edital) < 3:
            continue

        palavras_edital = [p for p in substancia_edital.split() if len(p) > 3 and p not in STOP_WORDS_FARMA]

        m1 = base_valida["SUBSTANCIA_NORM"].apply(lambda s: bool(s and (s in substancia_edital or substancia_edital in s))).astype(bool)
        m2 = base_valida["PRODUTO_NORM"].apply(lambda p: bool(p and len(p) > 3 and (p in desc_completa or p in substancia_edital))).astype(bool)
        m3 = base_valida["SUBSTANCIA_NORM"].apply(lambda s: bool(any(p in s for p in palavras_edital)) if palavras_edital else False).astype(bool)
        matches = base_valida[m1 | m2 | m3]

        if not matches.empty:
            labs_encontrados = matches["LABORATORIO_NORM"].unique().tolist()
            
            if any("PINT" in l for l in labs_encontrados):
                lab_final = [l for l in labs_encontrados if "PINT" in l][0]
            elif any("SANOFI" in l or "AVENTIS" in l or "MEDLEY" in l for l in labs_encontrados):
                lab_final = [l for l in labs_encontrados if "SANOFI" in l][0]
            elif any("UNITED" in l for l in labs_encontrados):
                lab_final = [l for l in labs_encontrados if "UNITED" in l][0]
            elif any("BAXTER" in l for l in labs_encontrados):
                lab_final = [l for l in labs_encontrados if "BAXTER" in l][0]
            elif any("BLAU" in l for l in labs_encontrados):
                lab_final = [l for l in labs_encontrados if "BLAU" in l][0]
            elif any("EUROFARMA" in l for l in labs_encontrados):
                lab_final = [l for l in labs_encontrados if "EUROFARMA" in l][0]
            else:
                lab_final = labs_encontrados[0]

            linha = matches[matches["LABORATORIO_NORM"] == lab_final].iloc[0]
            qtd = float(it.get("quantidade", 1.0))
            vref = float(it.get("valor_referencia_unitario", 0.0))

            itens_finais.append({
                "Item": it.get("numero_item", ""),
                "Descrição Completa Edital": it.get("descricao", ""),
                "Princípio Ativo": linha["SUBSTÂNCIA"],
                "Laboratório Sugerido": linha["LABORATÓRIO"],
                "Produto / Marca Ref.": linha["PRODUTO"],
                "Qtd": qtd,
                "Valor Ref. Unit. (R$)": vref,
                "Valor Total Estimado (R$)": qtd * vref,
                "Custo Aquisição (R$)": 0.0,
                "Margem Alvo (%)": 0.15,
                "Preço Proposta Unit. (R$)": 0.0
            })

    df_out = pd.DataFrame(itens_finais)
    if not df_out.empty:
        try:
            df_out["_num"] = pd.to_numeric(df_out["Item"].str.extract(r'(\d+)')[0], errors="coerce")
            df_out = df_out.sort_values(by="_num").drop(columns=["_num"])
        except Exception:
            pass

    return df_out

def gerar_excel_bytes(df_dados: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_dados.to_excel(writer, index=False, sheet_name="Mapa_de_Precos")
        ws = writer.sheets["Mapa_de_Precos"]
        ws.views.sheetView[0].showGridLines = True

        fonte_cabecalho = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        fill_cabecalho = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
        fonte_corpo = Font(name="Calibri", size=10)
        fill_editavel = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
        borda_fina = Border(
            left=Side(style="thin", color="D9D9D9"), right=Side(style="thin", color="D9D9D9"),
            top=Side(style="thin", color="D9D9D9"), bottom=Side(style="thin", color="D9D9D9")
        )

        num_linhas = len(df_dados)
        colunas_nomes = list(df_dados.columns)
        for col_num in range(1, len(colunas_nomes) + 1):
            celula = ws.cell(row=1, column=col_num)
            celula.font = fonte_cabecalho
            celula.fill = fill_cabecalho
            celula.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 28

        for r_idx in range(2, num_linhas + 2):
            ws.row_dimensions[r_idx].height = 20
            for c_idx in range(1, len(colunas_nomes) + 1):
                cell = ws.cell(row=r_idx, column=c_idx)
                nome = colunas_nomes[c_idx - 1]
                cell.font = fonte_corpo
                cell.border = borda_fina
                if nome == "Item":
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                elif nome in ["Descrição Completa Edital", "Princípio Ativo", "Laboratório Sugerido", "Produto / Marca Ref."]:
                    cell.alignment = Alignment(horizontal="left", vertical="center")
                elif nome == "Qtd":
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    cell.number_format = "#,##0"
                elif nome in ["Valor Ref. Unit. (R$)", "Valor Total Estimado (R$)"]:
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    cell.number_format = "R$ #,##0.00"
                elif nome == "Custo Aquisição (R$)":
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    cell.number_format = "R$ #,##0.00"
                    cell.fill = fill_editavel
                elif nome == "Margem Alvo (%)":
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    cell.number_format = "0.0%"
                    cell.value = 0.15
                elif nome == "Preço Proposta Unit. (R$)":
                    cell.alignment = Alignment(horizontal="right", vertical="center")
                    cell.number_format = "R$ #,##0.00"

        for col in ws.columns:
            letter = get_column_letter(col[0].column)
            max_len = max(len(str(cell.value or '')) for cell in col)
            ws.column_dimensions[letter].width = max(max_len + 4, 13)

        if "Descrição Completa Edital" in colunas_nomes:
            ws.column_dimensions[get_column_letter(colunas_nomes.index("Descrição Completa Edital") + 1)].width = 45

    return output.getvalue()
