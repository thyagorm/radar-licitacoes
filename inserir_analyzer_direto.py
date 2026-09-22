import subprocess

# 1. Recupera o painel do analisador do commit c461711
antigo = subprocess.check_output(["git", "show", "c461711:static/dashboard.html"], text=True)

pos_ini = antigo.find('<div class="tab-pane" id="pane-analyzer">')
if pos_ini == -1:
    pos_ini = antigo.find('id="pane-analyzer"')
    pos_ini = antigo.rfind('<div', 0, pos_ini)

pos_fim = antigo.find('<div class="tab-pane" id="pane-', pos_ini + 30)
if pos_fim == -1:
    pos_fim = antigo.find('id="pane-', pos_ini + 30)
    pos_fim = antigo.rfind('<div', 0, pos_fim)

pane_analyzer_html = antigo[pos_ini:pos_fim].strip()

# 2. Recupera os estilos CSS do analisador se não existirem
css_ini = antigo.find("/* Analisador Grid */")
css_bloco = ""
if css_ini != -1:
    css_fim = antigo.find("</style>", css_ini)
    css_bloco = antigo[css_ini:css_fim].strip()

# 3. Recupera os scripts de laboratórios e processamento
js_ini = antigo.find("const LABS_PADRAO =")
js_start = antigo.rfind("<script", 0, js_ini)
js_end = antigo.find("</script>", js_ini) + 9
js_bloco = antigo[js_start:js_end].strip()

# 4. Injeta no dashboard.html atual
with open("static/dashboard.html", "r", encoding="utf-8") as f:
    atual = f.read()

# Injeta CSS se necessário
if ".analyzer-grid" not in atual and css_bloco:
    pos_style = atual.find("</style>")
    atual = atual[:pos_style] + "\n" + css_bloco + "\n" + atual[pos_style:]
    print("✅ CSS do analisador inserido!")

# Injeta o pane exatamente antes de pane-mesa
pos_mesa = atual.find('<div id="pane-mesa"')
if pos_mesa == -1:
    pos_mesa = atual.find('id="pane-mesa"')
    pos_mesa = atual.rfind('<div', 0, pos_mesa)

atual = atual[:pos_mesa] + pane_analyzer_html + "\n\n        " + atual[pos_mesa:]
print("✅ pane-analyzer inserido com sucesso antes de pane-mesa!")

# Injeta os scripts JS antes de </body> se não existirem
if "const LABS_PADRAO =" not in atual:
    pos_body = atual.rfind("</body>")
    atual = atual[:pos_body] + "\n" + js_bloco + "\n" + atual[pos_body:]
    print("✅ Scripts de laboratórios e processamento inseridos!")

# Assegura que ao clicar na aba o painel renderiza os laboratórios
if 'if (nome === "analyzer")' in atual:
    trecho_subst = 'if (nome === "analyzer") {\n            if (typeof renderizarTagsPadrao === "function") renderizarTagsPadrao();\n            if (typeof atualizarStatusPortfolio === "function") atualizarStatusPortfolio();\n        }'
    # Atualiza a chamada da aba analyzer
    pos_chk = atual.find('if (nome === "analyzer")')
    fim_chk = atual.find("}", pos_chk) + 1
    atual = atual[:pos_chk] + trecho_subst + atual[fim_chk:]

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(atual)

print("🚀 Concluído!")
