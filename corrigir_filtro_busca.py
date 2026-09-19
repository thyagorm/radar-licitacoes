import re

with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# Função para normalizar strings (remover acentos e minúsculas no JS)
js_normalizacao = """
        function normalizarTexto(txt) {
            if (!txt) return "";
            return txt.toString().toLowerCase()
                .normalize("NFD").replace(/[\\u0300-\\u036f]/g, "")
                .trim();
        }
"""

if "function normalizarTexto" not in html:
    html = html.replace("</script>", js_normalizacao + "\n    </script>")

# Substitui o trecho de filtragem da lista dentro de carregarLicitacoesPncp
antigo_filtro = """                // Filtros client-side complementares
                if (valMin > 0) {
                    lista = lista.filter(l => (l.valor_estimado || l.valor_total || l.valor || 0) >= valMin);
                }
                if (valMax > 0) {
                    lista = lista.filter(l => (l.valor_estimado || l.valor_total || l.valor || 0) <= valMax);
                }
                if (modalidade) {
                    lista = lista.filter(l => {
                        const modStr = (l.modalidade || l.modalidade_nome || "").toUpperCase();
                        return modStr.includes(modalidade);
                    });
                }"""

novo_filtro = """                // 1. Filtro rigoroso de texto (Objeto, Descrição e Órgão)
                if (termo) {
                    const termoNorm = normalizarTexto(termo);
                    const palavras = termoNorm.split(/\\s+/).filter(p => p.length > 1);
                    
                    lista = lista.filter(l => {
                        const textoAlvo = normalizarTexto(
                            (l.objeto || "") + " " + 
                            (l.descricao || "") + " " + 
                            (l.orgao_nome || l.orgao || "") + " " +
                            (l.numero_edital || l.numero || "")
                        );
                        // Deve conter todas as palavras digitadas na busca
                        return palavras.every(palavra => textoAlvo.includes(palavra));
                    });
                }

                // 2. Filtro por UF
                if (uf) {
                    const ufNorm = uf.toUpperCase().trim();
                    lista = lista.filter(l => (l.uf || l.sigla_uf || "").toUpperCase().trim() === ufNorm);
                }

                // 3. Filtros client-side complementares de valores e modalidade
                if (valMin > 0) {
                    lista = lista.filter(l => (l.valor_estimado || l.valor_total || l.valor || 0) >= valMin);
                }
                if (valMax > 0) {
                    lista = lista.filter(l => (l.valor_estimado || l.valor_total || l.valor || 0) <= valMax);
                }
                if (modalidade) {
                    lista = lista.filter(l => {
                        const modStr = (l.modalidade || l.modalidade_nome || "").toUpperCase();
                        return modStr.includes(modalidade);
                    });
                }"""

if antigo_filtro in html:
    html = html.replace(antigo_filtro, novo_filtro)
else:
    # Se já tiver alguma variação, substitui o bloco do carregarLicitacoesPncp
    print("Ajustando via regex...")
    html = re.sub(
        r'// Filtros client-side complementares[\s\S]*?(?=// Ordenação dinâmica)',
        novo_filtro + "\n\n                ",
        html
    )

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Filtro de busca textual corrigido com normalização de acentos!")
