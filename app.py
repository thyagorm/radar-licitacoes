import streamlit as st
import pandas as pd
import time
from io import BytesIO
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from pypdf import PdfReader

# 1. Estrutura de Extração
class ItemLicitacao(BaseModel):
    numero_item: str = Field(description="Número ou identificador do item/lote no edital (ex: '01', 'Lote 1 - Item 2')")
    descricao: str = Field(description="Descrição técnica completa do medicamento ou item")
    unidade: str = Field(description="Unidade de fornecimento (ex: AMP, FA, COMP, TB, FR, UN)")
    quantidade: float = Field(description="Quantidade licitada em formato numérico")
    valor_referencia_unitario: float = Field(description="Valor unitário de referência do edital")
    laboratorio_sugerido: str = Field(description="Laboratório parceiro prioritário compatível ou 'Outro / Não Mapeado'")
    status_aderencia: str = Field(description="'Alta' se pertence diretamente ao portfólio parceiro, 'Média' se for similar, ou 'Baixa'")

class ListaItens(BaseModel):
    itens: list[ItemLicitacao]

# 2. Configurações da Página
st.set_page_config(page_title="Radar de Licitações", layout="wide")
st.title("🎯 Analisador de Editais & Mapa de Preços")
st.caption("Faça upload do Termo de Referência ou Edital em PDF para extrair os itens automaticamente.")

if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Chave Gemini API", type="password")

# 3. Barra Lateral
st.sidebar.header("⚙️ Configurações de Busca")

segmento = st.sidebar.selectbox(
    "Segmento do Edital:",
    options=["Medicamentos", "Material Elétrico / Engenharia", "Personalizado / Geral"]
)

if segmento == "Medicamentos":
    st.sidebar.subheader("💊 Portfólio de Laboratórios")
    labs_base = [
        "Blau", "Eurofarma", "Baxter", "Biocon", "Accord",
        "Halex Istar", "United Medical", "GSK", "Aspen", "Sanofi", "Pint Pharma"
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
        index=0
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

# Função auxiliar para extrair texto do PDF localmente
def extrair_texto_pdf(arquivo_carregado):
    leitor = PdfReader(arquivo_carregado)
    texto_total = []
    for i, pagina in enumerate(leitor.pages):
        conteudo = pagina.extract_text()
        if conteudo:
            texto_total.append(f"--- PÁGINA {i+1} ---\n{conteudo}")
    return "\n\n".join(texto_total)

# 4. Execução da IA
if arquivo_pdf and api_key:
    if st.button("🚀 Processar Edital", type="primary"):
        with st.spinner("Extraindo texto do edital e consultando a IA..."):
            try:
                texto_edital = extrair_texto_pdf(arquivo_pdf)

                if not texto_edital.strip():
                    st.error("O PDF parece ser uma imagem digitalizada sem camada de texto pesquisável.")
                    st.stop()

                client = genai.Client(api_key=api_key)

                if segmento == "Medicamentos":
                    prompt = f"""
                    Você é um analista sênior de licitações farmacêuticas.
                    Analise o texto deste edital (foco no Termo de Referência ou tabelas de itens):

                    Laboratórios parceiros:
                    [{", ".join(todos_labs)}]

                    DIRETRIZES:
                    1. Extraia os itens de medicamentos demandados.
                    2. Para cada medicamento, identifique a compatibilidade com a linha dos laboratórios:
                       - BLAU: oncologia, biológicos/eritropoetina/filgrastim, anestésicos, antibióticos injetáveis, heparinas.
                       - EUROFARMA: antibióticos hospitalares, anestésicos, injetáveis gerais, oncologia.
                       - BAXTER: soluções parenterais, anestesia inalatória, oncologia, nutrição clínica.
                       - BIOCON: biossimilares, insulinas, oncologia.
                       - ACCORD: oncologia hospitalar e injetáveis de alta complexidade.
                       - HALEX ISTAR: soluções injetáveis parenterais.
                       - UNITED MEDICAL: terapia intensiva, oncologia e doenças raras.
                       - GSK: vacinas, biológicos, respiratórios e hospitalares de referência.
                       - ASPEN: anestésicos hospitalares, heparinas, oncologia.
                       - SANOFI: produtos de REFERÊNCIA e especialidades (NÃO incluir Medley, sem genéricos).
                       - PINT PHARMA: oncologia, hematologia, imunologia, doenças raras.
                    3. PRIORIDADE: Se o item puder ser Blau e Eurofarma, defina BLAU como o 'laboratorio_sugerido'.
                    4. 'status_aderencia': 'Alta' (pertence à linha), 'Média' (mesma classe), 'Baixa' (fora).
                    5. Converta quantidades e valores unitários para formato numérico float.

                    TEXTO DO EDITAL:
                    \"\"\"
                    {texto_edital}
                    \"\"\"
                    """
                else:
                    prompt = f"""
                    Você é um analista de licitações. Extraia os itens correspondentes a: "{portfolio_texto}".
                    Estruture no JSON solicitado com quantidades e valores unitários numéricos float.

                    TEXTO DO EDITAL:
                    \"\"\"
                    {texto_edital}
                    \"\"\"
                    """

                # Modelos de fallback caso algum servidor apresente fila
                modelos_tentativa = ["gemini-3.6-flash", "gemini-1.5-flash"]
                resposta = None
                ultimo_erro = None

                for nome_modelo in modelos_tentativa:
                    try:
                        resposta = client.models.generate_content(
                            model=nome_modelo,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                response_schema=ListaItens,
                            )
                        )
                        if resposta:
                            break
                    except Exception as err:
                        ultimo_erro = err
                        time.sleep(2)

                if not resposta:
                    raise ultimo_erro

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