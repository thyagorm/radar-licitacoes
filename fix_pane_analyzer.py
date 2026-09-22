with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

bloco_analyzer_completo = """
        <!-- ================= ABA ANALISADOR / MAPA DE PREÇOS ================= -->
        <div class="tab-pane" id="pane-analyzer" style="padding: 20px;">
            <div class="page-header" style="margin-bottom: 24px;">
                <h1 style="font-size: 22px; font-weight: 700; margin: 0 0 6px 0;">📊 Analisador de Editais & Mapa de Preços</h1>
                <p style="color: var(--text-muted); font-size: 13px; margin: 0;">Envie o edital em PDF para extrair automaticamente a tabela de itens, cruzar com o portfólio e gerar o Mapa de Preços em Excel.</p>
            </div>

            <div style="display: grid; grid-template-columns: 360px 1fr; gap: 24px; align-items: start;">
                <!-- Coluna Lateral: Formulário de Upload -->
                <div style="background: var(--card-bg, #ffffff); border: 1px solid var(--border-color, #e5e7eb); border-radius: 12px; padding: 20px;">
                    <h3 style="font-size: 15px; font-weight: 700; margin: 0 0 16px 0;">📤 Enviar Edital (PDF)</h3>
                    
                    <div style="margin-bottom: 14px;">
                        <label style="display: block; font-size: 12px; font-weight: 600; margin-bottom: 6px;">Arquivo PDF do Edital</label>
                        <input type="file" id="arquivoEditalInput" accept="application/pdf" style="width: 100%; font-size: 12px; padding: 8px; border: 1px dashed var(--border-color); border-radius: 6px; background: rgba(0,0,0,0.02);" />
                    </div>

                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px;">
                        <div>
                            <label style="display: block; font-size: 11px; font-weight: 600; margin-bottom: 4px;">Pág. Inicial (Tabela)</label>
                            <input type="number" id="pagInicialInput" placeholder="Ex: 15" style="width: 100%; padding: 6px; font-size: 12px; border: 1px solid var(--border-color); border-radius: 6px;" />
                        </div>
                        <div>
                            <label style="display: block; font-size: 11px; font-weight: 600; margin-bottom: 4px;">Pág. Final (Tabela)</label>
                            <input type="number" id="pagFinalInput" placeholder="Ex: 22" style="width: 100%; padding: 6px; font-size: 12px; border: 1px solid var(--border-color); border-radius: 6px;" />
                        </div>
                    </div>

                    <div style="margin-bottom: 16px;">
                        <label style="display: flex; align-items: center; gap: 8px; font-size: 12px; cursor: pointer;">
                            <input type="checkbox" id="chkCruzarPortfolio" checked />
                            <span>Cruzar com Portfólio / CMED</span>
                        </label>
                    </div>

                    <button type="button" id="btnProcessarEdital" onclick="iniciarProcessamentoEdital()" style="width: 100%; padding: 10px; background: #3b82f6; color: #fff; border: none; border-radius: 8px; font-weight: 700; font-size: 13px; cursor: pointer;">
                        ⚡ Extrair Itens & Gerar Mapa
                    </button>

                    <div id="statusProcessamento" style="display: none; margin-top: 14px; padding: 10px; border-radius: 6px; font-size: 12px; text-align: center;"></div>
                </div>

                <!-- Coluna Principal: Prévia da Tabela de Itens e Download -->
                <div style="background: var(--card-bg, #ffffff); border: 1px solid var(--border-color, #e5e7eb); border-radius: 12px; padding: 20px; min-height: 400px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color, #e5e7eb); padding-bottom: 14px; margin-bottom: 16px;">
                        <div>
                            <h3 style="font-size: 15px; font-weight: 700; margin: 0;" id="tituloPreviaTabela">Itens Extraídos do Edital</h3>
                            <span style="font-size: 12px; color: var(--text-muted);" id="subtituloPreviaTabela">Aguardando envio do arquivo PDF...</span>
                        </div>
                        <div id="acoesPosExtracao" style="display: none; gap: 8px;">
                            <button id="btnDownloadExcel" onclick="baixarExcelGerado()" style="padding: 6px 14px; background: #10b981; color: #fff; border: none; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer;">
                                📥 Baixar Excel
                            </button>
                            <button id="btnEnviarParaMesa" onclick="enviarExtracaoParaMesa()" style="padding: 6px 14px; background: #6366f1; color: #fff; border: none; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer;">
                                💼 Enviar para Mesa
                            </button>
                        </div>
                    </div>

                    <div id="conteudoTabelaItensExtracao" style="overflow-x: auto;">
                        <p style="text-align: center; padding: 60px 20px; color: var(--text-muted);">
                            Selecione o arquivo PDF na barra lateral e clique em "Extrair Itens & Gerar Mapa".<br>
                            A tabela extraída será visualizada aqui e o ficheiro Excel ficará disponível para transferência imediata.
                        </p>
                    </div>
                </div>
            </div>
        </div>
"""

# Se já existe id="pane-analyzer", substitui; se não, injeta antes do pane-mesa
pos_an = html.find('id="pane-analyzer"')
if pos_an != -1:
    inicio_pane = html.rfind('<div', 0, pos_an)
    fim_pane = html.find('<!--', pos_an)
    if fim_pane == -1:
        fim_pane = html.find('<div id="pane-', pos_an + 20)
    
    # Fecha a div anterior
    html = html[:inicio_pane] + bloco_analyzer_completo + "\n" + html[fim_pane:]
    print("✅ pane-analyzer existente atualizado com a interface completa!")
else:
    pos_mesa = html.find('id="pane-mesa"')
    if pos_mesa != -1:
        inicio_mesa = html.rfind('<div', 0, pos_mesa)
        html = html[:inicio_mesa] + bloco_analyzer_completo + "\n" + html[inicio_mesa:]
        print("✅ pane-analyzer injetado antes de pane-mesa!")

# Injetar os scripts de execução do processamento de edital
scripts_analyzer = """
<script>
let dadosUltimoExcelBase64 = null;
let nomeUltimoArquivo = "mapa_precos.xlsx";
let itensUltimaExtracao = [];

async function iniciarProcessamentoEdital() {
    const fileInput = document.getElementById("arquivoEditalInput");
    const pagIni = document.getElementById("pagInicialInput").value;
    const pagFim = document.getElementById("pagFinalInput").value;
    const statusDiv = document.getElementById("statusProcessamento");
    const btn = document.getElementById("btnProcessarEdital");

    if (!fileInput.files || fileInput.files.length === 0) {
        alert("Por favor, selecione um arquivo PDF de edital.");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    if (pagIni) formData.append("pagina_inicio", pagIni);
    if (pagFim) formData.append("pagina_fim", pagFim);

    statusDiv.style.display = "block";
    statusDiv.style.background = "rgba(59, 130, 246, 0.1)";
    statusDiv.style.color = "#3b82f6";
    statusDiv.innerHTML = "⏳ Processando edital com IA e gerando planilha... Aguarde.";
    btn.disabled = true;

    try {
        const res = await fetch("/api/analyzer/processar-edital", {
            method: "POST",
            body: formData
        });

        if (!res.ok) {
            const errJson = await res.json().catch(() => ({}));
            throw new Error(errJson.detail || "Erro no processamento do edital.");
        }

        const data = await res.json();
        dadosUltimoExcelBase64 = data.excel_base64;
        nomeUltimoArquivo = data.nome_arquivo || "mapa_precos.xlsx";
        itensUltimaExtracao = data.itens || [];

        statusDiv.style.background = "rgba(16, 185, 129, 0.1)";
        statusDiv.style.color = "#10b981";
        statusDiv.innerHTML = `✅ Concluído! ${itensUltimaExtracao.length} itens extraídos com sucesso.`;

        // Renderiza a prévia
        document.getElementById("acoesPosExtracao").style.display = "flex";
        document.getElementById("subtituloPreviaTabela").innerText = `${itensUltimaExtracao.length} itens encontrados`;

        let tabelaHtml = `
            <table class="table-modern" style="width:100%; font-size:12px;">
                <thead>
                    <tr>
                        <th style="width:50px;">Item</th>
                        <th>Descrição</th>
                        <th style="width:80px;">Qtd</th>
                        <th style="width:60px;">Und</th>
                        <th style="width:100px;">Ref. Unit.</th>
                        <th style="width:110px;">Total Ref.</th>
                    </tr>
                </thead>
                <tbody>
        `;

        itensUltimaExtracao.forEach((it, idx) => {
            const qtd = it.quantidade || 0;
            const ref = it.valor_referencia || it.valor_estimado || 0;
            tabelaHtml += `
                <tr>
                    <td><strong>#${it.item || (idx + 1)}</strong></td>
                    <td>${it.descricao || it.especificacao || "-"}</td>
                    <td>${qtd.toLocaleString("pt-BR")}</td>
                    <td>${it.unidade || "UN"}</td>
                    <td>R$ ${ref.toLocaleString("pt-BR", {minimumFractionDigits: 2})}</td>
                    <td>R$ ${(qtd * ref).toLocaleString("pt-BR", {minimumFractionDigits: 2})}</td>
                </tr>
            `;
        });
        tabelaHtml += `</tbody></table>`;
        document.getElementById("conteudoTabelaItensExtracao").innerHTML = tabelaHtml;

    } catch(err) {
        statusDiv.style.background = "rgba(239, 68, 68, 0.1)";
        statusDiv.style.color = "#ef4444";
        statusDiv.innerHTML = "❌ " + err.message;
    } finally {
        btn.disabled = false;
    }
}

function baixarExcelGerado() {
    if (!dadosUltimoExcelBase64) {
        alert("Nenhum arquivo Excel gerado ainda.");
        return;
    }
    const byteCharacters = atob(dadosUltimoExcelBase64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], {type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"});
    const link = document.createElement("a");
    link.href = window.URL.createObjectURL(blob);
    link.download = nomeUltimoArquivo;
    link.click();
}

async function enviarExtracaoParaMesa() {
    if (!itensUltimaExtracao || itensUltimaExtracao.length === 0) {
        alert("Não há itens extraídos para enviar.");
        return;
    }
    const numEdital = prompt("Informe o número do Edital (ou processo interno) para vincular estes itens:", "");
    if (!numEdital) return;

    try {
        const res = await fetch("/api/mesa/importar-extracao", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                numero_edital: numEdital,
                itens: itensUltimaExtracao
            })
        });
        const d = await res.json();
        alert(d.mensagem || "Itens importados para a Mesa com sucesso!");
    } catch(e) {
        alert("Erro ao enviar itens para a Mesa.");
    }
}
</script>
"""

if "function iniciarProcessamentoEdital" not in html:
    pos_corpo = html.rfind("</body>")
    html = html[:pos_corpo] + "\n" + scripts_analyzer + "\n" + html[pos_corpo:]
    print("✅ Scripts JS de processamento e download do Excel injetados!")

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
