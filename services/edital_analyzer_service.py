import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("edital_analyzer")

def analisar_edital_com_ia(dados_edital: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analisa os dados e o termo de referência do edital com IA, gerando resumo, itens e mapa de riscos.
    """
    objeto = dados_edital.get("objeto", "Não especificado")
    orgao = dados_edital.get("orgao_nome", "Órgão Público")
    valor = dados_edital.get("valor_estimado", 0.0)
    numero = dados_edital.get("numero_edital", "-")
    uf = dados_edital.get("uf", "BR")

    gemini_key = os.getenv("GEMINI_API_KEY", "")

    if gemini_key:
        try:
            from google import genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-2.5-flash")

            prompt = f"""
            Você é um especialista em licitações públicas brasileiras (Lei 14.133/21).
            Analise as informações do seguinte edital e gere um parecer técnico estruturado em JSON:

            Órgão: {orgao} ({uf})
            Processo/Edital: {numero}
            Valor Estimado: R$ {valor:,.2f}
            Objeto: {objeto}

            Formato estritamente JSON:
            {{
                "resumo_executivo": "...",
                "segmento": "...",
                "complexidade": "Baixa" | "Média" | "Alta",
                "itens_provaveis": [
                    {{"item": "...", "quantidade_estimada": "...", "unidade": "...", "observacao": "..."}}
                ],
                "requisitos_habilitacao": [
                    "...", "..."
                ],
                "pontos_atencao_riscos": [
                    "...", "..."
                ],
                "estrategia_precificacao": "..."
            }}
            """
            resposta = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(resposta.text)
        except Exception as e:
            logger.warning(f"Fallback para análise heurística: {e}")

    # Fallback estruturado inteligente caso não haja chave Gemini configurada
    return {
        "resumo_executivo": f"Contratação conduzida por {orgao} ({uf}) referente a {objeto}.",
        "segmento": "Geral / Serviços & Suprimentos",
        "complexidade": "Média" if valor > 100000 else "Baixa",
        "itens_provaveis": [
            {
                "item": "Lote Principal - Fornecimento / Prestação do Objeto",
                "quantidade_estimada": "Conforme termo de referência",
                "unidade": "Global/Unid",
                "observacao": "Verificar especificações técnicas completas no edital"
            }
        ],
        "requisitos_habilitacao": [
            "Atestado de Capacidade Técnica compatível com o objeto",
            "Certidão Negativa de Débitos Federais, Trabalhistas e FGTS",
            "Balanço Patrimonial e Comprovação de Boa Situação Financeira",
            "Declaração de cumprimento do Art. 7º, XXXIII da CF"
        ],
        "pontos_atencao_riscos": [
            "Atenção ao prazo estipulado para esclarecimentos e impugnações",
            "Verificar exigência de vistoria técnica facultativa ou obrigatória",
            "Garantia de proposta ou execução contratual, se aplicável"
        ],
        "estrategia_precificacao": f"Valor teto estimado de R$ {valor:,.2f}. Recomenda-se margem de BDI entre 18% e 25% dependendo da incidência de insumos."
    }

def gerar_parecer_tecnico_ia(dados_edital: dict) -> dict:
    try:
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {"erro": "Chave de API do Gemini não configurada no ambiente."}

        client = genai.Client(api_key=api_key)

        orgao = dados_edital.get("orgao_nome") or dados_edital.get("orgao") or "Órgão Público"
        uf = dados_edital.get("uf") or "BR"
        numero = dados_edital.get("numero_edital") or dados_edital.get("numero") or "-"
        valor = float(dados_edital.get("valor_estimado") or dados_edital.get("valor") or 0.0)
        objeto = dados_edital.get("objeto") or dados_edital.get("descricao") or "-"

        prompt = f"""
Você é um especialista sênior em licitações públicas brasileiras (Lei 14.133/21).
Analise as informações do seguinte edital e gere um parecer técnico estruturado exclusivamente em formato JSON válido:

Órgão: {orgao} ({uf})
Processo/Edital: {numero}
Valor Estimado: R$ {valor:,.2f}
Objeto: {objeto}

Responda APENAS com um objeto JSON válido no seguinte formato:
{{
    "resumo_executivo": "resumo conciso do objeto e escopo",
    "segmento": "ex: Medicamentos Hospitalares, Saúde, Serviços",
    "complexidade": "Baixa" | "Média" | "Alta",
    "itens_provaveis": [
        {{"item": "nome do item ou grupo", "quantidade_estimada": "quantidade", "unidade": "UN", "observacao": "..."}}
    ],
    "requisitos_habilitacao": [
        "documentos regulatórios Anvisa/CMED esperados",
        "qualificação técnica e certidões"
    ],
    "pontos_atencao_riscos": [
        "prazos de entrega",
        "risco de dotação ou impugnação"
    ],
    "recomendacao_final": "Participar" | "Analisar com Cautela" | "Não Participar",
    "justificativa_estrategica": "parecer conclusivo sobre a viabilidade comercial"
}}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        texto_resp = response.text.strip()
        # Limpar blocos de markdown se houver
        if texto_resp.startswith("```json"):
            texto_resp = texto_resp[7:]
        if texto_resp.startswith("```"):
            texto_resp = texto_resp[3:]
        if texto_resp.endswith("```"):
            texto_resp = texto_resp[:-3]

        return json.loads(texto_resp.strip())

    except Exception as e:
        print(f"Erro ao gerar parecer técnico: {e}")
        return {"erro": f"Falha ao gerar o parecer técnico de IA: {str(e)}"}
