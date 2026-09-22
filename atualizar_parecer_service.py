import re

with open("services/edital_analyzer_service.py", "r", encoding="utf-8") as f:
    codigo = f.read()

# Substitui as importações antigas do google.generativeai pelo novo google.genai
novo_trecho = """import os
import json
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
"""

# Se tiver import google.generativeai, substitui
codigo = re.sub(r"import google\.generativeai as genai\b", "from google import genai", codigo)

# Atualiza a função que gera o parecer para usar client = genai.Client e model="gemini-2.5-flash"
funcao_parecer = """
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

        prompt = f\"\"\"
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
\"\"\"

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
"""

# Localizar onde a função de parecer começa e substituir
pos_inicio = codigo.find("def gerar_parecer")
if pos_inicio != -1:
    pos_proxima_func = codigo.find("\ndef ", pos_inicio + 20)
    if pos_proxima_func != -1:
        codigo = codigo[:pos_inicio] + funcao_parecer.strip() + "\n\n" + codigo[pos_proxima_func:]
    else:
        codigo = codigo[:pos_inicio] + funcao_parecer.strip() + "\n"
else:
    codigo += "\n" + funcao_parecer.strip() + "\n"

# Garantir imports corretos no topo
if "from google import genai" not in codigo:
    codigo = "from google import genai\nfrom google.genai import types\n" + codigo

with open("services/edital_analyzer_service.py", "w", encoding="utf-8") as f:
    f.write(codigo)

print("✅ services/edital_analyzer_service.py atualizado com o SDK google.genai e gemini-2.5-flash!")
