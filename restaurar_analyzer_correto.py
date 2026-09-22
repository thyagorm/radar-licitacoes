import subprocess

# 1. Recuperar o dashboard.html da versão original com os filtros de laboratório (c461711)
antigo = subprocess.check_output(["git", "show", "c461711:static/dashboard.html"], text=True)

# 2. Localizar o bloco exato do pane-analyzer no commit antigo
pos_ini = antigo.find('<div id="pane-analyzer"')
if pos_ini == -1:
    pos_ini = antigo.find('id="pane-analyzer"')
    pos_ini = antigo.rfind("<div", 0, pos_ini)

# O bloco termina antes do pane seguinte (ex: pane-matches, pane-alertas, etc.)
pos_prox = antigo.find('<div id="pane-', pos_ini + 30)
if pos_prox == -1:
    pos_prox = antigo.find('id="pane-', pos_ini + 30)
    pos_prox = antigo.rfind("<div", 0, pos_prox)

# Encontra o último fechamento de div antes do próximo pane
pos_fim = antigo.rfind("</div>", pos_ini, pos_prox) + 6
pane_analyzer_original = antigo[pos_ini:pos_fim].strip()

# 3. Localizar os scripts JS do Analisador e dos Laboratórios no commit antigo
pos_js_ini = antigo.find("const LABS_PADRAO =")
pos_sc_ini = antigo.rfind("<script", 0, pos_js_ini)
pos_sc_fim = antigo.find("</script>", pos_js_ini) + 9
js_analyzer_original = antigo[pos_sc_ini:pos_sc_fim].strip()

# 4. Atualizar o dashboard.html atual
with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html_atual = f.read()

# Remover a mensagem de erro que ficou cravada no HTML
alvo_erro = """        <!-- ================= ABA ANALISADOR / MAPA DE PREÇOS ================= -->
        <div style="text-align: center; color: #c53030; padding: 30px;">Falha ao gerar o parecer técnico de IA.</div>"""

if alvo_erro in html_atual:
    html_atual = html_atual.replace(alvo_erro, pane_analyzer_original)
    print("✅ Bloco de erro substituído pelo pane-analyzer original!")
else:
    # Se a quebra de linha for ligeiramente diferente, busca por 'Falha ao gerar o parecer'
    pos_falha = html_atual.find("Falha ao gerar o parecer técnico de IA.")
    if pos_falha != -1:
        ini_del = html_atual.rfind("<div", 0, pos_falha)
        fim_del = html_atual.find("</div>", pos_falha) + 6
        html_atual = html_atual[:ini_del] + pane_analyzer_original + html_atual[fim_del:]
        print("✅ Falha removida e pane-analyzer injetado!")

# 5. Garantir que os scripts de laboratório estejam presentes
if "const LABS_PADRAO =" not in html_atual:
    pos_body = html_atual.rfind("</body>")
    html_atual = html_atual[:pos_body] + "\n" + js_analyzer_original + "\n" + html_atual[pos_body:]
    print("✅ Scripts de laboratórios e tags injetados no final da página!")
else:
    # Se já existir um script quebrado, atualiza com o original
    pos_labs = html_atual.find("const LABS_PADRAO =")
    sc1 = html_atual.rfind("<script", 0, pos_labs)
    sc2 = html_atual.find("</script>", pos_labs) + 9
    html_atual = html_atual[:sc1] + js_analyzer_original + html_atual[sc2:]
    print("✅ Scripts de laboratórios atualizados com a versão íntegra!")

# 6. Adicionar a chamada de renderizarTagsPadrao() ao abrir a aba se necessário
if 'if (nome === "analyzer")' in html_atual:
    if 'renderizarTagsPadrao' not in html_atual[html_atual.find('if (nome === "analyzer"'):]:
        html_atual = html_atual.replace(
            'if (nome === "analyzer") {',
            'if (nome === "analyzer") {\n                if (typeof renderizarTagsPadrao === "function") renderizarTagsPadrao();'
        )

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_atual)

print("🚀 dashboard.html corrigido e reestruturado com sucesso!")
