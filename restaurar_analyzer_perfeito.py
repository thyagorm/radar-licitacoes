import subprocess

# 1. Obter o HTML original do commit c461711
antigo = subprocess.check_output(["git", "show", "c461711:static/dashboard.html"], text=True)

# 2. Localizar o bloco exato do pane-analyzer no commit antigo
marca_inicio = '<div class="tab-pane" id="pane-analyzer">'
if marca_inicio not in antigo:
    marca_inicio = 'id="pane-analyzer"'
    pos_ini = antigo.find(marca_inicio)
    pos_ini = antigo.rfind('<div', 0, pos_ini)
else:
    pos_ini = antigo.find(marca_inicio)

# Achar onde fecha o pane-analyzer antigo (antes do pane-matches ou proximo pane)
pos_fim = antigo.find('<div class="tab-pane" id="pane-', pos_ini + 30)
if pos_fim == -1:
    pos_fim = antigo.find('id="pane-', pos_ini + 30)
    pos_fim = antigo.rfind('<div', 0, pos_fim)

bloco_original = antigo[pos_ini:pos_fim].strip()

# 3. Localizar os scripts JS do analyzer no commit antigo
js_ini = antigo.find("const LABS_PADRAO =")
js_start = antigo.rfind("<script", 0, js_ini)
js_end = antigo.find("</script>", js_ini) + 9
bloco_js_original = antigo[js_start:js_end].strip()

# 4. Atualizar o static/dashboard.html atual
with open("static/dashboard.html", "r", encoding="utf-8") as f:
    atual = f.read()

# Substitui o pane-analyzer atual pelo bloco original
pos_atual_ini = atual.find('id="pane-analyzer"')
if pos_atual_ini != -1:
    p1 = atual.rfind('<div', 0, pos_atual_ini)
    # procura o próximo pane
    p2 = atual.find('id="pane-', pos_atual_ini + 20)
    if p2 != -1:
        p2 = atual.rfind('<div', 0, p2)
        atual = atual[:p1] + bloco_original + "\n\n        " + atual[p2:]
        print("✅ Pane HTML do Analisador restaurado perfeitamente!")

# Garantir que ao clicar na aba o JS inicialize os laboratórios
if "carregarLaboratoriosPadrao()" not in atual:
    atual = atual.replace(
        'if (nome === "analyzer") {',
        'if (nome === "analyzer") {\n                if (typeof renderizarTagsPadrao === "function") renderizarTagsPadrao();\n                if (typeof atualizarStatusPortfolio === "function") atualizarStatusPortfolio();'
    )

# Garantir que os scripts do analisador (LABS_PADRAO, etc.) estejam presentes
if "const LABS_PADRAO =" not in atual:
    pos_body = atual.rfind("</body>")
    atual = atual[:pos_body] + "\n" + bloco_js_original + "\n" + atual[pos_body:]
    print("✅ Scripts originais de laboratório e processamento injetados!")

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(atual)

print("🚀 Concluído com sucesso!")
