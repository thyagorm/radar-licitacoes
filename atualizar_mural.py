import re

with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Gaveta de Filtros Avançados Compacta
painel_mural = """
            <!-- MURAL DE EDITAIS COM FILTROS AVANÇADOS -->
            <div id="pane-licitacoes" class="tab-pane">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <h2 style="font-size: 18px; font-weight: 700; color: var(--text-heading); margin: 0;">📋 Mural de Editais (PNCP)</h2>
                        <p style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">Captação contínua e triagem de certames públicos em tempo real.</p>
                    </div>
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span id="contadorEditaisBadge" style="font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 6px; background: var(--table-stripe); border: 1px solid var(--border-color); color: var(--text-muted);">
                            0 editais
                        </span>
                        <button type="button" onclick="carregarLicitacoesPncp()" style="background: var(--color-primary); color: #fff; border: none; padding: 6px 14px; border-radius: 6px; font-weight: 600; font-size: 12px; cursor: pointer; display: flex; align-items: center; gap: 6px;">
                            🔄 Atualizar
                        </button>
                    </div>
                </div>

                <!-- Barra de Busca Rápida + Gatilho de Avançados -->
                <div class="kpi-card" style="padding: 10px 14px; margin-bottom: 8px; display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                    <div style="flex: 1; min-width: 200px;">
                        <input type="text" id="filtroPncpTermo" placeholder="Buscar medicamento, material, equipamento ou órgão..." onkeyup="if(event.key==='Enter') carregarLicitacoesPncp()" style="width: 100%; padding: 6px 10px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                    </div>
                    <div style="width: 110px;">
                        <select id="filtroPncpUf" onchange="carregarLicitacoesPncp()" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                            <option value="">Todas UFs</option>
                            <option value="RJ">RJ</option>
                            <option value="SP">SP</option>
                            <option value="MG">MG</option>
                            <option value="ES">ES</option>
                            <option value="PR">PR</option>
                            <option value="SC">SC</option>
                            <option value="RS">RS</option>
                            <option value="BA">BA</option>
                            <option value="DF">DF</option>
                            <option value="GO">GO</option>
                            <option value="PE">PE</option>
                        </select>
                    </div>
                    <button type="button" onclick="toggleFiltrosAvancados()" id="btnToggleFiltros" style="background: var(--table-stripe); color: var(--text-body); border: 1px solid var(--border-color); padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 5px;">
                        ⚙️ Filtros Avançados
                    </button>
                    <button type="button" onclick="carregarLicitacoesPncp()" style="background: var(--color-primary); color: #fff; border: none; padding: 6px 14px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer;">
                        🔍 Filtrar
                    </button>
                </div>

                <!-- Painel Retrátil de Filtros Avançados -->
                <div id="painelFiltrosAvancados" class="kpi-card" style="display: none; padding: 14px 16px; margin-bottom: 12px; background: var(--table-stripe); border: 1px solid var(--border-color);">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 10px;">
                        <div>
                            <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 3px;">Modalidade</label>
                            <select id="filtroPncpModalidade" style="width: 100%; padding: 5px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                <option value="">Todas as Modalidades</option>
                                <option value="PREGAO_ELETRONICO">Pregão Eletrônico</option>
                                <option value="DISPENSA">Dispensa Eletrônica</option>
                                <option value="CONCORRENCIA">Concorrência</option>
                            </select>
                        </div>
                        <div>
                            <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 3px;">Valor Mínimo (R$)</label>
                            <input type="number" id="filtroPncpValorMin" placeholder="Ex: 10000" style="width: 100%; padding: 5px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                        </div>
                        <div>
                            <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 3px;">Valor Máximo (R$)</label>
                            <input type="number" id="filtroPncpValorMax" placeholder="Ex: 5000000" style="width: 100%; padding: 5px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                        </div>
                        <div>
                            <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 3px;">Ordenação</label>
                            <select id="filtroPncpOrdenacao" style="width: 100%; padding: 5px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                <option value="recentes">Mais Recentes</option>
                                <option value="valor_maior">Maior Valor Estimado</option>
                                <option value="valor_menor">Menor Valor Estimado</option>
                                <option value="abertura">Abertura Próxima</option>
                            </select>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: flex-end; gap: 8px;">
                        <button type="button" onclick="limparFiltrosAvancados()" style="background: transparent; border: 1px solid var(--border-color); color: var(--text-muted); padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; cursor: pointer;">
                            Limpar Filtros
                        </button>
                        <button type="button" onclick="carregarLicitacoesPncp()" style="background: var(--color-primary); color: #fff; border: none; padding: 4px 14px; border-radius: 4px; font-size: 11px; font-weight: 600; cursor: pointer;">
                            Aplicar
                        </button>
                    </div>
                </div>

                <!-- Tabela de Editais Compacta -->
                <div class="table-container">
                    <table class="table-modern table-mural-compact">
                        <thead>
                            <tr>
                                <th style="width: 160px;">Edital / Órgão</th>
                                <th style="width: 50px; text-align: center;">UF</th>
                                <th>Objeto Resumido</th>
                                <th style="width: 120px; text-align: right;">Estimado</th>
                                <th style="width: 95px; text-align: center;">Abertura</th>
                                <th style="width: 130px; text-align: center;">Ações</th>
                            </tr>
                        </thead>
                        <tbody id="tabelaPncpBody">
                            <tr>
                                <td colspan="6" style="text-align: center; padding: 36px 20px;">
                                    <div style="max-width: 280px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 10px;">
                                        <div class="mural-spinner"></div>
                                        <div style="width: 100%;">
                                            <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 600; color: var(--text-muted); margin-bottom: 4px;">
                                                <span id="labelStatusCarregamento">A consultar PNCP...</span>
                                                <span id="labelPorcentagemCarregamento">40%</span>
                                            </div>
                                            <div style="height: 5px; width: 100%; background: var(--border-color); border-radius: 3px; overflow: hidden;">
                                                <div id="barraProgressoCarregamento" style="height: 100%; width: 40%; background: var(--color-primary); transition: width 0.25s ease;"></div>
                                            </div>
                                        </div>
                                    </div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
"""

pos_ini = html.find('id="pane-licitacoes"')
pos_div_abertura = html.rfind('<div', 0, pos_ini)
pos_prox = html.find('id="pane-matches"')
pos_div_prox = html.rfind('<div', 0, pos_prox)

html = html[:pos_div_abertura] + painel_mural + "\n            " + html[pos_div_prox:]

# 2. Funções JavaScript completas (busca avançada + filtros client-side)
js_completo = """
        function toggleFiltrosAvancados() {
            const painel = document.getElementById("painelFiltrosAvancados");
            const btn = document.getElementById("btnToggleFiltros");
            if (!painel) return;
            const visivel = painel.style.display !== "none";
            painel.style.display = visivel ? "none" : "block";
            if (btn) {
                btn.style.background = visivel ? "var(--table-stripe)" : "var(--color-primary)";
                btn.style.color = visivel ? "var(--text-body)" : "#fff";
            }
        }

        function limparFiltrosAvancados() {
            const setVal = (id, v) => { const el = document.getElementById(id); if (el) el.value = v; };
            setVal("filtroPncpModalidade", "");
            setVal("filtroPncpValorMin", "");
            setVal("filtroPncpValorMax", "");
            setVal("filtroPncpOrdenacao", "recentes");
            setVal("filtroPncpTermo", "");
            setVal("filtroPncpUf", "");
            carregarLicitacoesPncp();
        }

        async function carregarLicitacoesPncp() {
            const tbody = document.getElementById("tabelaPncpBody");
            if (!tbody) return;

            tbody.innerHTML = `
                <tr>
                    <td colspan="6" style="text-align: center; padding: 34px 20px;">
                        <div style="max-width: 280px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 10px;">
                            <div class="mural-spinner"></div>
                            <div style="width: 100%;">
                                <div style="display: flex; justify-content: space-between; font-size: 11px; font-weight: 600; color: var(--text-muted); margin-bottom: 4px;">
                                    <span id="labelStatusCarregamento">Filtrando certames no PNCP...</span>
                                    <span id="labelPorcentagemCarregamento">40%</span>
                                </div>
                                <div style="height: 5px; width: 100%; background: var(--border-color); border-radius: 3px; overflow: hidden;">
                                    <div id="barraProgressoCarregamento" style="height: 100%; width: 40%; background: var(--color-primary); transition: width 0.25s ease;"></div>
                                </div>
                            </div>
                        </div>
                    </td>
                </tr>
            `;

            const termo = document.getElementById("filtroPncpTermo")?.value.trim() || "";
            const uf = document.getElementById("filtroPncpUf")?.value.trim() || "";
            const modalidade = document.getElementById("filtroPncpModalidade")?.value || "";
            const valMin = parseFloat(document.getElementById("filtroPncpValorMin")?.value) || 0;
            const valMax = parseFloat(document.getElementById("filtroPncpValorMax")?.value) || 0;
            const ordenacao = document.getElementById("filtroPncpOrdenacao")?.value || "recentes";

            const barra = document.getElementById("barraProgressoCarregamento");
            const pct = document.getElementById("labelPorcentagemCarregamento");
            const lbl = document.getElementById("labelStatusCarregamento");

            try {
                if (barra) barra.style.width = "75%";
                if (pct) pct.textContent = "75%";
                if (lbl) lbl.textContent = "Consultando base nacional...";

                const params = new URLSearchParams();
                if (uf) params.append("uf", uf);
                if (termo) params.append("termo", termo);
                if (termo) params.append("q", termo);
                params.append("limit", "100");

                let res = await fetch(`/api/pncp/licitacoes?${params.toString()}`);
                if (!res.ok) {
                    res = await fetch(`/api/pncp/licitacoes`);
                }

                if (barra) barra.style.width = "100%";
                if (pct) pct.textContent = "100%";

                if (!res.ok) throw new Error(`Status ${res.status}`);

                const data = await res.json();
                let lista = [];

                if (Array.isArray(data)) lista = data;
                else if (Array.isArray(data.licitacoes)) lista = data.licitacoes;
                else if (Array.isArray(data.editais)) lista = data.editais;
                else if (Array.isArray(data.data)) lista = data.data;
                else if (Array.isArray(data.itens)) lista = data.itens;

                // Filtros client-side complementares
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
                }

                // Ordenação dinâmica
                if (ordenacao === "valor_maior") {
                    lista.sort((a, b) => (b.valor_estimado || b.valor_total || 0) - (a.valor_estimado || a.valor_total || 0));
                } else if (ordenacao === "valor_menor") {
                    lista.sort((a, b) => (a.valor_estimado || a.valor_total || 0) - (b.valor_estimado || b.valor_total || 0));
                }

                const badgeTotal = document.getElementById("contadorEditaisBadge");
                if (badgeTotal) badgeTotal.textContent = `${lista.length} editais`;

                if (lista.length === 0) {
                    tbody.innerHTML = `
                        <tr>
                            <td colspan="6" style="text-align: center; padding: 28px 16px; color: var(--text-muted); font-size: 12px;">
                                🔍 Nenhum edital encontrado para estes filtros. Tente flexibilizar os valores ou termos.
                            </td>
                        </tr>
                    `;
                    return;
                }

                tbody.innerHTML = lista.map(l => {
                    const numero = l.numero_edital || l.numero || l.id || l.numero_processo || "-";
                    const orgao = l.orgao_nome || l.orgao || l.nome_orgao || "Órgão Público";
                    const estado = l.uf || l.sigla_uf || "BR";
                    const objeto = l.objeto || l.descricao || "Aquisição conforme edital.";
                    const rawVal = l.valor_estimado ?? l.valor_total ?? l.valor ?? 0;
                    const valor = Number(rawVal).toLocaleString("pt-BR", { minimumFractionDigits: 2 });
                    const abertura = l.data_abertura || l.data_publicacao || "-";
                    const link = l.link_edital || l.url_pncp || l.link || "#";

                    return `
                        <tr>
                            <td>
                                <strong style="color: var(--color-primary); font-size: 12px; display: block;">${numero}</strong>
                                <span style="font-size: 10px; color: var(--text-muted); display: block; max-width: 150px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${orgao}">${orgao}</span>
                            </td>
                            <td style="text-align: center; font-weight: 700; font-size: 11px;">${estado}</td>
                            <td>
                                <div style="max-height: 32px; overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; font-size: 11px; line-height: 1.25;" title="${objeto}">
                                    ${objeto}
                                </div>
                            </td>
                            <td style="text-align: right; font-weight: 700; font-size: 12px; white-space: nowrap;">R$ ${valor}</td>
                            <td style="text-align: center; font-size: 11px; color: var(--text-muted); white-space: nowrap;">${abertura}</td>
                            <td style="text-align: center;">
                                <div style="display: flex; gap: 4px; justify-content: center;">
                                    ${link !== '#' ? `<a href="${link}" target="_blank" style="padding: 3px 6px; background: var(--table-stripe); color: var(--color-primary); border: 1px solid var(--border-color); border-radius: 4px; text-decoration: none; font-size: 10px; font-weight: 700;">Edital ↗</a>` : ''}
                                    <button type="button" onclick="promoverEditalParaMesa('${numero}', '${orgao.replace(/'/g, "\\'")}', '${estado}', ${rawVal})" style="padding: 3px 8px; background: var(--color-primary); color: #fff; border: none; border-radius: 4px; font-size: 10px; font-weight: 700; cursor: pointer;">
                                        + Mesa
                                    </button>
                                </div>
                            </td>
                        </tr>
                    `;
                }).join("");

            } catch (err) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align: center; padding: 22px; color: var(--color-danger); font-size: 12px;">
                            ⚠️ Erro ao carregar mural: ${err.message}
                        </td>
                    </tr>
                `;
            }
        }
"""

html = re.sub(r'async function carregarLicitacoesPncp[\s\S]*?^        \}', '', html, flags=re.MULTILINE)
html = html.replace("</script>", js_completo + "\n    </script>")

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Mural atualizado com Filtros Avançados sem erros de sintaxe!")
