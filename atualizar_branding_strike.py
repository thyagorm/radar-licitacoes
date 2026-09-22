with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Substituir referências no Header / Navbar lateral
html = html.replace("Radar de Licitações", "STRIKE")
html = html.replace("<title>Radar de Licitações</title>", "<title>STRIKE | Inteligência em Licitações</title>")
html = html.replace("<title>Painel de Licitações</title>", "<title>STRIKE | Inteligência em Licitações</title>")

# 2. Ajustar o logo/título no topo se houver ícone de radar
html = html.replace("🎯 Radar de Licitações", "⚡ STRIKE")

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("🚀 Identidade atualizada com sucesso para STRIKE!")
