import re

with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# Substitui a montagem dos parâmetros para usar os nomes exatos do backend
antigo_params = """                const params = new URLSearchParams();
                if (uf) params.append("uf", uf);
                if (termo) params.append("termo", termo);
                if (termo) params.append("q", termo);
                params.append("limit", "100");"""

novo_params = """                const params = new URLSearchParams();
                if (termo) params.append("busca", termo);
                if (uf) params.append("uf", uf);
                if (valMin > 0) params.append("valor_min", valMin);
                if (valMax > 0) params.append("valor_max", valMax);"""

if antigo_params in html:
    html = html.replace(antigo_params, novo_params)
    print("Substituição exata de parâmetros realizada!")
else:
    html = re.sub(
        r'const params = new URLSearchParams\(\);[\s\S]*?params\.append\("limit", "100"\);',
        novo_params.strip(),
        html
    )
    print("Substituição via regex realizada!")

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("static/dashboard.html atualizado para enviar busca, valor_min e valor_max!")
