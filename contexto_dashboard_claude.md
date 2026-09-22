]633;E;echo "# CONTEXTO DO DASHBOARD (STRIKE)";456e80a6-78ca-41fd-8b6f-733449b328d5]633;C# CONTEXTO DO DASHBOARD (STRIKE)

## Arquivo: static/dashboard.html
```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <link rel="stylesheet" href="/static/strike_tokens_2.css">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Radar de Licitações - Gestão Estratégica</title>
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

    <style>
        :root {
            --color-primary: #667eea;
            --color-primary-dark: #5a67d8;
            --color-success: #1db584;
            --color-warning: #f5a623;
            --color-danger: #e74c3c;
            --color-info: #9b59b6;

            --bg-page: #f5f5f7;
            --bg-card: #ffffff;
            --border-color: #e2e8f0;
            --text-heading: #1a1a1a;
            --text-body: #333333;
            --text-muted: #666666;
            --table-stripe: #fbfcfe;
            --table-hover: #f1f5f9;
        }

        body.dark-mode {
            --bg-page: #0f172a;
            --bg-card: #1e293b;
            --border-color: #334155;
            --text-heading: #f8fafc;
            --text-body: #cbd5e1;
            --text-muted: #94a3b8;
            --table-stripe: #131d31;
            --table-hover: #24344d;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: "Inter", system-ui, -apple-system, sans-serif;
            background-color: var(--bg-page);
            color: var(--text-body);
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            transition: background-color 0.2s ease, color 0.2s ease;
        }

        .topbar {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-bottom: 1px solid #334155;
            padding: 12px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 50;
        }
        .topbar-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 17px;
            font-weight: 700;
            color: #ffffff;
        }
        .topbar-actions {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .btn-theme-toggle {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #f8fafc;
            font-size: 15px;
            width: 36px;
            height: 36px;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .btn-logout {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #f8fafc;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .app-container {
            display: flex;
            flex: 1;
        }

        .sidebar {
            width: 250px;
            background-color: #0f172a;
            border-right: 1px solid #1e293b;
            padding: 20px 14px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            flex-shrink: 0;
        }
        .sidebar-section-title {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: #64748b;
            text-transform: uppercase;
            margin: 16px 8px 6px 8px;
        }
        .sidebar-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 9px 12px;
            border-radius: 8px;
            color: #94a3b8;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
        }
        .sidebar-item:hover {
            background-color: #1e293b;
            color: #f8fafc;
        }
        .sidebar-item.active {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #ffffff;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }

        .main-content {
            flex: 1;
            padding: 28px;
            overflow-y: auto;
        }
        .tab-pane {
            display: none;
        }
        .tab-pane.active {
            display: block;
        }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }
        .kpi-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        }
        .kpi-card::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 4px;
        }
        .kpi-card.blue::before { background: var(--color-primary); }
        .kpi-card.green::before { background: var(--color-success); }
        .kpi-card.orange::before { background: var(--color-warning); }
        .kpi-card.purple::before { background: var(--color-info); }
        .kpi-card.red::before { background: var(--color-danger); }

        .kpi-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        .kpi-title {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
        }
        .kpi-icon { font-size: 18px; }
        .kpi-value {
            font-size: 26px;
            font-weight: 700;
            line-height: 1.2;
            margin-bottom: 4px;
        }
        .kpi-subtitle { font-size: 12px; color: var(--text-muted); }

        .table-container {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }
        .table-modern {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }
        .table-modern th {
            background-color: var(--table-stripe);
            color: var(--text-muted);
            font-weight: 600;
            padding: 12px 16px;
            border-bottom: 2px solid var(--border-color);
            text-align: left;
        }
        .table-modern td {
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-body);
        }
        .table-modern tbody tr:nth-child(even) { background-color: var(--table-stripe); }
        .table-modern tbody tr:hover { background-color: var(--table-hover); }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
        }
        .badge-green { background: #dcfce7; color: #166534; }
        .badge-yellow { background: #fef9c3; color: #854d0e; }
        .badge-red { background: #fee2e2; color: #991b1b; }
        .badge-blue { background: #dbeafe; color: #1e40af; }
    
    @keyframes spinRadar {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .radar-spinner {
        width: 28px;
        height: 28px;
        border: 3px solid var(--border-color);
        border-top: 3px solid var(--color-primary);
        border-radius: 50%;
        animation: spinRadar 0.8s linear infinite;
        display: inline-block;
    }
    .table-compact th {
        padding: 8px 10px !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .table-compact td {
        padding: 7px 10px !important;
        font-size: 12px !important;
        line-height: 1.35;
    }

</style>

<style id="claude-acabamento-perfeito">
    /* Forçar fundos escuros nos painéis que ficaram com o fundo transparente/branco */
    .main-content > div > div:not(.kpi-grid), div[class*="card"], div[class*="panel"] {
        background-color: #12151A !important;
        border: 1px solid #303844 !important;
        color: #E8EEF6 !important;
        border-radius: 10px !important;
    }

    /* Garantir texto legível nas tabelas inferiores */
    table, tr, td, th { background: transparent !important; border-color: #303844 !important; color: #E8EEF6 !important; }
    th, .kpi-title, .kpi-subtext { color: #A9B4C6 !important; }

    /* Consertar o Botão Ouro Técnico ("Abrir Mesa") */
    button[onclick*="abrirMesa"], #btnAbrirMesa, .btn-primary {
        background-color: #D9A62E !important;
        color: #0A0A0A !important;
        border: none !important;
        font-weight: 600 !important;
    }

    /* Consertar Botões Secundários ("Atualizar") */
    .btn-secondary, button[onclick*="carregar"] {
        background-color: #12151A !important;
        color: #E8EEF6 !important;
        border: 1px solid #303844 !important;
    }
</style>


<style id="strike-correcao-definitiva">
    /* Forçar fundo escuro nos painéis inferiores independentemente do que lá estiver */
    .panel-box, .table-card, [style*="var(--bg-surface)"] {
        background-color: var(--bg-surface, #12151A) !important;
        background: var(--bg-surface, #12151A) !important;
        border: 1px solid var(--border-default, #303844) !important;
        color: var(--text-primary, #E8EEF6) !important;
    }
    
    /* Garantir que o texto das tabelas e painéis fica legível */
    .panel-box *, .table-card * { color: var(--text-primary, #E8EEF6) !important; }
    .panel-box p, .table-card p, .panel-box th, .panel-box .text-muted { color: var(--text-secondary, #A9B4C6) !important; }
    table td { border-bottom: 1px solid var(--border-subtle, #232932) !important; }

    /* Corrigir os botões no canto superior direito para não se sobreporem */
    .topbar, .master-top-actions {
        position: absolute !important;
        top: 32px !important;
        right: 40px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        gap: 12px !important;
        background: transparent !important;
        width: auto !important;
        z-index: 9999 !important;
    }
    .topbar-actions {
        display: flex !important;
        flex-direction: row !important;
        gap: 12px !important;
        position: static !important; /* Remove conflitos antigos */
    }
    .topbar-actions button, .master-top-actions button {
        position: static !important;
        margin: 0 !important;
        white-space: nowrap !important;
    }

    /* Garantir cor Dourada no botão principal */
    button[onclick*="abrirMesa"], #btnAbrirMesa, .btn-primary {
        background-color: #D9A62E !important;
        color: #0A0A0A !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
    }
</style>

    <link rel="stylesheet" href="/static/strike_tokens_2.css?v=2">
</head>
<body>

    <div class="topbar">
        <div class="topbar-brand">
            <span></span>
            <span>Radar de Licitações</span>
        </div>
        <div class="topbar-actions">
            <button id="btnThemeToggle" class="btn-theme-toggle" onclick="alternarTemaVisual()" title="Alternar Modo Claro/Escuro">
                
            </button>
            <button class="btn-logout" onclick="fazerLogout()">
                👤 Sair
            </button>
        </div>
    </div>

    <div class="app-container">
        <aside class="sidebar">
            <div class="sidebar-section-title">Visão Geral</div>
            <div class="sidebar-item active" data-tab="dashboard">
                <span> Dashboard</span>
            </div>

            <div class="sidebar-section-title">Operacional de Licitações</div>
            <div class="sidebar-item" data-tab="licitacoes">
                <span> Mural de Editais (PNCP)</span>
            </div>
            <div class="sidebar-item" data-tab="matches">
                <span> Radar de Matches</span>
            </div>
            <div class="sidebar-item" data-tab="mesa">
                <span> Mesa de Operação</span>
            </div>
            <div class="sidebar-item" data-tab="alertas">
                <span> Alertas</span>
            </div>

            <div class="sidebar-section-title">Gestão & Estratégia</div>
            <div class="sidebar-item" data-tab="preferencias">
                <span> Estratégia & Critérios</span>
            </div>
            <div class="sidebar-item" data-tab="notificacoes">
                <span> Notificações</span>
            </div>
            <div class="sidebar-item" data-tab="conta">
                <span> Empresa & Certidões</span>
            </div>
        </aside>

        <main class="main-content">
            
            <!-- 1. DASHBOARD -->
            <div id="pane-dashboard" class="tab-pane active">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <h2 style="font-size: 22px; font-weight: 700; color: var(--text-heading);">Painel Executivo</h2>
                        <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">Monitorização em tempo real de certames, propostas e conformidade documental.</p>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <button onclick="carregarDashboardCompleto()" style="background: var(--bg-card); border: 1px solid var(--border-color); color: var(--text-body); padding: 8px 16px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer;">
                            ↻ Atualizar
                        </button>
                        <button onclick="trocarAbaSistema('mesa')" style="background: var(--color-primary); color: #fff; border: none; padding: 8px 18px; border-radius: 8px; font-size: 12px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);">
                             Abrir Mesa ↗
                        </button>
                    </div>
                </div>

                <div class="kpi-grid">
                    <div class="kpi-card blue">
                        <div class="kpi-header">
                            <span class="kpi-title">Mesa em Operação</span>
                            <span class="kpi-icon"></span>
                        </div>
                        <div id="dashKpiOperacao" class="kpi-value" style="color: var(--color-primary);">0</div>
                        <div id="dashKpiOperacaoSub" class="kpi-subtitle">0 ativas / 0 análise</div>
                    </div>

                    <div class="kpi-card green">
                        <div class="kpi-header">
                            <span class="kpi-title">Pipeline de Propostas</span>
                            <span class="kpi-icon"></span>
                        </div>
                        <div id="dashKpiVolume" class="kpi-value" style="color: var(--color-success);">R$ 0,00</div>
                        <div class="kpi-subtitle">em disputa comercial</div>
                    </div>

                    <div class="kpi-card orange">
                        <div class="kpi-header">
                            <span class="kpi-title">Taxa de Conversão</span>
                            <span class="kpi-icon"></span>
                        </div>
                        <div id="dashKpiWinRate" class="kpi-value" style="color: var(--color-warning);">0%</div>
                        <div id="dashKpiWinRateSub" class="kpi-subtitle">0 ganhas / 0 perdas</div>
                    </div>

                    <div class="kpi-card purple">
                        <div class="kpi-header">
                            <span class="kpi-title">Matches de Portfólio</span>
                            <span class="kpi-icon"></span>
                        </div>
                        <div id="dashKpiMatches" class="kpi-value" style="color: var(--color-info);">0</div>
                        <div class="kpi-subtitle">editais compatíveis</div>
                    </div>

                    <div class="kpi-card green" id="cardDocContainer">
                        <div class="kpi-header">
                            <span class="kpi-title">Risco Documental</span>
                            <span class="kpi-icon"></span>
                        </div>
                        <div id="dashKpiCertidoes" class="kpi-value" style="color: var(--color-success);">0</div>
                        <div id="dashKpiCertidoesSub" class="kpi-subtitle">todas regularizadas</div>
                    </div>
                </div>

                <div class="kpi-card" style="margin-bottom: 24px; padding: 18px 22px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <span style="font-size: 13px; font-weight: 600; color: var(--text-heading);">Funil de Disputa (Mesa)</span>
                        <span style="font-size: 12px; color: var(--text-muted);">Fluxo da esteira</span>
                    </div>
                    <div style="display: flex; height: 8px; border-radius: 4px; overflow: hidden; background: var(--border-color); margin-bottom: 12px;">
                        <div id="barAtivas" style="width: 25%; background: var(--color-primary);"></div>
                        <div id="barAnalise" style="width: 25%; background: var(--color-warning);"></div>
                        <div id="barGanhas" style="width: 25%; background: var(--color-success);"></div>
                        <div id="barPerdidas" style="width: 25%; background: #94a3b8;"></div>
                    </div>
                    <div style="display: flex; gap: 20px; font-size: 12px; color: var(--text-muted); flex-wrap: wrap;">
                        <span><span style="color: var(--color-primary);">●</span> Ativas: <strong id="legAtivas">0</strong></span>
                        <span><span style="color: var(--color-warning);">●</span> Em Análise: <strong id="legAnalise">0</strong></span>
                        <span><span style="color: var(--color-success);">●</span> Ganhas: <strong id="legGanhas">0</strong></span>
                        <span><span style="color: #94a3b8;">●</span> Perdidas: <strong id="legPerdidas">0</strong></span>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1.35fr 1fr; gap: 24px;">
                    <div class="table-container" style="padding: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                            <h3 style="font-size: 15px; font-weight: 700; color: var(--text-heading);"> Editais Ativos na Mesa</h3>
                            <span style="font-size: 12px; color: var(--color-primary); cursor: pointer; font-weight: 600;" onclick="trocarAbaSistema('mesa')">Ver todos ↗</span>
                        </div>
                        <table class="table-modern">
                            <thead>
                                <tr>
                                    <th>Edital / Órgão</th>
                                    <th>Abertura</th>
                                    <th style="text-align: right;">Estimado</th>
                                    <th style="text-align: center;">Ação</th>
                                </tr>
                            </thead>
                            <tbody id="tabelaDashProximos">
                                <tr><td colspan="4" style="text-align: center; padding: 24px; color: var(--text-muted);">A carregar certames...</td></tr>
                            </tbody>
                        </table>
                    </div>

                    <div class="table-container" style="padding: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h3 style="font-size: 15px; font-weight: 700; color: var(--text-heading);"> Calibração Comercial</h3>
                            <span class="badge badge-blue">Inteligência</span>
                        </div>
                        <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 16px;">
                            Ajuste de margens e propostas conforme histórico real de desfechos.
                        </p>
                        <div id="listaMotivosPerdaDash" style="display: flex; flex-direction: column; gap: 8px;">
                            <div style="text-align: center; padding: 20px; color: var(--text-muted); font-size: 12px;">Sem dados de perdas no momento.</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2. MURAL DE EDITAIS (PNCP) -->
            
            <!-- 2. MURAL DE EDITAIS (PNCP) REFORMULADO E COMPACTO -->
            
            <!-- MURAL DE EDITAIS COM FILTROS AVANÇADOS -->
            <div id="pane-licitacoes" class="tab-pane">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; flex-wrap: wrap; gap: 8px;">
                    <div>
                        <h2 style="font-size: 18px; font-weight: 700; color: var(--text-heading); margin: 0;"> Mural de Editais (PNCP)</h2>
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
                         Filtros Avançados
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

            <div id="pane-matches" class="tab-pane">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <div>
                        <h2 style="font-size: 22px; font-weight: 700; color: var(--text-heading);"> Radar de Matches de Portfólio</h2>
                        <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">Editais identificados com alta aderência aos seus produtos.</p>
                    </div>
                    <button onclick="carregarMeusMatches()" style="background: var(--color-primary); color: #fff; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: 12px; cursor: pointer;">
                        🔄 Recalcular Matches
                    </button>
                </div>
                <div class="table-container">
                    <table class="table-modern">
                        <thead>
                            <tr>
                                <th>Edital</th>
                                <th>Órgão</th>
                                <th>Score de Aderência</th>
                                <th>Valor Estimado</th>
                                <th style="text-align: center;">Ação</th>
                            </tr>
                        </thead>
                        <tbody id="tabelaMatchesBody">
                            <tr><td colspan="5" style="text-align: center; padding: 24px; color: var(--text-muted);">A carregar matches...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 4. MESA DE OPERAÇÃO -->
            <div id="pane-mesa" class="tab-pane">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <div>
                        <h2 style="font-size: 22px; font-weight: 700; color: var(--text-heading);"> Mesa de Operação</h2>
                        <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">Gestão da esteira de propostas, cotações e disputas.</p>
                    </div>
                    <button onclick="carregarProcessosMesa(statusMesaAtual)" style="background: var(--color-primary); color: #fff; border: none; padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: 12px; cursor: pointer;">
                        🔄 Atualizar Mesa
                    </button>
                </div>
                <div style="display: flex; gap: 8px; margin-bottom: 16px;">
                    <button id="tabMesaAtiva" onclick="filtrarMesaPorStatus('ATIVA', this)" style="padding: 7px 16px; border-radius: 6px; border: none; background: var(--color-primary); color: #fff; font-size: 12px; font-weight: 700; cursor: pointer;">📌 Ativas</button>
                    <button id="tabMesaAnalise" onclick="filtrarMesaPorStatus('EM_ANALISE', this)" style="padding: 7px 16px; border-radius: 6px; border: none; background: var(--border-color); color: var(--text-body); font-size: 12px; font-weight: 700; cursor: pointer;">📝 Em Análise</button>
                    <button id="tabMesaGanha" onclick="filtrarMesaPorStatus('GANHA', this)" style="padding: 7px 16px; border-radius: 6px; border: none; background: var(--border-color); color: var(--text-body); font-size: 12px; font-weight: 700; cursor: pointer;">🏆 Ganhas</button>
                    <button id="tabMesaPerdida" onclick="filtrarMesaPorStatus('PERDIDA', this)" style="padding: 7px 16px; border-radius: 6px; border: none; background: var(--border-color); color: var(--text-body); font-size: 12px; font-weight: 700; cursor: pointer;">📉 Perdidas</button>
                </div>
                <div class="table-container">
                    <table class="table-modern">
                        <thead>
                            <tr>
                                <th>Edital / Órgão</th>
                                <th>UF</th>
                                <th>Valor Estimado</th>
                                <th>Valor Proposta</th>
                                <th style="text-align: center;">Margem</th>
                                <th style="text-align: center;">Status</th>
                                <th style="text-align: center;">Ações</th>
                            </tr>
                        </thead>
                        <tbody id="tabelaMesaProcessosBody">
                            <tr><td colspan="7" style="text-align: center; padding: 24px; color: var(--text-muted);">A carregar certames...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 5. ALERTAS & DIGEST -->
            
            <!-- 5. CENTRAL DE ALERTAS OPERACIONAIS -->
            
            <!-- 5. CENTRAL DE ALERTAS (WHATSAPP & E-MAIL) -->
            <div id="pane-alertas" class="tab-pane">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <h2 style="font-size: 22px; font-weight: 700; color: var(--text-heading); margin: 0;"> Central de Alertas & Notificações Ativas</h2>
                        <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">Configure os canais de recebimento imediato de oportunidades e prazos via WhatsApp e E-mail.</p>
                    </div>
                    <button type="button" onclick="salvarConfiguracaoAlertas()" style="background: var(--color-primary); color: #fff; border: none; padding: 8px 18px; border-radius: 8px; font-weight: 600; font-size: 13px; cursor: pointer; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);">
                        💾 Salvar Configurações de Disparo
                    </button>
                </div>

                <!-- CARDS DE CANAIS PRINCIPAIS (WHATSAPP E E-MAIL) -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
                    <!-- Canal WhatsApp -->
                    <div class="kpi-card green" style="padding: 22px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-size: 24px;">📱</span>
                                <h3 style="font-size: 16px; font-weight: 700; color: var(--text-heading); margin: 0;">Disparo via WhatsApp</h3>
                            </div>
                            <span class="badge badge-green" id="badgeStatusWhatsapp">ATIVO</span>
                        </div>
                        <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 16px;">
                            Receba alertas urgentes no celular com link direto para o edital e resumo dos itens.
                        </p>

                        <div style="margin-bottom: 14px;">
                            <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 4px;">Número do WhatsApp (com DDD)</label>
                            <div style="display: flex; gap: 8px;">
                                <input type="text" id="alertaWppNumero" placeholder="(21) 99999-9999" style="flex: 1; padding: 8px 10px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 13px; font-weight: 600; background: var(--bg-card); color: var(--text-body);">
                                <button type="button" onclick="testarDisparoWhatsapp()" style="background: #25d366; color: #fff; border: none; padding: 8px 14px; border-radius: 6px; font-size: 12px; font-weight: 700; cursor: pointer; white-space: nowrap;">
                                     Enviar Teste
                                </button>
                            </div>
                        </div>

                        <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
                            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                                <input type="checkbox" id="checkWppMatchesAltos" checked style="width: 15px; height: 15px;">
                                Disparar no WhatsApp quando surgir edital com match ≥ 80%
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                                <input type="checkbox" id="checkWppAbertura" checked style="width: 15px; height: 15px;">
                                Alerta 1 hora antes de pregões cadastrados na Mesa
                            </label>
                        </div>
                    </div>

                    <!-- Canal E-mail -->
                    <div class="kpi-card blue" style="padding: 22px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-size: 24px;">✉</span>
                                <h3 style="font-size: 16px; font-weight: 700; color: var(--text-heading); margin: 0;">Disparo via E-mail</h3>
                            </div>
                            <span class="badge badge-blue">ATIVO</span>
                        </div>
                        <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 16px;">
                            Envio de relatórios consolidados e notificações de certidões diretamente na caixa postal.
                        </p>

                        <div style="margin-bottom: 14px;">
                            <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 4px;">E-mail(s) de Destino (separe por vírgula se mais de um)</label>
                            <div style="display: flex; gap: 8px;">
                                <input type="text" id="alertaEmailDestino" placeholder="comercial@suaempresa.com.br" style="flex: 1; padding: 8px 10px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 13px; font-weight: 600; background: var(--bg-card); color: var(--text-body);">
                                <button type="button" onclick="testarDisparoEmail()" style="background: var(--color-primary); color: #fff; border: none; padding: 8px 14px; border-radius: 6px; font-size: 12px; font-weight: 700; cursor: pointer; white-space: nowrap;">
                                    ✉ Enviar Teste
                                </button>
                            </div>
                        </div>

                        <div style="display: flex; flex-direction: column; gap: 8px; font-size: 12px;">
                            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                                <input type="checkbox" id="checkEmailMatinal" checked style="width: 15px; height: 15px;">
                                Relatório matinal diário de novas oportunidades às 08:00
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                                <input type="checkbox" id="checkEmailCertidoes" checked style="width: 15px; height: 15px;">
                                Aviso preventivo quando certidões entrarem na faixa de 15 dias
                            </label>
                        </div>
                    </div>
                </div>

                <!-- HISTÓRICO DE DISPAROS RECENTES -->
                <div class="table-container" style="padding: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px;">
                        <h3 style="font-size: 15px; font-weight: 700; color: var(--text-heading); margin: 0;">
                            📜 Histórico de Alertas Recentes Enviados
                        </h3>
                        <span style="font-size: 12px; color: var(--text-muted);">Últimas 24 horas</span>
                    </div>

                    <table class="table-modern">
                        <thead>
                            <tr>
                                <th>Canal</th>
                                <th>Destinatário</th>
                                <th>Mensagem / Assunto</th>
                                <th>Data & Hora</th>
                                <th style="text-align: center;">Status de Entrega</th>
                            </tr>
                        </thead>
                        <tbody id="tabelaHistoricoAlertasBody">
                            <tr>
                                <td><span class="badge badge-green">📱 WhatsApp</span></td>
                                <td><strong>(21) 98765-4321</strong></td>
                                <td> Novo Match 94%: Pregão 045/2026 - SMS Rio (Amoxicilina 500mg)</td>
                                <td style="color: var(--text-muted);">Hoje às 08:15</td>
                                <td style="text-align: center;"><span class="badge badge-green">✓ Entregue</span></td>
                            </tr>
                            <tr>
                                <td><span class="badge badge-blue">✉ E-mail</span></td>
                                <td><strong>comercial@empresa.com.br</strong></td>
                                <td> Relatório Matinal: 8 novos editais encontrados no PNCP</td>
                                <td style="color: var(--text-muted);">Hoje às 08:00</td>
                                <td style="text-align: center;"><span class="badge badge-green">✓ Entregue</span></td>
                            </tr>
                            <tr>
                                <td><span class="badge badge-green">📱 WhatsApp</span></td>
                                <td><strong>(21) 98765-4321</strong></td>
                                <td>⚠ Atenção: Certidão Municipal expira em 12 dias</td>
                                <td style="color: var(--text-muted);">Ontem às 16:30</td>
                                <td style="text-align: center;"><span class="badge badge-green">✓ Entregue</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <div id="pane-preferencias" class="tab-pane">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
                    <div>
                        <h2 style="font-size: 22px; font-weight: 700; color: var(--text-heading); margin: 0;"> Estratégia Comercial & Critérios de Participação</h2>
                        <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">Defina regras comerciais, modalidades aceitas e governança de lances.</p>
                    </div>
                    <button type="button" onclick="salvarPreferenciasConfig()" style="background: var(--color-primary); color: #fff; border: none; padding: 8px 18px; border-radius: 8px; font-weight: 600; font-size: 13px; cursor: pointer; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);">
                        💾 Salvar Estratégia
                    </button>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                    <div class="kpi-card" style="padding: 20px;">
                        <h3 style="font-size: 14px; font-weight: 700; color: var(--text-heading); margin-bottom: 12px; border-bottom: 1px solid var(--border-color); padding-bottom: 6px;">
                            🏛 Modalidades & Julgamento Aceitos
                        </h3>
                        <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 14px;">
                            <label style="display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer;">
                                <input type="checkbox" id="prefModPregao" checked style="width: 16px; height: 16px;">
                                Pregão Eletrônico (Lei 14.133/2021)
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer;">
                                <input type="checkbox" id="prefModDispensa" checked style="width: 16px; height: 16px;">
                                Dispensa Eletrônica / Cotação Rápida
                            </label>
                            <label style="display: flex; align-items: center; gap: 8px; font-size: 13px; cursor: pointer;">
                                <input type="checkbox" id="prefModConcorrencia" style="width: 16px; height: 16px;">
                                Concorrência Pública / Diálogo Competitivo
                            </label>
                        </div>
                        <div style="margin-top: 10px;">
                            <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 4px;">Tipo de Julgamento Preferencial</label>
                            <select id="prefTipoJulgamento" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 13px; background: var(--bg-card); color: var(--text-body);">
                                <option value="ITEM">Menor Preço por Item / Lote Único</option>
                                <option value="GLOBAL">Menor Preço Global / Grupo</option>
                                <option value="TODOS" selected>Qualquer Critério de Menor Preço</option>
                            </select>
                        </div>
                    </div>

                    <div class="kpi-card" style="padding: 20px;">
                        <h3 style="font-size: 14px; font-weight: 700; color: var(--text-heading); margin-bottom: 12px; border-bottom: 1px solid var(--border-color); padding-bottom: 6px;">
                            ⚖ Governança de Margens & Parâmetros
                        </h3>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px;">
                            <div>
                                <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 4px;">Piso Stop-Loss (%)</label>
                                <input type="number" id="prefMargemMinima" value="15" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 13px; font-weight: bold; color: var(--color-danger); background: var(--bg-card);">
                            </div>
                            <div>
                                <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 4px;">Margem Alvo (%)</label>
                                <input type="number" id="prefMargemAlvo" value="25" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 13px; font-weight: bold; color: var(--color-success); background: var(--bg-card);">
                            </div>
                        </div>
                        <div style="margin-bottom: 12px;">
                            <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 4px;">UFs Prioritárias de Atuação</label>
                            <input type="text" id="prefUfs" value="RJ, SP, MG, PR" placeholder="RJ, SP, MG, PR" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 13px; text-transform: uppercase; background: var(--bg-card); color: var(--text-body);">
                        </div>
                        <div>
                            <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 4px;">Desempate ME/EPP (LC 123/2006)</label>
                            <select id="prefRegraMeEpp" style="width: 100%; padding: 8px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 13px; background: var(--bg-card); color: var(--text-body);">
                                <option value="SIM" selected>Simular e Cobrir Lance de Empate (até 5%)</option>
                                <option value="NAO">Ignorar Desempate Automático</option>
                            </select>
                        </div>
                    </div>

                    <div class="kpi-card" style="grid-column: span 2; padding: 20px;">
                        <h3 style="font-size: 14px; font-weight: 700; color: var(--text-heading); margin-bottom: 4px;">
                            📦 Catálogo de Itens & Palavras-Chave do Portfólio
                        </h3>
                        <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 8px;">Termos cruzados automaticamente com os editais do PNCP em tempo real.</p>
                        <textarea id="prefPalavrasChave" rows="3" placeholder="Ex: amoxicilina, paracetamol 500mg, seringa descartavel luer lock, luva cirurgica estéril, propofol..." style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 13px; margin-bottom: 16px; background: var(--bg-card); color: var(--text-body);"></textarea>

                        <h3 style="font-size: 14px; font-weight: 700; color: var(--color-danger); margin-bottom: 4px;">
                            🚫 Filtro Anti-Ruído (Blacklist de Objeto)
                        </h3>
                        <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 6px;">Editais contendo esses termos serão automaticamente descartados do radar.</p>
                        <textarea id="prefBlacklist" rows="2" placeholder="Ex: merenda escolar, asfalto, locação de ambulância, manutenção predial, fardamento..." style="width: 100%; padding: 10px; border: 1px solid var(--border-color); border-radius: 6px; font-size: 13px; background: var(--bg-card); color: var(--text-body);"></textarea>
                    </div>
                </div>
            </div>

            <!-- 7. NOTIFICAÇÕES -->
            <div id="pane-notificacoes" class="tab-pane">
                <div style="margin-bottom: 20px;">
                    <h2 style="font-size: 22px; font-weight: 700; color: var(--text-heading);"> Central de Notificações</h2>
                    <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">Avisos em tempo real e regras de envio.</p>
                </div>
                <div class="kpi-card" style="padding: 24px;">
                    <p style="font-size: 13px; color: var(--text-muted);">As notificações do sistema alertam sobre novos editais no PNCP e certidões a vencer.</p>
                </div>
            </div>

            <!-- 8. EMPRESA & CERTIDÕES COMPLETA -->
            <div id="pane-conta" class="tab-pane">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <div>
                        <h2 style="font-size: 22px; font-weight: 700; color: var(--text-heading); margin: 0;"> Gestão da Empresa & Habilitação</h2>
                        <p style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">Configurações institucionais, ramo de atividade, certidões e equipa.</p>
                    </div>
                </div>

                <div style="display: flex; gap: 8px; margin-bottom: 20px;">
                    <button class="subtab-btn" onclick="alternarSubTabEmpresa('dados', this)" style="padding: 7px 16px; border-radius: 6px; border: none; background: var(--color-primary); color: #fff; font-size: 12px; font-weight: 700; cursor: pointer;">
                         Dados Gerais
                    </button>
                    <button class="subtab-btn" onclick="alternarSubTabEmpresa('pagamento', this)" style="padding: 7px 16px; border-radius: 6px; border: none; background: var(--border-color); color: var(--text-body); font-size: 12px; font-weight: 700; cursor: pointer;">
                        💳 Pagamento da Plataforma
                    </button>
                    <button class="subtab-btn" onclick="alternarSubTabEmpresa('usuarios', this)" style="padding: 7px 16px; border-radius: 6px; border: none; background: var(--border-color); color: var(--text-body); font-size: 12px; font-weight: 700; cursor: pointer;">
                        👥 Membros da Equipa
                    </button>
                </div>

                <div id="subpane-empresa-dados" class="subpane-empresa">
                    <div style="display: flex; justify-content: flex-end; margin-bottom: 12px;">
                        <button onclick="salvarDadosEmpresaConfig()" style="background: var(--color-primary); color: #fff; border: none; padding: 7px 18px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.25);">
                            💾 Salvar Dados da Empresa
                        </button>
                    </div>

                    <div style="display: grid; grid-template-columns: 1.2fr 0.9fr; gap: 16px; align-items: start;">
                        <div style="display: flex; flex-direction: column; gap: 14px;">
                            <div class="kpi-card" style="padding: 16px;">
                                <h3 style="font-size: 13px; font-weight: 700; color: var(--text-heading); margin-bottom: 10px; border-bottom: 1px solid var(--border-color); padding-bottom: 6px;">
                                     Identificação & Ramo de Atuação
                                </h3>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                                    <div style="grid-column: span 2;">
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">Razão Social</label>
                                        <input type="text" id="empRazaoSocial" placeholder="Razão Social Completa" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                    </div>
                                    <div>
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">Nome Fantasia</label>
                                        <input type="text" id="empNomeFantasia" placeholder="Nome Comercial" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                    </div>
                                    <div>
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">Porte (LC 123/2006)</label>
                                        <select id="empPorte" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                            <option value="ME">Microempresa (ME)</option>
                                            <option value="EPP" selected>Empresa de Pequeno Porte (EPP)</option>
                                            <option value="GERAL">Médio / Grande Porte</option>
                                        </select>
                                    </div>

                                    <div style="grid-column: span 2;">
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">Ramo de Atuação / Segmento Comercial Principal</label>
                                        <select id="empRamoAtuacao" style="width: 100%; padding: 7px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; font-weight: 600; background: var(--bg-card); color: var(--text-body);">
                                            <option value="">Selecione o segmento...</option>
                                            <option value="FARMACO">Medicamentos, Fármacos e Vacinas</option>
                                            <option value="HOSPITALAR">Materiais Médicos, Cirúrgicos e Descartáveis (OPME)</option>
                                            <option value="EQUIPAMENTOS">Equipamentos Médicos, Odontológicos e Laboratoriais</option>
                                            <option value="SANEANTES">Saneantes, Cosméticos e Higienização Hospitalar</option>
                                            <option value="NUTRICAO">Dietas Enterais, Nutrição Especial e Suplementos</option>
                                            <option value="ENGENHARIA">Engenharia, Manutenção e Obras</option>
                                            <option value="SERVICOS">Serviços Gerais e Locação</option>
                                            <option value="OUTRO">Outro Segmento Comercial</option>
                                        </select>
                                    </div>
                                    <div style="grid-column: span 2;">
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">CNAE Principal ou Objeto Social</label>
                                        <input type="text" id="empCnaePrincipal" placeholder="Ex: 46.44-3-01 - Comércio atacadista de medicamentos" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                    </div>

                                    <div>
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">CNPJ</label>
                                        <input type="text" id="empCnpj" placeholder="00.000.000/0001-00" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                    </div>
                                    <div>
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">Inscrição Estadual (IE)</label>
                                        <input type="text" id="empIE" placeholder="Isento ou Nº" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                    </div>
                                    <div style="grid-column: span 2;">
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">Endereço Completo</label>
                                        <input type="text" id="empEndereco" placeholder="Logradouro, Nº, Bairro, CEP" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                    </div>
                                    <div>
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">Cidade / UF</label>
                                        <input type="text" id="empCidadeUf" placeholder="Rio de Janeiro / RJ" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                    </div>
                                    <div>
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">Telefone / WhatsApp</label>
                                        <input type="text" id="empTelefone" placeholder="(21) 99999-9999" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                    </div>
                                </div>
                            </div>

                            <div class="kpi-card" style="padding: 16px;">
                                <h3 style="font-size: 13px; font-weight: 700; color: var(--text-heading); margin-bottom: 10px; border-bottom: 1px solid var(--border-color); padding-bottom: 6px;">
                                    ✍ Representante & Dados Bancários
                                </h3>
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                                    <div>
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">Procurador / Representante</label>
                                        <input type="text" id="empRepNome" placeholder="Nome Completo" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                    </div>
                                    <div>
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">CPF do Representante</label>
                                        <input type="text" id="empRepCpf" placeholder="000.000.000-00" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                    </div>
                                    <div>
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">Banco & Agência</label>
                                        <input type="text" id="empBancoAgencia" placeholder="Ex: Itaú - Ag 1234" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                    </div>
                                    <div>
                                        <label style="font-size: 11px; font-weight: 600; color: var(--text-muted); display: block; margin-bottom: 2px;">Conta Corrente / PIX</label>
                                        <input type="text" id="empContaPix" placeholder="CC: 12345-6 / PIX" style="width: 100%; padding: 6px 8px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 12px; background: var(--bg-card); color: var(--text-body);">
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="kpi-card" style="padding: 16px;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                                <h3 style="font-size: 13px; font-weight: 700; color: var(--text-heading); margin: 0;"> Radar de Certidões & Validades</h3>
                                <button type="button" onclick="adicionarNovoDocumentoCertidao()" style="background: var(--table-stripe); color: var(--color-primary); border: 1px solid var(--border-color); padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; cursor: pointer;">
                                    + Outro Documento
                                </button>
                            </div>
                            <p style="font-size: 11px; color: var(--text-muted); margin-bottom: 10px;">Monitorização contínua de prazos para evitar inabilitação.</p>

                            <div style="display: flex; flex-direction: column; gap: 6px;" id="containerCertidoesLista">
                                <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: var(--table-stripe); border-radius: 4px; border: 1px solid var(--border-color); gap: 8px;">
                                    <div style="flex: 1;">
                                        <span style="font-size: 11px; font-weight: 600; display: block;">CND Federal / INSS</span>
                                        <span id="badgeCndFederal" style="font-size: 10px; font-weight: 700; padding: 1px 5px; border-radius: 3px;">-</span>
                                    </div>
                                    <input type="date" id="valCndFederal" onchange="atualizarBadgesCertidoes()" style="width: 130px; padding: 4px 6px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 11px; background: var(--bg-card); color: var(--text-body);">
                                </div>

                                <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: var(--table-stripe); border-radius: 4px; border: 1px solid var(--border-color); gap: 8px;">
                                    <div style="flex: 1;">
                                        <span style="font-size: 11px; font-weight: 600; display: block;">CRF FGTS (Caixa)</span>
                                        <span id="badgeCrfFgts" style="font-size: 10px; font-weight: 700; padding: 1px 5px; border-radius: 3px;">-</span>
                                    </div>
                                    <input type="date" id="valCrfFgts" onchange="atualizarBadgesCertidoes()" style="width: 130px; padding: 4px 6px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 11px; background: var(--bg-card); color: var(--text-body);">
                                </div>

                                <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: var(--table-stripe); border-radius: 4px; border: 1px solid var(--border-color); gap: 8px;">
                                    <div style="flex: 1;">
                                        <span style="font-size: 11px; font-weight: 600; display: block;">CNDT Trabalhista</span>
                                        <span id="badgeCndt" style="font-size: 10px; font-weight: 700; padding: 1px 5px; border-radius: 3px;">-</span>
                                    </div>
                                    <input type="date" id="valCndt" onchange="atualizarBadgesCertidoes()" style="width: 130px; padding: 4px 6px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 11px; background: var(--bg-card); color: var(--text-body);">
                                </div>

                                <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: var(--table-stripe); border-radius: 4px; border: 1px solid var(--border-color); gap: 8px;">
                                    <div style="flex: 1;">
                                        <span style="font-size: 11px; font-weight: 600; display: block;">CND Estadual (SEFAZ)</span>
                                        <span id="badgeCndEstadual" style="font-size: 10px; font-weight: 700; padding: 1px 5px; border-radius: 3px;">-</span>
                                    </div>
                                    <input type="date" id="valCndEstadual" onchange="atualizarBadgesCertidoes()" style="width: 130px; padding: 4px 6px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 11px; background: var(--bg-card); color: var(--text-body);">
                                </div>

                                <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 10px; background: var(--table-stripe); border-radius: 4px; border: 1px solid var(--border-color); gap: 8px;">
                                    <div style="flex: 1;">
                                        <span style="font-size: 11px; font-weight: 600; display: block;">CND Municipal</span>
                                        <span id="badgeCndMunicipal" style="font-size: 10px; font-weight: 700; padding: 1px 5px; border-radius: 3px;">-</span>
                                    </div>
                                    <input type="date" id="valCndMunicipal" onchange="atualizarBadgesCertidoes()" style="width: 130px; padding: 4px 6px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 11px; background: var(--bg-card); color: var(--text-body);">
                                </div>

                                <div id="listaDocumentosExtras" style="display: flex; flex-direction: column; gap: 6px; margin-top: 2px;"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <div id="subpane-empresa-pagamento" class="subpane-empresa" style="display: none;">
                    <div class="kpi-card" style="padding: 24px; max-width: 600px;">
                        <span class="badge badge-green">PLANO ATIVO</span>
                        <h3 style="font-size: 20px; font-weight: 700; color: var(--text-heading); margin-top: 8px;">Radar Enterprise</h3>
                        <p style="color: var(--text-muted); font-size: 13px; margin: 4px 0 16px 0;">Acesso ilimitado às licitações e esteira de margens do PNCP.</p>
                        <div style="font-size: 22px; font-weight: 700; color: var(--color-primary);">R$ 499,00 <span style="font-size: 12px; color: var(--text-muted);">/ mês</span></div>
                    </div>
                </div>

                <div id="subpane-empresa-usuarios" class="subpane-empresa" style="display: none;">
                    <div class="table-container" style="padding: 20px;">
                        <h3 style="font-size: 15px; font-weight: 700; color: var(--text-heading); margin-bottom: 12px;">Membros da Equipa</h3>
                        <table class="table-modern">
                            <thead>
                                <tr>
                                    <th>Nome</th>
                                    <th>E-mail</th>
                                    <th>Função</th>
                                    <th style="text-align: center;">Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>Administrador</strong></td>
                                    <td>admin@radarlicitacoes.com.br</td>
                                    <td>Gestor Principal</td>
                                    <td style="text-align: center;"><span class="badge badge-green">ATIVO</span></td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

        </main>
    </div>

    <script>
        function alternarTemaVisual() {
            const isDark = document.body.classList.toggle("dark-mode");
            localStorage.setItem("radar_dark_mode", isDark);
            const btn = document.getElementById("btnThemeToggle");
            if (btn) btn.innerHTML = isDark ? "☀" : "";
        }

        function trocarAbaSistema(nome) {
            document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
            document.querySelectorAll(".sidebar-item").forEach(i => i.classList.remove("active"));

            const pane = document.getElementById("pane-" + nome);
            if (pane) pane.classList.add("active");

            const nav = document.querySelector(`.sidebar-item[data-tab="${nome}"]`);
            if (nav) nav.classList.add("active");

            if (nome === "dashboard") carregarDashboardCompleto();
            if (nome === "mesa") carregarProcessosMesa(statusMesaAtual);
            if (nome === "matches") carregarMeusMatches();
            if (nome === "licitacoes") carregarLicitacoesPncp();
            if (nome === "conta") carregarDadosEmpresaConfig();
            if (nome === "preferencias") carregarPreferenciasConfig();
        }

        function alternarSubTabEmpresa(subaba, btn) {
            document.querySelectorAll(".subpane-empresa").forEach(p => p.style.display = "none");
            document.querySelectorAll(".subtab-btn").forEach(b => {
                b.style.background = "var(--border-color)";
                b.style.color = "var(--text-body)";
            });
            if (btn) {
                btn.style.background = "var(--color-primary)";
                btn.style.color = "#fff";
            }
            const alvo = document.getElementById("subpane-empresa-" + subaba);
            if (alvo) alvo.style.display = "block";
        }

        document.addEventListener("DOMContentLoaded", function() {
            document.querySelectorAll(".sidebar-item").forEach(item => {
                const tab = item.getAttribute("data-tab");
                if (tab) {
                    item.addEventListener("click", function(e) {
                        e.preventDefault();
                        trocarAbaSistema(tab);
                    });
                }
            });

            if (localStorage.getItem("radar_dark_mode") === "true") {
                document.body.classList.add("dark-mode");
                const btn = document.getElementById("btnThemeToggle");
                if (btn) btn.innerHTML = "☀";
            }

            carregarDashboardCompleto();
        });

        let statusMesaAtual = "ATIVA";
        function filtrarMesaPorStatus(status, btn) {
            statusMesaAtual = status;
            document.querySelectorAll("#pane-mesa button[id^='tabMesa']").forEach(b => {
                b.style.background = "var(--border-color)";
                b.style.color = "var(--text-body)";
            });
            if (btn) {
                btn.style.background = "var(--color-primary)";
                btn.style.color = "#fff";
            }
            carregarProcessosMesa(status);
        }

        async function carregarProcessosMesa(status = "ATIVA") {
            const tbody = document.getElementById("tabelaMesaProcessosBody");
            if (!tbody) return;
            try {
                const res = await fetch(`/api/processos?status=${status}`);
                const data = await res.json();
                const lista = data.processos || [];
                if (lista.length === 0) {
                    tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 24px; color: var(--text-muted);">Nenhum processo nesta categoria.</td></tr>`;
                    return;
                }
                tbody.innerHTML = lista.map(p => `
                    <tr>
                        <td><strong>${p.numero_edital || "-"}</strong><div style="font-size: 11px; color: var(--text-muted);">${p.orgao_nome || ""}</div></td>
                        <td style="font-weight: 600;">${p.uf || "BR"}</td>
                        <td>R$ ${(p.valor_estimado || 0).toLocaleString("pt-BR", {minimumFractionDigits: 2})}</td>
                        <td style="font-weight: 600; color: var(--color-success);">${p.proposta_valor ? "R$ " + p.proposta_valor.toLocaleString("pt-BR", {minimumFractionDigits: 2}) : "<span style='color: var(--text-muted);'>Não cotado</span>"}</td>
                        <td style="text-align: center; font-weight: bold;">${p.margem_estimada ? p.margem_estimada + "%" : "-"}</td>
                        <td style="text-align: center;"><span class="badge badge-blue">${p.status}</span></td>
                        <td style="text-align: center;">${p.link_edital ? `<a href="${p.link_edital}" target="_blank" style="padding: 4px 8px; background: var(--border-color); color: var(--color-primary); border-radius: 4px; text-decoration: none; font-size: 11px; font-weight: 600;">Edital ↗</a>` : "-"}</td>
                    </tr>
                `).join("");
            } catch (e) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 20px; color: var(--color-danger);">Erro ao carregar dados da mesa.</td></tr>`;
            }
        }

        async function carregarDashboardCompleto() {
            try {
                const res = await fetch("/api/dashboard-stats");
                if (!res.ok) return;
                const data = await res.json();
                const k = data.kpis || {};

                const op = document.getElementById("dashKpiOperacao"); if (op) op.textContent = k.em_operacao || 0;
                const opSub = document.getElementById("dashKpiOperacaoSub"); if (opSub) opSub.textContent = `${k.ativas || 0} ativas / ${k.em_analise || 0} análise`;
                const vol = document.getElementById("dashKpiVolume"); if (vol) vol.textContent = `R$ ${(k.total_propostas || 0).toLocaleString("pt-BR", {minimumFractionDigits: 2})}`;
                const win = document.getElementById("dashKpiWinRate"); if (win) win.textContent = `${k.win_rate || 0}%`;
                const winSub = document.getElementById("dashKpiWinRateSub"); if (winSub) winSub.textContent = `${k.ganhas || 0} ganhas / ${k.perdidas || 0} perdas`;
                const mat = document.getElementById("dashKpiMatches"); if (mat) mat.textContent = k.total_matches || 0;

                const cert = document.getElementById("dashKpiCertidoes");
                const certSub = document.getElementById("dashKpiCertidoesSub");
                const cardDoc = document.getElementById("cardDocContainer");
                if (cert) {
                    cert.textContent = k.certidoes_risco || 0;
                    if ((k.certidoes_risco || 0) > 0) {
                        cert.style.color = "var(--color-warning)";
                        if (certSub) certSub.textContent = "atenção ao prazo";
                        if (cardDoc) cardDoc.className = "kpi-card orange";
                    } else {
                        cert.style.color = "var(--color-success)";
                        if (certSub) certSub.textContent = "todas regularizadas";
                        if (cardDoc) cardDoc.className = "kpi-card green";
                    }
                }

                const totalFunil = (k.ativas || 0) + (k.em_analise || 0) + (k.ganhas || 0) + (k.perdidas || 0);
                const bAt = document.getElementById("barAtivas");
                const bAn = document.getElementById("barAnalise");
                const bGa = document.getElementById("barGanhas");
                const bPe = document.getElementById("barPerdidas");
                if (bAt && bAn && bGa && bPe) {
                    if (totalFunil > 0) {
                        bAt.style.width = `${((k.ativas || 0) / totalFunil) * 100}%`;
                        bAn.style.width = `${((k.em_analise || 0) / totalFunil) * 100}%`;
                        bGa.style.width = `${((k.ganhas || 0) / totalFunil) * 100}%`;
                        bPe.style.width = `${((k.perdidas || 0) / totalFunil) * 100}%`;
                    }
                }
                const lAt = document.getElementById("legAtivas"); if (lAt) lAt.textContent = k.ativas || 0;
                const lAn = document.getElementById("legAnalise"); if (lAn) lAn.textContent = k.em_analise || 0;
                const lGa = document.getElementById("legGanhas"); if (lGa) lGa.textContent = k.ganhas || 0;
                const lPe = document.getElementById("legPerdidas"); if (lPe) lPe.textContent = k.perdidas || 0;

                const tbodyProximos = document.getElementById("tabelaDashProximos");
                if (tbodyProximos) {
                    const lista = data.proximos_pregoes || [];
                    if (lista.length === 0) {
                        tbodyProximos.innerHTML = `<tr><td colspan="4" style="text-align: center; padding: 20px; color: var(--text-muted);">Nenhum edital ativo na mesa no momento.</td></tr>`;
                    } else {
                        tbodyProximos.innerHTML = lista.map(p => `
                            <tr>
                                <td><strong>${p.numero_edital}</strong><div style="font-size: 11px; color: var(--text-muted);">${p.orgao_nome} (${p.uf})</div></td>
                                <td style="color: var(--text-muted);">${p.data_abertura || "-"}</td>
                                <td style="font-weight: 600; text-align: right;">R$ ${(p.valor_estimado || 0).toLocaleString("pt-BR", {minimumFractionDigits: 2})}</td>
                                <td style="text-align: center;"><button onclick="trocarAbaSistema('mesa');" style="padding: 4px 10px; border-radius: 4px; border: 1px solid var(--border-color); background: var(--bg-card); cursor: pointer; font-size: 11px; font-weight: 600;">Abrir ↗</button></td>
                            </tr>
                        `).join("");
                    }
                }
            } catch (e) {
                console.error("Dashboard:", e);
            }
        }

        function adicionarNovoDocumentoCertidao(nome = "", dataVal = "") {
            const container = document.getElementById("listaDocumentosExtras");
            if (!container) return;

            const row = document.createElement("div");
            row.className = "doc-extra-item";
            row.style = "display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; border: 1px solid var(--border-color); border-radius: 4px; background: var(--table-stripe); gap: 8px;";
            
            row.innerHTML = `
                <div style="flex: 1; display: flex; flex-direction: column; gap: 2px;">
                    <input type="text" class="doc-extra-nome" value="${nome}" placeholder="Nome (ex: AFE Anvisa, Alvará)" style="border: 1px solid var(--border-color); padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: bold; color: var(--color-primary); width: 95%; background: var(--bg-card);">
                    <span class="doc-extra-badge" style="font-size: 10px; font-weight: 700; padding: 1px 5px; border-radius: 3px; align-self: flex-start;">-</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <input type="date" class="doc-extra-data" value="${dataVal}" onchange="atualizarBadgesCertidoes()" style="width: 130px; padding: 4px 6px; border: 1px solid var(--border-color); border-radius: 4px; font-size: 11px; background: var(--bg-card); color: var(--text-body);">
                    <button type="button" onclick="this.closest('.doc-extra-item').remove(); atualizarBadgesCertidoes();" title="Remover documento" style="background: transparent; border: none; color: var(--color-danger); font-weight: bold; cursor: pointer; font-size: 14px;">&times;</button>
                </div>
            `;
            container.appendChild(row);
            atualizarBadgesCertidoes();
        }

        function calcularStatusDataCertidao(dataStr) {
            if (!dataStr) return { texto: "Não informada", cor: "#94a3b8", bg: "#f1f5f9" };
            const hoje = new Date();
            hoje.setHours(0, 0, 0, 0);
            const partes = dataStr.split("-");
            const dtVal = new Date(partes[0], partes[1] - 1, partes[2]);
            const diffDias = Math.ceil((dtVal - hoje) / (1000 * 60 * 60 * 24));

            if (diffDias < 0) {
                return { texto: `🔴 VENCIDA (${Math.abs(diffDias)}d atrás)`, cor: "#991b1b", bg: "#fee2e2" };
            } else if (diffDias <= 15) {
                return { texto: `🟡 Vence em ${diffDias}d`, cor: "#854d0e", bg: "#fef9c3" };
            } else {
                return { texto: `🟢 Válida (${diffDias}d)`, cor: "#166534", bg: "#dcfce7" };
            }
        }

        function atualizarBadgesCertidoes() {
            const certs = [
                { input: "valCndFederal", badge: "badgeCndFederal" },
                { input: "valCrfFgts", badge: "badgeCrfFgts" },
                { input: "valCndt", badge: "badgeCndt" },
                { input: "valCndEstadual", badge: "badgeCndEstadual" },
                { input: "valCndMunicipal", badge: "badgeCndMunicipal" }
            ];

            certs.forEach(c => {
                const inp = document.getElementById(c.input);
                const bdg = document.getElementById(c.badge);
                if (inp && bdg) {
                    const res = calcularStatusDataCertidao(inp.value);
                    bdg.textContent = res.texto;
                    bdg.style.color = res.cor;
                    bdg.style.background = res.bg;
                }
            });

            document.querySelectorAll(".doc-extra-item").forEach(item => {
                const dataInput = item.querySelector(".doc-extra-data");
                const badge = item.querySelector(".doc-extra-badge");
                if (dataInput && badge) {
                    const res = calcularStatusDataCertidao(dataInput.value);
                    badge.textContent = res.texto;
                    badge.style.color = res.cor;
                    badge.style.background = res.bg;
                }
            });
        }

        async function carregarDadosEmpresaConfig() {
            try {
                const res = await fetch("/api/empresa");
                if (!res.ok) return;
                const data = await res.json();
                const e = data.empresa || {};

                const setVal = (id, v) => { const el = document.getElementById(id); if (el && v !== undefined) el.value = v; };
                setVal("empRazaoSocial", e.razao_social || "");
                setVal("empNomeFantasia", e.nome_fantasia || "");
                setVal("empPorte", e.porte || "EPP");
                setVal("empRamoAtuacao", e.ramo_atuacao || "");
                setVal("empCnaePrincipal", e.cnae_principal || "");
                setVal("empCnpj", e.cnpj || "");
                setVal("empIE", e.inscricao_estadual || "");
                setVal("empEndereco", e.endereco || "");
                setVal("empCidadeUf", e.cidade_uf || "");
                setVal("empTelefone", e.telefone || "");
                setVal("empRepNome", e.representante_nome || "");
                setVal("empRepCpf", e.representante_cpf || "");
                setVal("empBancoAgencia", e.banco_nome || "");
                setVal("empContaPix", e.chave_pix || "");

                setVal("valCndFederal", e.val_cnd_federal || "");
                setVal("valCrfFgts", e.val_crf_fgts || "");
                setVal("valCndt", e.val_cndt_trabalhista || "");
                setVal("valCndEstadual", e.val_cnd_estadual || "");
                setVal("valCndMunicipal", e.val_cnd_municipal || "");

                const container = document.getElementById("listaDocumentosExtras");
                if (container) container.innerHTML = "";
                (e.outros_documentos || []).forEach(doc => {
                    adicionarNovoDocumentoCertidao(doc.nome, doc.validade);
                });

                atualizarBadgesCertidoes();
            } catch (err) {
                console.error("Erro empresa:", err);
            }
        }

        async function salvarDadosEmpresaConfig() {
            const docsExtras = [];
            document.querySelectorAll(".doc-extra-item").forEach(item => {
                const nome = item.querySelector(".doc-extra-nome")?.value.trim();
                const dataVal = item.querySelector(".doc-extra-data")?.value;
                if (nome) docsExtras.push({ nome: nome, validade: dataVal || "" });
            });

            const getVal = id => document.getElementById(id)?.value || "";
            const payload = {
                razao_social: getVal("empRazaoSocial"),
                nome_fantasia: getVal("empNomeFantasia"),
                porte: getVal("empPorte") || "EPP",
                ramo_atuacao: getVal("empRamoAtuacao"),
                cnae_principal: getVal("empCnaePrincipal"),
                cnpj: getVal("empCnpj"),
                inscricao_estadual: getVal("empIE"),
                endereco: getVal("empEndereco"),
                cidade_uf: getVal("empCidadeUf"),
                telefone: getVal("empTelefone"),
                representante_nome: getVal("empRepNome"),
                representante_cpf: getVal("empRepCpf"),
                banco_nome: getVal("empBancoAgencia"),
                chave_pix: getVal("empContaPix"),
                val_cnd_federal: getVal("valCndFederal"),
                val_crf_fgts: getVal("valCrfFgts"),
                val_cndt_trabalhista: getVal("valCndt"),
                val_cnd_estadual: getVal("valCndEstadual"),
                val_cnd_municipal: getVal("valCndMunicipal"),
                outros_documentos: docsExtras
            };

            try {
                const res = await fetch("/api/empresa", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                alert(data.mensagem || "Dados e documentos gravados com sucesso!");
                atualizarBadgesCertidoes();
            } catch (err) {
                alert("Erro ao gravar dados: " + err.message);
            }
        }

        async function carregarPreferenciasConfig() {
            try {
                const res = await fetch("/api/preferencias");
                if (!res.ok) return;
                const data = await res.json();
                const p = data.preferencias || {};

                const setVal = (id, v) => { const el = document.getElementById(id); if (el && v !== undefined) el.value = v; };
                setVal("prefMargemMinima", p.margem_minima || 15);
                setVal("prefMargemAlvo", p.margem_alvo || 25);
                setVal("prefUfs", p.ufs || "RJ, SP, MG, PR");
                setVal("prefPalavrasChave", p.palavras_chave || "");
                setVal("prefBlacklist", p.blacklist || "");
            } catch (e) {}
        }

        async function salvarPreferenciasConfig() {
            const getVal = id => document.getElementById(id)?.value || "";
            const payload = {
                margem_minima: parseFloat(getVal("prefMargemMinima")) || 15,
                margem_alvo: parseFloat(getVal("prefMargemAlvo")) || 25,
                ufs: getVal("prefUfs"),
                palavras_chave: getVal("prefPalavrasChave"),
                blacklist: getVal("prefBlacklist")
            };

            try {
                const res = await fetch("/api/preferencias", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                alert("Estratégia comercial gravada com sucesso!");
            } catch (e) {
                alert("Erro ao salvar preferências: " + e.message);
            }
        }

        function fazerLogout() {
            if (confirm("Deseja realmente sair da plataforma?")) {
                location.href = "/";
            }
        }
    
        

    
        // --- MURAL PNCP INTEGRADO AO ENDPOINT REAL ---
        

        async function promoverEditalParaMesa(numero, orgao, uf, valor) {
            try {
                const res = await fetch('/promover-pncp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        numero_edital: numero,
                        orgao_nome: orgao,
                        uf: uf,
                        valor_estimado: valor
                    })
                });
                if (res.ok) {
                    alert(`✅ Edital ${numero} promovido para a Mesa de Operação com sucesso!`);
                } else {
                    alert(`Edital ${numero} enviado.`);
                }
            } catch (e) {
                alert(`Edital adicionado à mesa.`);
            }
        }

    
        

    
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
                if (termo) params.append("busca", termo);
                if (uf) params.append("uf", uf);
                if (valMin > 0) params.append("valor_min", valMin);
                if (valMax > 0) params.append("valor_max", valMax);

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

                // 1. Filtro rigoroso de texto (Objeto, Descrição e Órgão)
                if (termo) {
                    const termoNorm = normalizarTexto(termo);
                    const palavras = termoNorm.split(/\s+/).filter(p => p.length > 1);
                    
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
                                    <button type="button" onclick="promoverEditalParaMesa('${numero}', '${orgao.replace(/'/g, "\'")}', '${estado}', ${rawVal})" style="padding: 3px 8px; background: var(--color-primary); color: #fff; border: none; border-radius: 4px; font-size: 10px; font-weight: 700; cursor: pointer;">
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
                            ⚠ Erro ao carregar mural: ${err.message}
                        </td>
                    </tr>
                `;
            }
        }

    
        function normalizarTexto(txt) {
            if (!txt) return "";
            return txt.toString().toLowerCase()
                .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
                .trim();
        }

    </script>

        /<script>

        // --- CONTROLE DE WHATSAPP E E-MAIL ---
        async function carregarConfiguracaoAlertas() {
            try {
                // Tenta puxar telefone da empresa como padrão do WhatsApp
                const res = await fetch('/api/empresa');
                if (res.ok) {
                    const data = await res.json();
                    const e = data.empresa || {};
                    const wppInp = document.getElementById("alertaWppNumero");
                    if (wppInp && !wppInp.value && e.telefone) {
                        wppInp.value = e.telefone;
                    }
                }
            } catch(err) {}

            const savedWpp = localStorage.getItem("radar_alerta_wpp");
            const savedEmail = localStorage.getItem("radar_alerta_email");
            if (savedWpp && document.getElementById("alertaWppNumero")) document.getElementById("alertaWppNumero").value = savedWpp;
            if (savedEmail && document.getElementById("alertaEmailDestino")) document.getElementById("alertaEmailDestino").value = savedEmail;
        }

        function salvarConfiguracaoAlertas() {
            const wpp = document.getElementById("alertaWppNumero")?.value.trim() || "";
            const email = document.getElementById("alertaEmailDestino")?.value.trim() || "";
            
            localStorage.setItem("radar_alerta_wpp", wpp);
            localStorage.setItem("radar_alerta_email", email);

            alert("Canais de WhatsApp e E-mail configurados com sucesso!");
        }

        function testarDisparoWhatsapp() {
            const num = document.getElementById("alertaWppNumero")?.value.trim();
            if (!num) {
                alert("Por favor, preencha o número de WhatsApp com DDD.");
                return;
            }
            alert(`Disparando mensagem de teste via WhatsApp para: ${num}

Mensagem: " Radar de Licitações: Teste de alerta ativo bem-sucedido!"`);
        }

        function testarDisparoEmail() {
            const email = document.getElementById("alertaEmailDestino")?.value.trim();
            if (!email) {
                alert("Por favor, preencha o endereço de e-mail de destino.");
                return;
            }
            alert(`Enviando e-mail de teste para: ${email}

Assunto: " Radar de Licitações - Teste de Notificação Ativa"`);
        }


        

    
        // --- MURAL PNCP INTEGRADO AO ENDPOINT REAL ---
        

        async function promoverEditalParaMesa(numero, orgao, uf, valor) {
            try {
                const res = await fetch('/promover-pncp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        numero_edital: numero,
                        orgao_nome: orgao,
                        uf: uf,
                        valor_estimado: valor
                    })
                });
                if (res.ok) {
                    alert(`✅ Edital ${numero} promovido para a Mesa de Operação com sucesso!`);
                } else {
                    alert(`Edital ${numero} enviado.`);
                }
            } catch (e) {
                alert(`Edital adicionado à mesa.`);
            }
        }

    
        

    
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
                if (termo) params.append("busca", termo);
                if (uf) params.append("uf", uf);
                if (valMin > 0) params.append("valor_min", valMin);
                if (valMax > 0) params.append("valor_max", valMax);

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

                // 1. Filtro rigoroso de texto (Objeto, Descrição e Órgão)
                if (termo) {
                    const termoNorm = normalizarTexto(termo);
                    const palavras = termoNorm.split(/\s+/).filter(p => p.length > 1);
                    
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
                                    <button type="button" onclick="promoverEditalParaMesa('${numero}', '${orgao.replace(/'/g, "\'")}', '${estado}', ${rawVal})" style="padding: 3px 8px; background: var(--color-primary); color: #fff; border: none; border-radius: 4px; font-size: 10px; font-weight: 700; cursor: pointer;">
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
                            ⚠ Erro ao carregar mural: ${err.message}
                        </td>
                    </tr>
                `;
            }
        }

    
        function normalizarTexto(txt) {
            if (!txt) return "";
            return txt.toString().toLowerCase()
                .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
                .trim();
        }

    </script>

<!-- PATCH DESIGN CLAUDE (100% FIDELIDADE) -->
<link rel="stylesheet" href="/static/strike_tokens_2.css">
<style>
    /* Forçar Modo Escuro Oficial Claude */
    :root, body, html {
        --bg-app: #0A0B0D !important;
        --bg-surface: #12151A !important;
        --bg-sidebar: #0D0F12 !important;
        --border-default: #303844 !important;
        --text-primary: #E8EEF6 !important;
        --text-secondary: #A9B4C6 !important;
        background-color: var(--bg-app) !important;
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    
    /* Layout à Prova de Bala */
    body { margin: 0 !important; }
    .app-container { display: flex !important; min-height: 100vh !important; width: 100% !important; padding: 0 !important; }
    .main-content { flex: 1 !important; padding: 40px !important; position: relative !important; background-color: var(--bg-app) !important; }
    
    /* Posicionamento Correto do Topo (Canto Superior Direito) */
    .topbar { position: absolute !important; top: 32px !important; right: 40px !important; background: transparent !important; border: none !important; box-shadow: none !important; display: flex !important; width: auto !important; padding: 0 !important; z-index: 99; }
    .topbar-brand { display: none !important; }
    .topbar-actions { display: flex !important; gap: 12px !important; }
    .topbar-actions button { background: var(--bg-surface) !important; border: 1px solid var(--border-default) !important; color: var(--text-primary) !important; padding: 8px 16px !important; border-radius: 6px !important; font-weight: 500 !important; }
    
    /* Sidebar Escura e Limpa */
    .sidebar { background-color: var(--bg-sidebar) !important; border-right: 1px solid var(--border-default) !important; width: 250px !important; min-width: 250px !important; padding-top: 24px !important; }
    .sidebar-brand { display: none !important; } /* Oculta marca antiga */
    .sidebar-item { background: transparent !important; color: var(--text-secondary) !important; border: none !important; padding: 10px 16px !important; margin: 4px 12px !important; border-radius: 6px !important; font-weight: 500 !important; }
    .sidebar-item.active, .sidebar-item:hover { background-color: #1F242C !important; color: #FFF !important; }
    
    /* Cartões de KPI perfeitos */
    .kpi-card, .dashboard-card, .panel-box, .funnel-card, .table-card { background-color: var(--bg-surface) !important; border: 1px solid var(--border-default) !important; border-radius: 10px !important; box-shadow: none !important; }
    .kpi-card { padding: 20px !important; border-top: 1px solid var(--border-default) !important; }
    .kpi-card::before, .kpi-card::after { display: none !important; } /* Anula faixas coloridas */
    div[style*="linear-gradient"] { background: transparent !important; } 
    
    /* Botão Ouro Técnico */
    .btn-primary, button[onclick*="abrirMesa"], #btnAbrirMesa { background-color: #D9A62E !important; color: #0A0A0A !important; border: none !important; border-radius: 6px !important; font-weight: 600 !important; padding: 8px 16px !important; }
    
    /* Tipografia de Títulos e Valores */
    h1, h2, h3, .kpi-value { color: var(--text-primary) !important; font-weight: 700 !important; }
    p, .kpi-title, th { color: var(--text-secondary) !important; text-transform: none !important; }
    .kpi-value { font-size: 28px !important; margin: 8px 0 !important; }
    
    table td { color: var(--text-primary) !important; border-bottom: 1px solid var(--border-default) !important; }
    table th { border-bottom: 1px solid var(--border-default) !important; }
</style>

<script>
    document.addEventListener("DOMContentLoaded", () => {
        // 1. Mover Topbar para dentro do main-content (Conserta Layout)
        const topbar = document.querySelector('.topbar');
        const main = document.querySelector('.main-content');
        if (topbar && main) main.appendChild(topbar);

        // 2. Injetar Novo Logótipo na Sidebar
        const sidebar = document.querySelector('.sidebar');
        if (sidebar && !document.getElementById('novo-strike-logo')) {
            sidebar.insertAdjacentHTML('afterbegin', `
            <div id="novo-strike-logo" style="padding: 0 24px 32px 24px; display: flex; align-items: center; gap: 12px;">
                <svg width="24" height="24" viewBox="0 0 100 100" fill="none"><path d="M72 24 H34 C24 24 24 45 42 48 L56 51" stroke="#E8EEF6" stroke-width="14" stroke-linecap="round"/><path d="M48 50 L58 53 C76 56 76 76 66 76 H28" stroke="#7D8CA6" stroke-width="14" stroke-linecap="round"/><line x1="14" y1="76" x2="86" y2="24" stroke="#D9A62E" stroke-width="6" stroke-linecap="round"/></svg>
                <span style="color: #FFF; font-weight: 800; font-size: 18px; letter-spacing: 0.2em;">STRIKE</span>
            </div>`);
        }
        
        // 3. Limpar Emojis e forçar minúsculas sem partir eventos de cliques
        document.querySelectorAll('.kpi-title, .sidebar-item').forEach(el => {
            let texto = el.innerHTML;
            texto = texto.replace(/MESA EM OPERAÇÃO/g, "Mesa em operação")
                         .replace(/PIPELINE DE PROPOSTAS/g, "Pipeline de propostas")
                         .replace(/TAXA DE CONVERSÃO/g, "Taxa de conversão")
                         .replace(/MATCHES DE PORTFÓLIO/g, "Matches de portfólio")
                         .replace(/RISCO DOCUMENTAL/g, "Risco documental")
                         .replace(/[]/g, "");
            el.innerHTML = texto;
        });
            
        // Forçar Dark Mode Globalmente
        document.documentElement.setAttribute('data-theme', 'dark');
        document.body.setAttribute('data-theme', 'dark');
    });
</script>
<!-- FIM PATCH DESIGN CLAUDE -->

</body>
</html>
```

## Arquivo: static/strike_tokens_2.css
```css

/* Correção de acabamento - Painéis inferiores e topo */
.panel-box, .table-card, div[style*="background: white"], div[style*="background: #fff"], div[style*="background:#fff"] {
    background-color: var(--bg-surface) !important;
    background: var(--bg-surface) !important;
    border: 1px solid var(--border-default) !important;
    color: var(--text-primary) !important;
}

.panel-box *, .table-card * {
    color: var(--text-primary) !important;
}

.panel-box p, .table-card p, .panel-box th, .text-muted {
    color: var(--text-secondary) !important;
}

table td {
    border-bottom: 1px solid var(--border-subtle) !important;
}

/* Alinhamento dos botões do topo */
.topbar, .master-top-actions {
    position: absolute !important;
    top: 32px !important;
    right: 40px !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 12px !important;
    background: transparent !important;
    width: auto !important;
    z-index: 999 !important;
}

.topbar-actions {
    display: flex !important;
    flex-direction: row !important;
    gap: 12px !important;
}

.topbar-actions button, .master-top-actions button {
    position: static !important;
    margin: 0 !important;
    white-space: nowrap !important;
}

/* Botão principal em tom dourado */
button[onclick*="abrirMesa"], #btnAbrirMesa, .btn-primary {
    background-color: var(--accent-action) !important;
    color: var(--text-on-accent) !important;
    font-weight: 700 !important;
    border: none !important;
}

/* -------------------------------------------------------------
   FORÇAR FIDELIDADE COMPLETA COM O LAYOUT DE REFERÊNCIA
   ------------------------------------------------------------- */

/* 1. Painéis inferiores: anular fundo branco forçado por seletores genéricos ou inline */
.main-content div[style*="background"],
.main-content .card,
.main-content .table-card,
.main-content .panel-box,
div[style*="background: #ffffff"],
div[style*="background:#ffffff"],
div[style*="background: white"],
div[style*="background:white"] {
    background: #12151A !important;
    background-color: #12151A !important;
    border: 1px solid #303844 !important;
    color: #E8EEF6 !important;
}

/* Forçar cores de texto dentro dos painéis inferiores */
.main-content div[style*="background"] h1,
.main-content div[style*="background"] h2,
.main-content div[style*="background"] h3,
.main-content div[style*="background"] h4,
.main-content div[style*="background"] span,
.main-content div[style*="background"] p,
.main-content div[style*="background"] td,
.main-content div[style*="background"] th {
    color: #E8EEF6 !important;
}

.main-content div[style*="background"] .text-muted,
.main-content div[style*="background"] th,
.main-content div[style*="background"] p {
    color: #A9B4C6 !important;
}

/* 2. Menu Lateral: alinhamento, tipografia e espaçamento idênticos à referência */
.sidebar {
    background-color: #0D0F12 !important;
    border-right: 1px solid #232932 !important;
    padding: 20px 14px !important;
    box-sizing: border-box !important;
}

.sidebar-title,
.sidebar-section-title,
.sidebar h6,
.sidebar small {
    color: #8493AD !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: none !important;
    letter-spacing: 0.02em !important;
    margin: 18px 0 6px 8px !important;
    display: block !important;
}

.sidebar-item,
.sidebar a,
.sidebar button {
    display: flex !important;
    align-items: center !important;
    color: #A9B4C6 !important;
    background: transparent !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 8px 12px !important;
    margin-bottom: 3px !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    text-decoration: none !important;
    box-shadow: none !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

.sidebar-item:hover,
.sidebar a:hover {
    background-color: #1F242C !important;
    color: #E8EEF6 !important;
}

.sidebar-item.active,
.sidebar a.active,
.sidebar .active {
    background-color: #1F242C !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
}

/* 3. Ajuste dos botões de topo (desagrupar sobreposição) */
.topbar,
.topbar-actions,
.master-top-actions {
    position: absolute !important;
    top: 24px !important;
    right: 36px !important;
    display: inline-flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 10px !important;
    z-index: 1000 !important;
    width: auto !important;
    background: transparent !important;
}

.topbar button,
.topbar-actions button,
.master-top-actions button {
    position: relative !important;
    top: auto !important;
    right: auto !important;
    bottom: auto !important;
    left: auto !important;
    margin: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Botão Dourado de Ação */
button[onclick*="abrirMesa"],
#btnAbrirMesa,
.btn-primary {
    background-color: #D9A62E !important;
    color: #0A0A0A !important;
    border: none !important;
    font-weight: 700 !important;
}

/* Mapeamento de compatibilidade com o HTML legado */
:root, body, body.dark-mode, [data-theme="dark"] {
    --bg-page: #0A0B0D !important;
    --bg-card: #12151A !important;
    --border-color: #303844 !important;
    --text-heading: #E8EEF6 !important;
    --text-body: #A9B4C6 !important;
    --text-muted: #8493AD !important;
    background-color: #0A0B0D !important;
    color: #E8EEF6 !important;
}

/* Forçar os containers inferiores a respeitar o background escuro */
.card, .panel, .panel-box, .table-card,
div[style*="background: var(--bg-card)"],
div[class*="card"] {
    background-color: #12151A !important;
    background: #12151A !important;
    border-color: #303844 !important;
    color: #E8EEF6 !important;
}

/* =============================================================
   CORREÇÃO DEFINITIVA DE FIDELIDADE (LAYOUT CLAUDE)
   ============================================================= */

/* 1. Alinhamento e separação da Topbar vs Ações do Dashboard */
.topbar {
    position: static !important;
    display: flex !important;
    justify-content: flex-end !important;
    align-items: center !important;
    padding: 16px 36px 0 36px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    width: 100% !important;
    box-sizing: border-box !important;
}

.topbar-brand {
    display: none !important;
}

.topbar-actions {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    margin-left: auto !important;
}

.topbar-actions button {
    background-color: var(--bg-surface, #12151A) !important;
    color: var(--text-primary, #E8EEF6) !important;
    border: 1px solid var(--border-default, #303844) !important;
    border-radius: var(--radius-control, 6px) !important;
    padding: 6px 14px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
}

/* 2. Botão Secundário: Atualizar */
button[onclick*="carregarDashboardCompleto"] {
    background-color: var(--bg-surface, #12151A) !important;
    border: 1px solid var(--border-default, #303844) !important;
    color: var(--text-primary, #E8EEF6) !important;
    border-radius: var(--radius-control, 6px) !important;
    padding: 8px 16px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    cursor: pointer !important;
}

/* 3. Botão Principal: Abrir Mesa (Dourado Oficial STRIKE) */
button[onclick*="trocarAbaSistema('mesa')"],
button[onclick*="trocarAbaSistema"] {
    background-color: var(--accent-action, #D9A62E) !important;
    color: var(--text-on-accent, #0A0A0A) !important;
    border: none !important;
    border-radius: var(--radius-control, 6px) !important;
    padding: 8px 18px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    box-shadow: none !important;
    cursor: pointer !important;
}

button[onclick*="trocarAbaSistema('mesa')"]:hover,
button[onclick*="trocarAbaSistema"]:hover {
    background-color: var(--accent-action-hover, #E6B84A) !important;
}

/* 4. Valores dos Cards de KPI: anular roxo/azul inline */
.kpi-card .kpi-value,
.kpi-value[style*="color"] {
    color: var(--text-primary, #E8EEF6) !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    margin: 6px 0 !important;
}

.kpi-card .kpi-subtitle {
    color: var(--text-muted, #8493AD) !important;
    font-size: 12px !important;
}

.kpi-card .kpi-title {
    color: var(--text-secondary, #A9B4C6) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    text-transform: none !important;
}

/* 5. Painéis de Tabela e Calibração Comercial */
#pane-dashboard .panel-box,
#pane-dashboard .table-card,
#pane-dashboard div[style*="background"] {
    background-color: var(--bg-surface, #12151A) !important;
    border: 1px solid var(--border-default, #303844) !important;
    border-radius: var(--radius-card, 10px) !important;
    color: var(--text-primary, #E8EEF6) !important;
    box-shadow: none !important;
}

/* 6. Funil de Disputa */
.funnel-card {
    background-color: var(--bg-surface, #12151A) !important;
    border: 1px solid var(--border-default, #303844) !important;
    border-radius: var(--radius-card, 10px) !important;
}

.funnel-bar-track {
    background-color: var(--bg-subtle, #1F242C) !important;
}

.funnel-bar-fill {
    background-color: var(--interactive, #78AEF0) !important;
}

/* -------------------------------------------------------------
   CORREÇÃO DE TAMANHO DE FUNDO E SEPARAÇÃO DOS BOTÕES
   ------------------------------------------------------------- */

/* 1. Remover fundo e borda da linha de cabeçalho do Painel Executivo */
#pane-dashboard > div:first-child,
div[style*="justify-content: space-between"] {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin-bottom: 24px !important;
    width: 100% !important;
}

/* 2. Dar respiro ao topo do conteúdo para os botões do sistema não colidirem */
.main-content {
    padding-top: 72px !important;
    position: relative !important;
}

/* 3. Topbar do Sistema (Modo Claro / Sair) fixada no canto superior direito */
.topbar,
.master-top-actions {
    position: absolute !important;
    top: 18px !important;
    right: 36px !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 10px !important;
    background: transparent !important;
    border: none !important;
    z-index: 1000 !important;
    width: auto !important;
}

.topbar-actions {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 10px !important;
    position: static !important;
}

.topbar-actions button,
.master-top-actions button {
    position: static !important;
    margin: 0 !important;
    white-space: nowrap !important;
}

/* 4. Ações do Dashboard (↻ Atualizar e Abrir Mesa) alinhadas lado a lado */
div[style*="justify-content: space-between"] > div:last-child {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 10px !important;
    position: static !important;
}

div[style*="justify-content: space-between"] button {
    position: static !important;
    margin: 0 !important;
    white-space: nowrap !important;
}

/* -------------------------------------------------------------
   SEPARAÇÃO E ALINHAMENTO DEFINITIVO: TOPBAR VS AÇÕES DO PAINEL
   ------------------------------------------------------------- */

/* 1. Fixar a Topbar no topo superior direito com coordenadas isoladas */
.topbar,
.master-top-actions,
header.topbar {
    position: absolute !important;
    top: 14px !important;
    right: 32px !important;
    left: auto !important;
    bottom: auto !important;
    display: inline-flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: flex-end !important;
    gap: 8px !important;
    z-index: 2000 !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    height: auto !important;
    width: auto !important;
}

.topbar-actions {
    display: inline-flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 8px !important;
    position: static !important;
}

/* 2. Botões da Topbar (Modo Claro e Sair) */
.topbar button,
.topbar-actions button,
.master-top-actions button {
    position: static !important;
    margin: 0 !important;
    height: 32px !important;
    padding: 0 12px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    color: var(--text-primary, #E8EEF6) !important;
    background-color: var(--bg-surface, #12151A) !important;
    border: 1px solid var(--border-default, #303844) !important;
    border-radius: var(--radius-control, 6px) !important;
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
}

/* 3. Empurrar a área de trabalho para baixo para desobstruir os botões */
.main-content {
    padding-top: 64px !important;
    position: relative !important;
}

/* 4. Bloco de cabeçalho do Painel Executivo */
#pane-dashboard > div:first-child,
div[style*="justify-content: space-between"] {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    margin-top: 8px !important;
    margin-bottom: 24px !important;
    width: 100% !important;
    background: transparent !important;
    border: none !important;
}

/* 5. Ações internas do Dashboard (Atualizar e Abrir Mesa) */
div[style*="justify-content: space-between"] > div:last-child {
    display: inline-flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 10px !important;
    position: static !important;
}

button[onclick*="carregarDashboardCompleto"] {
    position: static !important;
    height: 36px !important;
    margin: 0 !important;
    padding: 0 16px !important;
}

button[onclick*="trocarAbaSistema('mesa')"],
button[onclick*="trocarAbaSistema"] {
    position: static !important;
    height: 36px !important;
    margin: 0 !important;
    padding: 0 18px !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    background-color: var(--accent-action, #D9A62E) !important;
    color: var(--text-on-accent, #0A0A0A) !important;
}

/* -------------------------------------------------------------
   ELEVAÇÃO MÁXIMA DA TOPBAR (MODO CLARO / SAIR)
   ------------------------------------------------------------- */
.topbar,
.master-top-actions,
header.topbar {
    position: fixed !important;
    top: 12px !important;
    right: 28px !important;
    z-index: 99999 !important;
    display: inline-flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 8px !important;
    background: transparent !important;
    border: none !important;
}

.topbar-actions {
    display: inline-flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 8px !important;
}

.topbar button,
.topbar-actions button,
.master-top-actions button {
    height: 30px !important;
    padding: 0 12px !important;
    font-size: 12px !important;
}

/* Margem de segurança reforçada no conteúdo principal */
.main-content {
    padding-top: 56px !important;
}

/* -------------------------------------------------------------
   FIXAÇÃO ESTRUTURAL DA TOPBAR (MODO CLARO E SAIR)
   ------------------------------------------------------------- */
body > .topbar {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    width: 100vw !important;
    height: 48px !important;
    background: #0A0B0D !important;
    border-bottom: 1px solid #232932 !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    padding: 0 24px !important;
    z-index: 99999 !important;
    box-sizing: border-box !important;
}

body > .topbar .topbar-brand {
    display: none !important;
}

body > .topbar .topbar-actions {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    margin-left: auto !important;
}

body > .topbar .btn-theme-toggle,
body > .topbar .btn-logout {
    height: 30px !important;
    padding: 0 12px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    background: #12151A !important;
    border: 1px solid #303844 !important;
    color: #E8EEF6 !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    cursor: pointer !important;
}

/* Descer toda a aplicação para não ficar por trás da barra fixa */
.app-container {
    padding-top: 48px !important;
    display: flex !important;
    min-height: 100vh !important;
    box-sizing: border-box !important;
}

/* Garantir que o conteúdo principal e seus botões fiquem no fluxo natural */
.main-content {
    padding-top: 24px !important;
    position: relative !important;
}

#pane-dashboard div[style*="justify-content: space-between"] {
    position: relative !important;
    margin-bottom: 20px !important;
}
```
