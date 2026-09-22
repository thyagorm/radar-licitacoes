import subprocess
import re

# 1. Recupera o dashboard.html da versão anterior
html_antigo = subprocess.check_output(["git", "show", "b91bc55:static/dashboard.html"], text=True)

with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html_atual = f.read()

# 2. Restaurar o item no menu lateral (se ainda não existir)
if 'data-tab="analyzer"' not in html_atual:
    alvo_menu = '<div class="sidebar-item" data-tab="mesa">'
    novo_menu = """<div class="sidebar-item" data-tab="analyzer">
                <span>📊 Mapa de Preços (Excel)</span>
            </div>
            """ + alvo_menu
    html_atual = html_atual.replace(alvo_menu, novo_menu)
    print("✅ Item 'Mapa de Preços (Excel)' adicionado ao menu lateral!")

# 3. Extrair a tela (pane-analyzer) do histórico
pos_inicio_pane = html_antigo.find('id="pane-analyzer"')
if pos_inicio_pane != -1:
    # Achar onde a div começa
    div_start = html_antigo.rfind('<div', 0, pos_inicio_pane)
    
    # Encontra o próximo pane para saber onde termina
    proximo_pane = html_antigo.find('id="pane-', pos_inicio_pane + 20)
    if proximo_pane != -1:
        div_end = html_antigo.rfind('</div>', 0, html_antigo.rfind('<div', 0, proximo_pane))
        pane_analyzer_html = html_antigo[div_start:div_end]
    else:
        pane_analyzer_html = ""

    # Insere o pane-analyzer antes do pane-mesa ou outro pane existente
    if 'id="pane-analyzer"' not in html_atual and pane_analyzer_html:
        pos_pane_mesa = html_atual.find('id="pane-mesa"')
        if pos_pane_mesa != -1:
            div_mesa_start = html_atual.rfind('<div', 0, pos_pane_mesa)
            html_atual = html_atual[:div_mesa_start] + pane_analyzer_html + "\n\n" + html_atual[div_mesa_start:]
            print("✅ Tela pane-analyzer restaurada no corpo do HTML!")

# 4. Extrair e restaurar as funções JavaScript do analisador (processar-edital, upload, etc)
funcoes_necessarias = ["processar-edital", "downloadBase64", "analisarEdital"]
for fn in funcoes_necessarias:
    pos_fn = html_antigo.find(fn)
    if pos_fn != -1 and fn not in html_atual:
        # Pega o bloco script ou função ao redor
        bloco_start = html_antigo.rfind("<script", 0, pos_fn)
        bloco_end = html_antigo.find("</script>", pos_fn)
        if bloco_start != -1 and bloco_end != -1:
            trecho_js = html_antigo[bloco_start:bloco_end+9]
            pos_final_body = html_atual.rfind("</body>")
            html_atual = html_atual[:pos_final_body] + "\n" + trecho_js + "\n" + html_atual[pos_final_body:]
            print(f"✅ Scripts de '{fn}' restaurados!")
            break

# 5. Garantir que a troca de abas conheça o analyzer
if 'if (nome === "analyzer")' not in html_atual:
    html_atual = html_atual.replace(
        'if (nome === "mesa")',
        'if (nome === "analyzer") { /* inicializacao analyzer se necessario */ }\n            if (nome === "mesa")'
    )

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_atual)

print("🚀 dashboard.html totalmente atualizado com o Mapa de Preços!")
