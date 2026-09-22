import subprocess
import re

# 1. Recuperar o dashboard.html integral do commit c461711
conteudo_antigo = subprocess.check_output(["git", "show", "c461711:static/dashboard.html"], text=True)

# 2. Extrair os estilos CSS do analyzer do commit antigo
pos_css_inicio = conteudo_antigo.find("/* Analisador Grid */")
if pos_css_inicio == -1:
    pos_css_inicio = conteudo_antigo.find(".analyzer-grid")

pos_css_fim = conteudo_antigo.find("</style>", pos_css_inicio)
css_analyzer = conteudo_antigo[pos_css_inicio:pos_css_fim]

# 3. Extrair a DIV completa do pane-analyzer
pos_pane_inicio = conteudo_antigo.find('<div id="pane-analyzer"')
if pos_pane_inicio == -1:
    pos_pane_inicio = conteudo_antigo.find("pane-analyzer")
    pos_pane_inicio = conteudo_antigo.rfind("<div", 0, pos_pane_inicio)

# Achar onde o painel fecha (logo antes do proximo pane ou comentário)
pos_proximo_pane = conteudo_antigo.find('id="pane-', pos_pane_inicio + 30)
pos_pane_fim = conteudo_antigo.rfind("</div>", pos_pane_inicio, pos_proximo_pane)
# pegar a tag de fechamento certa do painel
pos_pane_fim = conteudo_antigo.find("</div>", pos_pane_fim) + 6

pane_analyzer_original = conteudo_antigo[pos_pane_inicio:pos_pane_fim]

# 4. Extrair todos os scripts JavaScript do Analisador (LABS_PADRAO, funcoes de tags, processamento)
pos_js_inicio = conteudo_antigo.find("const LABS_PADRAO =")
pos_script_tag = conteudo_antigo.rfind("<script", 0, pos_js_inicio)
pos_script_fim = conteudo_antigo.find("</script>", pos_js_inicio) + 9
js_analyzer_original = conteudo_antigo[pos_script_tag:pos_script_fim]

# 5. Ler o dashboard.html atual
with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html_atual = f.read()

# Inserir o CSS específico no head se ainda não estiver
if ".analyzer-grid" not in html_atual:
    pos_head_style = html_atual.find("</style>")
    if pos_head_style != -1:
        html_atual = html_atual[:pos_head_style] + "\n" + css_analyzer + "\n" + html_atual[pos_head_style:]
        print("✅ CSS do Analisador e tags de laboratório inserido no <style>!")

# Substituir o pane-analyzer atual pelo pane original idêntico
pos_pane_atual = html_atual.find('id="pane-analyzer"')
if pos_pane_atual != -1:
    inicio_atual = html_atual.rfind("<div", 0, pos_pane_atual)
    # acha onde termina o pane atual
    pos_prox = html_atual.find('id="pane-mesa"', inicio_atual)
    if pos_prox != -1:
        fim_atual = html_atual.rfind("<div", inicio_atual, pos_prox)
    else:
        fim_atual = html_atual.find("</div>\n        </div>", inicio_atual) + 14
    
    html_atual = html_atual[:inicio_atual] + pane_analyzer_original + "\n\n        " + html_atual[fim_atual:]
    print("✅ Interface pane-analyzer substituída pela versão original com laboratórios!")

# Substituir ou injetar o bloco JS original
pos_js_atual = html_atual.find("iniciarProcessamentoEdital")
if pos_js_atual != -1:
    # Remove a versão simplificada anterior
    sc_ini = html_atual.rfind("<script>", 0, pos_js_atual)
    sc_fim = html_atual.find("</script>", pos_js_atual) + 9
    html_atual = html_atual[:sc_ini] + js_analyzer_original + html_atual[sc_fim:]
    print("✅ Scripts do Analisador restaurados para a versão completa original!")
else:
    pos_body = html_atual.rfind("</body>")
    html_atual = html_atual[:pos_body] + "\n" + js_analyzer_original + "\n" + html_atual[pos_body:]
    print("✅ Scripts originais injetados antes do </body>!")

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_atual)

print("🚀 Restauração 100% concluída!")
