with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Recuperar o item do menu do Mapa de Preços caso tenha sido removido do menu lateral
item_mapa = """            <a href="#" class="nav-item" onclick="navegarPara('mapaPrecos', this)">
                <span class="nav-icon">📊</span> Mapa de Preços / CMED
            </a>"""

if "mapaPrecos" not in html and "Mesa de Operação" in html:
    # Insere logo abaixo ou acima da Mesa de Operação
    alvo = """<span class="nav-icon">💼</span> Mesa de Operação"""
    if alvo in html:
        substituir = alvo + """\n            </a>\n            <a href="#" class="nav-item" onclick="navegarPara('mapaPrecos', this)">\n                <span class="nav-icon">📊</span> Mapa de Preços"""
        # localiza a tag </a> que fecha o item da Mesa
        pos_mesa = html.find(alvo)
        pos_fecho = html.find("</a>", pos_mesa)
        if pos_fecho != -1:
            html = html[:pos_fecho+4] + """\n            <a href="#" class="nav-item" onclick="navegarPara('mapaPrecos', this)">\n                <span class="nav-icon">📊</span> Mapa de Preços\n            </a>""" + html[pos_fecho+4:]
            print("Sucesso: Link do Mapa de Preços restaurado no menu lateral!")

# 2. Atualizar a função abrirModalItensProcesso para conter o botão de adicionar item manual
funcao_antiga = """        if (!itens || itens.length === 0) {
            container.innerHTML = '<p style="text-align:center; padding:20px; color:var(--text-muted);">Nenhum item associado diretamente a este processo ainda. Você pode importá-los via Edital.</p>';
            return;
        }"""

funcao_nova = """        let html = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <span style="font-size:12px; color:var(--text-muted);">Itens cadastrados para disputa e cotação</span>
                <button type="button" onclick="adicionarLinhaItemManual()" style="padding:5px 12px; background:#10b981; color:#fff; border:none; border-radius:4px; font-size:11px; font-weight:600; cursor:pointer;">+ Adicionar Item Manual</button>
            </div>
            <table class="table-modern" style="width:100%; font-size:12px;" id="tabelaModalItens">
                <thead>
                    <tr>
                        <th style="width:40px; text-align:center;">Disputar</th>
                        <th style="width:50px;">Item</th>
                        <th>Descrição</th>
                        <th style="width:90px;">Qtd</th>
                        <th style="width:60px;">Und</th>
                        <th style="width:100px;">Ref. Unit.</th>
                        <th style="width:110px;">Proposta Unit.</th>
                    </tr>
                </thead>
                <tbody id="corpoTabelaModalItens">
        `;
        if (!itens || itens.length === 0) {
            html += `<tr id="linhaSemItens"><td colspan="7" style="text-align:center; padding:24px; color:var(--text-muted);">Nenhum item associado ainda. Clique em "+ Adicionar Item Manual" acima para inserir.</td></tr>`;
        } else {
            itens.forEach((it, idx) => {
                html += `
                    <tr data-item-id="${it.id || ''}">
                        <td style="text-align:center;">
                            <input type="checkbox" class="chk-item-participar" ${it.participar ? "checked" : ""} style="cursor:pointer;" />
                        </td>
                        <td><input type="number" class="input-item-num" value="${it.numero_item || (idx + 1)}" style="width:45px; padding:3px; font-size:11px;" /></td>
                        <td><input type="text" class="input-item-desc" value="${it.descricao || ''}" style="width:100%; padding:3px; font-size:11px;" /></td>
                        <td><input type="number" step="any" class="input-item-qtd" value="${it.quantidade || 1}" style="width:80px; padding:3px; font-size:11px;" /></td>
                        <td><input type="text" class="input-item-und" value="${it.unidade || 'UN'}" style="width:50px; padding:3px; font-size:11px;" /></td>
                        <td><input type="number" step="0.01" class="input-item-ref" value="${it.valor_referencia_unitario || 0.0}" style="width:90px; padding:3px; font-size:11px;" /></td>
                        <td><input type="number" step="0.01" class="input-item-proposta" value="${it.preco_proposta_unitario || ''}" placeholder="R$ 0,00" style="width:100px; padding:3px; font-size:11px;" /></td>
                    </tr>
                `;
            });
        }
        html += `</tbody></table>`;
        container.innerHTML = html;
        return;"""

if funcao_antiga in html:
    html = html.replace(funcao_antiga, funcao_nova)
    print("Sucesso: Tabela de Itens com opção manual injetada!")

# 3. Adicionar funções auxiliares para manipular linhas dinâmicas e salvar tudo
scripts_auxiliares = """
function adicionarLinhaItemManual() {
    const semItens = document.getElementById("linhaSemItens");
    if (semItens) semItens.remove();
    const tbody = document.getElementById("corpoTabelaModalItens");
    const totalLinhas = tbody.querySelectorAll("tr").length + 1;
    const tr = document.createElement("tr");
    tr.innerHTML = `
        <td style="text-align:center;"><input type="checkbox" class="chk-item-participar" checked style="cursor:pointer;" /></td>
        <td><input type="number" class="input-item-num" value="${totalLinhas}" style="width:45px; padding:3px; font-size:11px;" /></td>
        <td><input type="text" class="input-item-desc" placeholder="Nome do medicamento / produto" style="width:100%; padding:3px; font-size:11px;" /></td>
        <td><input type="number" step="any" class="input-item-qtd" value="1000" style="width:80px; padding:3px; font-size:11px;" /></td>
        <td><input type="text" class="input-item-und" value="FR" style="width:50px; padding:3px; font-size:11px;" /></td>
        <td><input type="number" step="0.01" class="input-item-ref" value="0.00" style="width:90px; padding:3px; font-size:11px;" /></td>
        <td><input type="number" step="0.01" class="input-item-proposta" placeholder="R$ 0,00" style="width:100px; padding:3px; font-size:11px;" /></td>
    `;
    tbody.appendChild(tr);
}

// Substitui a função salvarSelecaoItens para ler a tabela dinâmica
async function salvarSelecaoItens() {
    if (!processoModalId) return;
    const linhas = document.querySelectorAll("#corpoTabelaModalItens tr");
    const payloadItens = [];
    linhas.forEach(tr => {
        if (tr.id === "linhaSemItens") return;
        const descInput = tr.querySelector(".input-item-desc");
        if (!descInput || !descInput.value.trim()) return;

        payloadItens.push({
            id: tr.getAttribute("data-item-id") || null,
            participar: tr.querySelector(".chk-item-participar")?.checked ? 1 : 0,
            numero_item: parseInt(tr.querySelector(".input-item-num")?.value || 1),
            descricao: descInput.value.trim(),
            quantidade: parseFloat(tr.querySelector(".input-item-qtd")?.value || 0),
            unidade: tr.querySelector(".input-item-und")?.value || "UN",
            valor_referencia_unitario: parseFloat(tr.querySelector(".input-item-ref")?.value || 0),
            preco_proposta_unitario: parseFloat(tr.querySelector(".input-item-proposta")?.value || 0)
        });
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
"""

pos_fechar = html.find("function fecharModalItensProcesso")
if pos_fechar != -1:
    html = html[:pos_fechar] + scripts_auxiliares + "\n" + html[pos_fechar:]
    print("Sucesso: Scripts de inserção manual integrados!")

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
