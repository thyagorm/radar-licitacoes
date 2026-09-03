import streamlit as st
import pandas as pd
from io import BytesIO
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

# 1. Estrutura de Dados da Extração
class ItemLicitacao(BaseModel):
    numero_item: str = Field(description="Número ou identificador do item/lote no edital (ex: '01', 'Lote 1 - Item 2')")
    descricao: str = Field(description="Descrição técnica detalhada, princípio ativo, dosagem e forma farmacêutica")
    unidade: str = Field(description="Unidade de fornecimento (ex: AMP, FA, COMP, TB, FR)")
    quantidade: float = Field(description="Quantidade licitada em formato numérico decimal")
    valor_referencia_unitario: float = Field(description="Valor unitário máximo ou estimado de referência no edital")
    laboratorio_prioritario: str = Field(description="Laboratório parceiro indicado para cotação, respeitando as regras de prioridade")

class ListaItens(BaseModel):
    itens: list[ItemLicitacao]

# 2. Configuração da Página e Cabeçalho Principal
st.set_page_config(page_title="Radar de Licitações", layout="wide")
st.title("🎯 Analisador de Editais & Mapa de Preços")
st.caption("Faça upload do Termo de Referência ou Edital em PDF para extrair os itens automaticamente.")

# Leitura segura da API Key
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
    
    # Sua lista de laboratórios parceiros
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
        "Sanofi"
    ]
    
    labs_selecionados = st.sidebar.multiselect(
        "Laboratórios para filtrar:",
        options=labs_base,
        default=labs_base,
        help="Laboratórios parceiros habilitados para análise do edital."
    )
    
    outro_lab = st.sidebar.text_input(
        "Adicionar outro laboratório (opcional):",
        placeholder="Ex: Cristália, Fresenius..."
    )
    
    todos_labs = list(labs_selecionados)
    if outro_lab.strip():
        todos_labs.append(outro_lab.strip())
        
    st.sidebar.info(
        "**Regras de Negócio Ativas:**\n"
        "- 🥇 **Blau** tem prioridade sobre a **Eurofarma** em caso de sobreposição.\n"
        "- 🚫 **Sanofi:** exclui linha Medley (sem genéricos)."
    )

elif segmento == "Material Elétrico / Engenharia":
    st.sidebar.subheader("⚡ Portfólio Elétrico")
    portfolio_texto = st.sidebar.text_area(
        "Itens de interesse:",
        value="Material elétrico, cabeamento estruturado, iluminação LED, quadros de distribuição",
        help="Especifique materiais e serviços que sua empresa atende."
    )

else:
    st.sidebar.subheader("📋 Portfólio Geral")
    portfolio_texto = st.sidebar.text_area(
        "Itens de interesse:",
        value="",
        placeholder="Digite os tipos de produtos, serviços ou palavras-chave...",
        help="Informe os produtos ou serviços que deseja filtrar."
    )

arquivo_pdf = st.file_uploader("Arraste o PDF do Edital aqui", type=["pdf"])

# 4. Execução da IA com Regras Específicas
if arquivo_pdf and api_key:
    # Verificação de segurança
    if segmento == "Medicamentos" and not todos_labs:
        st.warning("⚠️ Selecione pelo menos um laboratório na barra lateral para prosseguir.")
    elif segmento != "Medicamentos" and not portfolio_texto.strip():
        st.warning("⚠️ Preencha os itens de interesse na barra lateral.")
    else:
        if st.button("🚀 Processar Edital", type="primary"):
            with st.spinner("Analisando o documento e aplicando regras de portfólio..."):
                try:
                    client = genai.Client(api_key=api_key)
                    bytes_data = arquivo_pdf.read()

                    # Construção dinâmica do prompt com as regras do laboratório
                    if segmento == "Medicamentos":
                        prompt = f"""
                        Você é um analista sênior de licitações hospitalares especializado em medicamentos.
                        Analise minuciosamente todo o documento fornecido (Termo de Referência, Relação de Itens ou Edital).

                        Laboratórios parceiros habilitados:
                        [{", ".join(todos_labs)}]

                        REGRAS MANDATÓRIAS DE FILTRAGEM:
                        1. Extraia APENAS os itens de medicamentos compatíveis com o portfólio dos laboratórios habilitados selecionados.
                        2. REGRA DE PRIORIDADE: Se um princípio ativo/medicamento for produzido por BLAU e por EUROFARMA, priorize sempre a BLAU como o 'laboratorio_prioritario'.
                        3. REGRA SANOFI: Em relação à Sanofi, considere apenas a linha de referência e especialidades da Sanofi. NUNCA extraia genéricos ou produtos da MEDLEY (Medley está terminantemente proibida).
                        4. Converta quantidades e valores unitários de referência para números decimais (float).
                        5. Preencha rigorosamente a estrutura JSON solicitada.
                        """
                    else:
                        prompt = f"""
                        Você é um analista sênior de licitações.
                        Analise o documento fornecido e extraia APENAS os itens correspondentes a:
                        "{portfolio_texto}"
                        Converta quantidades e valores unitários para formato numérico float.
                        Preencha o schema JSON solicitado.
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
                        st.warning("Nenhum item compatível com as diretrizes e laboratórios foi encontrado neste edital.")
                    else:
                        df = pd.DataFrame([item.model_dump() for item in dados.itens])
                        df.columns = [
                            "Item", 
                            "Descrição / Princípio Ativo", 
                            "Unidade", 
                            "Qtd", 
                            "Valor Ref. Unit. (R$)", 
                            "Laboratório Alvo"
                        ]

                        # Colunas comerciais para cotação e composição de preço
                        df["Custo Aquisição (R$)"] = 0.0
                        df["Margem Alvo (%)"] = 15.0
                        df["Preço Proposta (R$)"] = df["Custo Aquisição (R$)"] * (1 + df["Margem Alvo (%)"] / 100)

                        st.success(f"Encontrados {len(df)} itens compatíveis com o seu portfólio de laboratórios!")
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
    st.info("Insira a chave da API na barra lateral ou configure nos secrets do Streamlit Cloud.")