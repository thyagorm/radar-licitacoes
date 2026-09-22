with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# Vamos ler o conteúdo limpo que criamos para o alerts.html e injetar diretamente no dashboard.html
with open("static/alerts.html", "r", encoding="utf-8") as f_alt:
    conteudo_alertas_full = f_alt.read()

# Extrair apenas o miolo dentro da div pane-alertas
import re
match = re.search(r'<div id="pane-alertas"[^>]*>([\s\S]*)</div>\s*$', conteudo_alertas_full.strip())
if not match:
    # Tenta um regex mais abrangente caso o fecho varie
    match = re.search(r'<div id="pane-alertas"[^>]*>([\s\S]*)', conteudo_alertas_full.strip())

if match:
    miolo = match.group(1)
    # Remove o último </div> correspondente ao pane-alertas se necessário
    if miolo.endswith("</div>"):
        miolo = miolo[:-6]
        
    # Substitui o miolo antigo do pane-alertas no dashboard.html
    # Localizamos o div de alertas no dashboard principal e atualizamos o seu conteúdo interior
    pattern = r'(<div id="pane-alertas" class="tab-pane"[^>]*>)([\s\S]*?)(</div>\s*<!-- PAINEL EMPRESA|\s*</div>\s*<div id="pane-empresa"|\s*</div>\s*<!-- FIM|\Z)'
    
    # Abordagem mais segura: substituir o bloco delimitado por id="pane-alertas" até o próximo painel
    print("Aplicando substituição direta...")

