with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

bloco_modais_e_scripts = """
<!-- ================= MODAL ITENS DO PROCESSO ================= -->
<div id="modalItensProcesso" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--card-bg, #ffffff); border-radius:12px; width:90%; max-width:850px; max-height:85vh; display:flex; flex-direction:column; padding:24px; box-shadow:0 20px 25px -5px rgba(0,0,0,0.3);">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-color, #e5e7eb); padding-bottom:12px;">
            <div>
                <h3 style="margin:0; font-size:18px;" id="modalItensTitulo">Itens do Processo</h3>
                <span style="font-size:12px; color:var(--text-muted, #6b7280);" id="modalItensSubtitulo">Selecione quais itens serão disputados</span>
            </div>
            <button onclick="fecharModalItensProcesso()" style="background:transparent; border:none; font-size:20px; cursor:pointer; color:var(--text-muted);">&times;</button>
        </div>
        <div style="overflow-y:auto; margin-top:16px; flex:1;" id="modalItensConteudo">
            <p style="text-align:center; color:var(--text-muted);">Carregando itens...</p>
        </div>
        <div style="margin-top:16px; display:flex; justify-content:flex-end; gap:8px; border-top:1px solid var(--border-color, #e5e7eb); padding-top:12px;">
            <button onclick="fecharModalItensProcesso()" style="padding:8px 16px; border-radius:6px; border:1px solid var(--border-color); background:transparent; cursor:pointer;">Fechar</button>
            <button onclick="salvarSelecaoItens()" style="padding:8px 16px; border-radius:6px; border:none; background:#3b82f6; color:#fff; font-weight:600; cursor:pointer;">Salvar Disputa</button>
        </div>
    </div>
</div>

<!-- ================= MODAL GESTÃO CONTRATUAL & AF ================= -->
<div id="modalContratoProcesso" style="display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6); z-index:9999; align-items:center; justify-content:center;">
    <div style="background:var(--card-bg, #ffffff); border-radius:12px; width:90%; max-width:900px; max-height:85vh; display:flex; flex-direction:column; padding:24px; box-shadow:0 20px 25px -5px rgba(0,0,0,0.3);">
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-color, #e5e7eb); padding-bottom:12px;">
            <div>
                <h3 style="margin:0; font-size:18px;" id="modalContratoTitulo">Gestão Contratual & Saldo</h3>
                <span style="font-size:12px; color:var(--text-muted, #6b7280);" id="modalContratoSubtitulo">Instrumento, vigência e ordens de fornecimento</span>
            </div>
            <button onclick="fecharModalContrato()" style="background:transparent; border:none; font-size:20px; cursor:pointer; color:var(--text-muted);">&times;</button>
        </div>
        <div style="overflow-y:auto; margin-top:16px; flex:1;" id="modalContratoConteudo">
            <p style="text-align:center; color:var(--text-muted);">Carregando dados contratuais...</p>
        </div>
        <div style="margin-top:16px; display:flex; justify-content:flex-end; gap:8px; border-top:1px solid var(--border-color, #e5e7eb); padding-top:12px;">
            <button onclick="fecharModalContrato()" style="padding:8px 16px; border-radius:6px; border:1px solid var(--border-color); background:transparent; cursor:pointer;">Fechar</button>
        </div>
    </div>
</div>

<script>
let processoModalId = null;
let itensEmCache = [];

async function abrirModalItensProcesso(processoId, codInterno) {
    processoModalId = processoId;
    document.getElementById("modalItensTitulo").innerText = `Itens do Processo ${codInterno ? "[" + codInterno + "]" : ""}`;
    document.getElementById("modalItensProcesso").style.display = "flex";
    const container = document.getElementById("modalItensConteudo");
    container.innerHTML = '<p style="text-align:center; padding:20px;">Carregando itens...</p>';

    try {
        const res = await fetch(`/api/mesa/processos/${processoId}/itens`);
        const itens = await res.json();
        itensEmCache = itens;
        if (!itens || itens.length === 0) {
            container.innerHTML = '<p style="text-align:center; padding:20px; color:var(--text-muted);">Nenhum item associado diretamente a este processo ainda. Você pode importá-los via Edital.</p>';
            return;
        }

        let html = `
            <table class="table-modern" style="width:100%; font-size:12px;">
                <thead>
                    <tr>
                        <th style="width:40px; text-align:center;">Disputar</th>
                        <th style="width:50px;">Item</th>
                        <th>Descrição</th>
                        <th>Qtd</th>
                        <th>Ref. Unit.</th>
                        <th>Proposta Unit.</th>
                    </tr>
                </thead>
                <tbody>
        `;
        itens.forEach((it, idx) => {
            html += `
                <tr>
                    <td style="text-align:center;">
                        <input type="checkbox" id="chk_item_${it.id}" ${it.participar ? "checked" : ""} style="cursor:pointer;" />
                    </td>
                    <td><strong>#${it.numero_item || (idx + 1)}</strong></td>
                    <td>${it.descricao}</td>
                    <td>${(it.quantidade || 0).toLocaleString("pt-BR")} ${it.unidade || "UN"}</td>
                    <td>R$ ${(it.valor_referencia_unitario || 0).toLocaleString("pt-BR", {minimumFractionDigits:2})}</td>
                    <td>
                        <input type="number" step="0.01" id="preco_item_${it.id}" value="${it.preco_proposta_unitario || ""}" placeholder="R$ 0,00" style="width:90px; padding:4px; font-size:12px; border-radius:4px; border:1px solid var(--border-color);" />
                    </td>
                </tr>
            `;
        });
        html += `</tbody></table>`;
        container.innerHTML = html;
    } catch(e) {
        container.innerHTML = '<p style="color:var(--color-danger); text-align:center;">Erro ao carregar itens do processo.</p>';
    }
}

function fecharModalItensProcesso() {
    document.getElementById("modalItensProcesso").style.display = "none";
}

async function salvarSelecaoItens() {
    if (!processoModalId || itensEmCache.length === 0) return;
    const payloadItens = itensEmCache.map(it => {
        const chk = document.getElementById(`chk_item_${it.id}`);
        const precoInput = document.getElementById(`preco_item_${it.id}`);
        return {
            ...it,
            participar: chk ? (chk.checked ? 1 : 0) : it.participar,
            preco_proposta_unitario: precoInput && precoInput.value ? parseFloat(precoInput.value) : (it.preco_proposta_unitario || 0.0)
        };
    });

    try {
        const res = await fetch(`/api/mesa/processos/${processoModalId}/itens`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({itens: payloadItens})
        });
        const resJson = await res.json();
        alert(resJson.mensagem || "Itens atualizados!");
        fecharModalItensProcesso();
    } catch(e) {
        alert("Erro ao salvar itens.");
    }
}

async function abrirModalContrato(processoId, codInterno) {
    document.getElementById("modalContratoTitulo").innerText = `Gestão do Contrato / ARP ${codInterno ? "[" + codInterno + "]" : ""}`;
    document.getElementById("modalContratoProcesso").style.display = "flex";
    const container = document.getElementById("modalContratoConteudo");
    container.innerHTML = '<p style="text-align:center; padding:20px;">Carregando resumo do contrato...</p>';

    try {
        const res = await fetch(`/api/mesa/processos/${processoId}/contrato-resumo`);
        if (res.status === 404) {
            container.innerHTML = `
                <div style="text-align:center; padding:30px;">
                    <p style="color:var(--text-muted); margin-bottom:12px;">Nenhum Contrato ou ARP foi registrado formalmente para este processo ganho.</p>
                    <button onclick="alert(\x27Formulário de homologação rápida disponível via menu de resultado!\x27)" style="padding:8px 16px; background:#10b981; color:#fff; border:none; border-radius:6px; cursor:pointer; font-weight:600;">+ Registrar Ata / Contrato</button>
                </div>
            `;
            return;
        }
        const data = await res.json();
        const c = data.contrato;
        const itens = data.itens || [];
        const afs = data.ordens_fornecimento || [];

        let html = `
            <div style="background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.3); border-radius:8px; padding:12px; margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="font-weight:bold; font-size:14px; color:#10b981;">${c.tipo_instrumento}: ${c.numero_instrumento}</span>
                    <div style="font-size:12px; color:var(--text-muted); margin-top:2px;">Vigência: ${c.data_inicio_vigencia || "-"} até ${c.data_fim_vigencia || "-"}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:11px; color:var(--text-muted);">Valor Total Homologado</div>
                    <div style="font-size:16px; font-weight:700; color:#10b981;">R$ ${(c.valor_total_homologado || 0).toLocaleString("pt-BR", {minimumFractionDigits:2})}</div>
                </div>
            </div>

            <h4 style="margin:16px 0 8px 0; font-size:13px;">Controle de Saldo por Item</h4>
            <table class="table-modern" style="width:100%; font-size:12px; margin-bottom:20px;">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Descrição</th>
                        <th>Qtd Homologada</th>
                        <th>Empenhado (AF)</th>
                        <th>Saldo Restante</th>
                    </tr>
                </thead>
                <tbody>
        `;

        itens.forEach(it => {
            html += `
                <tr>
                    <td><strong>#${it.numero_item}</strong></td>
                    <td>${it.descricao}</td>
                    <td>${it.quantidade_registrada} ${it.unidade}</td>
                    <td style="color:#3b82f6; font-weight:600;">${it.quantidade_empenhada}</td>
                    <td style="font-weight:bold; color:${it.saldo_quantidade > 0 ? "#10b981" : "var(--text-muted)"};">${it.saldo_quantidade}</td>
                </tr>
            `;
        });
        html += `</tbody></table>`;

        html += `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <h4 style="margin:0; font-size:13px;">Ordens de Fornecimento / Empenhos (${afs.length})</h4>
            </div>
        `;

        if (afs.length === 0) {
            html += `<p style="font-size:12px; color:var(--text-muted);">Nenhuma Ordem de Fornecimento lançada até o momento.</p>`;
        } else {
            html += `
                <table class="table-modern" style="width:100%; font-size:12px;">
                    <thead>
                        <tr>
                            <th>Nº AF / Empenho</th>
                            <th>Prazo Entrega</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            afs.forEach(af => {
                html += `
                    <tr>
                        <td><strong>${af.numero_af_empenho}</strong></td>
                        <td>${af.prazo_limite_entrega || "-"}</td>
                        <td><span class="badge" style="background:${af.status === "ENTREGUE_NO_PRAZO" ? "rgba(16,185,129,0.15); color:#10b981;" : "rgba(245,158,11,0.15); color:#f59e0b;"}">${af.status}</span></td>
                    </tr>
                `;
            });
            html += `</tbody></table>`;
        }

        container.innerHTML = html;
    } catch(e) {
        container.innerHTML = '<p style="color:var(--color-danger); text-align:center;">Erro ao carregar dados do contrato.</p>';
    }
}

function fecharModalContrato() {
    document.getElementById("modalContratoProcesso").style.display = "none";
}
</script>
"""

pos_body = html.rfind("</body>")
if pos_body != -1:
    html = html[:pos_body] + bloco_modais_e_scripts + "\n" + html[pos_body:]
    with open("static/dashboard.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Sucesso: Modais e scripts injetados em static/dashboard.html!")
else:
    print("Aviso: Tag </body> não encontrada.")
