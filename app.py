import streamlit as st
import pandas as pd
from io import BytesIO
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# 1. Definição da Estrutura de Extração
class ItemLicitacao(BaseModel):
    numero_item: str = Field(description="Número ou identificador do item (ex: '01', '1.1')")
    descricao: str = Field(description="Descrição técnica completa do item/serviço")
    unidade: str = Field(description="Unidade de medida (ex: UN, M, KG, CJ, SV)")
    quantidade: float = Field(description="Quantidade demandada expressa em número")
    valor_referencia_unitario: float = Field(description="Valor unitário estimado/máximo do edital")

class ListaItens(BaseModel):
    itens: list[ItemLicitacao]

# 2. Interface da Aplicação
st.set_page_config(page_title="Radar de Licitações", layout="wide")
st.title("🎯 Analisador de Editais & Mapa de Preços")
st.caption("Faça upload do Termo de Referência ou Edital em PDF para extrair os itens automaticamente.")

# Leitura segura da chave de API
if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Chave Gemini API", type="password")

portfolio_usuario = st.sidebar.text_area(
    "Filtro de Portfólio (Itens de interesse)",
    value="Material elétrico, cabeamento estruturado, iluminação LED, quadros de distribuição",
    help="Especifique os tipos de materiais ou serviços que a sua empresa fornece."
)

arquivo_pdf = st.file_uploader("Arraste o PDF do Edital aqui", type=["pdf"])

# 3. Execução da IA
if arquivo_pdf and api_key:
    if st.button("🚀 Processar Edital", type="primary"):
        with st.spinner("Analisando o documento e filtrando os itens do portfólio..."):
            try:
                client = genai.Client(api_key=api_key)
                bytes_data = arquivo_pdf.read()

                prompt = f"""
                Você é um analista sênior de licitações.
                Analise todo o documento fornecido (com foco no Termo de Referência ou tabela de itens).
                
                Instruções:
                1. Localize a tabela ou listagem com a relação de itens licitados.
                2. Filtre e extraia APENAS os itens relacionados ao seguinte portfólio:
                   "{portfolio_usuario}"
                3. Converta quantidades e valores numéricos no formato decimal padrão (float).
                4. Preencha rigorosamente a estrutura JSON solicitada.
                """

                resposta = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=[
                        types.Part.from_bytes(data=bytes_data, mime_type="application/pdf"),
                        prompt
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ListaItens,
                    )
                )

                dados = ListaItens.model_validate_json(resposta.text)

                if not dados.itens:
                    st.warning("Nenhum item correspondente ao seu portfólio foi encontrado neste edital.")
                else:
                    df = pd.DataFrame([item.model_dump() for item in dados.itens])
                    df.columns = ["Item", "Descrição", "Unidade", "Qtd", "Valor Ref. Unitário (R$)"]
                    
                    # Colunas comerciais complementares
                    df["Fornecedor / Cotação (R$)"] = 0.0
                    df["Margem Alvo (%)"] = 20.0
                    df["Preço Final Proposta (R$)"] = df["Fornecedor / Cotação (R$)"] * (1 + df["Margem Alvo (%)"] / 100)

                    st.success(f"Foram identificados {len(df)} itens aderentes ao seu portfólio!")
                    st.dataframe(df, use_container_width=True)

                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False, sheet_name="Mapa_de_Precos")

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