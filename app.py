import streamlit as st
import pandas as pd
import time
from io import BytesIO
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# 1. Estrutura de Extração Abrangente
class ItemLicitacao(BaseModel):
    numero_item: str = Field(description="Número ou identificador do item/lote no edital (ex: '01', 'Lote 1 - Item 2')")
    descricao: str = Field(description="Descrição técnica completa do medicamento (princípio ativo, dosagem, forma farmacêutica)")
    unidade: str = Field(description="Unidade de fornecimento (ex: AMP, FA, COMP, TB, FR, UN)")
    quantidade: float = Field(description="Quantidade licitada em formato numérico")
    valor_referencia_unitario: float = Field(description="Valor unitário máximo ou de referência do edital")
    laboratorio_sugerido: str = Field(description="Laboratório parceiro prioritário compatível ou 'Outro / Não Mapeado'")
    status_aderencia: str = Field(description="'Alta' se pertence diretamente ao portfólio parceiro, 'Média' se for da mesma classe/similar, ou 'Baixa'")

class ListaItens(BaseModel):
    itens: list[ItemLicitacao]

# 2. Configurações da Página
st.set_page_config(page_title="Radar de Licitações", layout="wide")
st.title("🎯 Analisador de Editais & Mapa de Preços")
st.caption("Faça upload do Termo de Referência ou Edital em PDF para extrair os itens automaticamente.")

# Leitura de segredos / API Key
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Chave Gemini API", type="password")

# 3. Barra Lateral Dinâmica
st.sidebar.header("⚙️ Configurações de Busca")

segmento = st.sidebar.selectbox(
    "Segmento do Edital:",
    options=["Medicamentos", "Material Elétrico / Engenharia", "Personalizado / Geral"]
)

if segmento == "Medicamentos":
    st.sidebar.subheader("💊 Portfólio de Laboratórios")
    labs_base = [
        "Blau",
        "Eurofarma",
        "Baxter",
        "Biocon",
        "Accord",
        "Halex Istar",
        "United Medical",
        "GSK",
        "Aspen",
        "Sanofi",
        "Pint Pharma"
    ]
    
    labs_selecionados = st.sidebar.multiselect(
        "Laboratórios parceiros:",
        options=labs_base,
        default=labs_base
    )
    
    outro_lab = st.sidebar.text_input("Adicionar outro laboratório (opcional):")
    todos_labs = list(labs_selecionados)
    if outro_lab.strip():
        todos_labs.append(outro_lab.strip())
        
    sensibilidade = st.sidebar.radio(
        "Filtro de Extração:",
        ["Apenas Itens Compatíveis (Alta/Média)", "Extrair Todos os Medicamentos do Edital"],
        index=0,
        help="Escolha se deseja ver somente os itens com match de portfólio ou a listagem total do edital classificada."
    )

    st.sidebar.info(
        "**Regras Comerciais:**\n"
        "- 🥇 **Blau** tem prioridade sobre a **Eurofarma** em sobreposição.\n"
        "- 🚫 **Sanofi:** exclui linha Medley (sem genéricos)."
    )

elif segmento == "Material Elétrico / Engenharia":
    portfolio_texto = st.sidebar.text_area(
        "Itens de interesse:",
        value="Material elétrico, cabeamento estruturado, iluminação LED, quadros de distribuição"
    )
else:
    portfolio_texto = st.sidebar.text_area("Itens de interesse:", value="")

arquivo_pdf = st.file_uploader("Arraste o PDF do Edital aqui", type=["pdf"])

# 4. Execução da IA com Fallback contra 503
if arquivo_pdf and api_key:
    if st.button("🚀 Processar Edital", type="primary"):
        with st.spinner("Analisando o edital e cruzando com o portfólio farmacêutico..."):
            try:
                client = genai.Client(api_key=api_key)
                bytes_data = arquivo_pdf.read()

                if segmento == "Medicamentos":
                    prompt = f"""
                    Você é um analista sênior de licitações farmacêuticas e compras hospitalares.
                    Analise todo o documento fornecido (com ênfase no Termo de Referência, Relação de Itens ou Planilhas).

                    Laboratórios parceiros do fornecedor:
                    [{", ".join(todos_labs)}]

                    DIRETRIZES DE ANÁLISE:
                    1. Localize TODOS os itens de medicamentos cotados no documento. NÃO pule itens da tabela.
                    2. Para cada medicamento, avalie a compatibilidade com a linha dos laboratórios parceiros:
                       - BLAU: oncologia, biológicos/eritropoetina/filgrastim, anestésicos, antibióticos injetáveis, heparinas.
                       - EUROFARMA: antibióticos hospitalares, anestésicos, injetáveis gerais, oncologia.
                       - BAXTER: soluções parenterais, anestesia inalatória (sevoflurano, desflurano), oncologia, nutrição clínica.
                       - BIOCON: biossimilares, insulinas, oncologia.
                       - ACCORD: oncologia hospitalar e injetáveis de alta complexidade.
                       - HALEX ISTAR: soluções injetáveis parenterais (eletrólitos, soros, ampolas plásticas).
                       - UNITED MEDICAL: medicamentos para cuidados críticos, oncologia e doenças raras.
                       - GSK: vacinas, biológicos, respiratórios e hospitalares de referência.
                       - ASPEN: anestésicos hospitalares, heparinas, cardiologia e oncologia.
                       - SANOFI: produtos de REFERÊNCIA e especialidades (NÃO incluir Medley, NÃO incluir genéricos).
                       - PINT PHARMA: oncologia, hematologia, imunologia e medicamentos para doenças raras/alta complexidade.
                    3. REGRA DE PRIORIDADE: Caso o item possa ser atendido por Blau e Eurofarma, defina a BLAU como o 'laboratorio_sugerido'.
                    4. Preencha 'status_aderencia' como:
                       - 'Alta': medicamento conhecido dessa linha.
                       - 'Média': medicamento de mesma classe terapêutica passível de cotação.
                       - 'Baixa': fora da linha desses laboratórios.
                    5. Converta quantidades e valores unitários para formato numérico (float).
                    6. Preencha rigorosamente a estrutura JSON solicitada.
                    """
                else:
                    prompt = f"""
                    Você é um analista de licitações. Extraia os itens correspondentes a: "{portfolio_texto}".
                    Estruture no JSON solicitado com quantidades e valores unitários numéricos.
                    """

                # Lista de modelos estáveis em ordem de preferência
                modelos_tentativa = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3.6-flash"]
                resposta = None
                erro_detalhado = None

                for nome_modelo in modelos_tentativa:
                    try:
                        resposta = client.models.generate_content(
                            model=nome_modelo,
                            contents=[
                                types.Part.from_bytes(data=bytes_data, mime_type="application/pdf"),
                                prompt
                            ],
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                response_schema=ListaItens,
                            )
                        )
                        if resposta:
                            break
                    except Exception as err:
                        erro_detalhado = err
                        time.sleep(2)  # Pausa breve antes de tentar o próximo modelo

                if not resposta:
                    raise erro_detalhado

                dados = ListaItens.model_validate_json(resposta.text)

                if not dados.itens:
                    st.warning("Nenhum item foi identificado no edital.")
                else:
                    df = pd.DataFrame([item.model_dump() for item in dados.itens])
                    df.columns = [
                        "Item", 
                        "Descrição / Princípio Ativo", 
                        "Unidade", 
                        "Qtd", 
                        "Valor Ref. Unit. (R$)", 
                        "Laboratório Sugerido", 
                        "Aderência"
                    ]

                    if segmento == "Medicamentos" and sensibilidade == "Apenas Itens Compatíveis (Alta/Média)":
                        df = df[df["Aderência"].isin(["Alta", "Média"])]

                    # Colunas comerciais complementares
                    df["Custo Aquisição (R$)"] = 0.0
                    df["Margem Alvo (%)"] = 15.0
                    df["Preço Proposta Unit. (R$)"] = df["Custo Aquisição (R$)"] * (1 + df["Margem Alvo (%)"] / 100)

                    st.success(f"Foram mapeados {len(df)} itens no edital!")
                    st.dataframe(df, use_container_width=True)

                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False, sheet_name="Mapa_Medicamentos")

                    st.download_button(
                        label="📥 Baixar Mapa de Preços (.xlsx)",
                        data=buffer.getvalue(),
                        file_name=f"Mapa_Precos_{arquivo_pdf.name.replace('.pdf', '')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except Exception as e:
                st.error(f"Erro no processamento: {str(e)}")

elif not api_key:
    st.info("Insira a sua chave de API na barra lateral para iniciar a análise.")