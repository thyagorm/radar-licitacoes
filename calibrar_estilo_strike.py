with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Garantir que <html> tenha data-theme="dark"
if 'data-theme="dark"' not in html:
    html = html.replace("<html", '<html data-theme="dark"')

# 2. Folha de estilo de alta precisão baseada estritamente na imagem
css_fiel = """
<style id="strike-exact-override">
    /* PALETA OFICIAL STRIKE (MODO ESCURO PERMANENTE) */
    :root, [data-theme="dark"], body {
        --bg-app: #0A0B0D !important;
        --bg-surface: #12151A !important;
        --bg-elevated: #191D24 !important;
        --bg-subtle: #1F242C !important;
        --bg-sidebar: #0D0F12 !important;

        --border-subtle: #232932 !important;
        --border-default: #303844 !important;
        --border-input: #667388 !important;

        --text-primary: #E8EEF6 !important;
        --text-secondary: #A9B4C6 !important;
        --text-muted: #8493AD !important;
        --text-on-accent: #0A0A0A !important;

        --accent-gold: #D9A62E !important;
        --accent-gold-hover: #E6B84A !important;
        --accent-gold-pressed: #BF8F22 !important;
    }

    /* Fundo da Aplicação */
    body {
        background-color: #0A0B0D !important;
        color: #E8EEF6 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* Barra Lateral */
    .sidebar {
        background-color: #0D0F12 !important;
        border-right: 1px solid #232932 !important;
    }
    .sidebar-section-title {
        color: #8493AD !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        text-transform: none !important;
        letter-spacing: normal !important;
        margin: 18px 8px 6px 8px !important;
    }
    .sidebar-item {
        color: #A9B4C6 !important;
        background: transparent !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        margin: 2px 6px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        transition: all 0.15s ease !important;
    }
    .sidebar-item:hover {
        background-color: #1F242C !important;
        color: #E8EEF6 !important;
    }
    .sidebar-item.active {
        background-color: #1F242C !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    .sidebar-item.active::before {
        display: none !important; /* Sem faixas laterais grossas, foco no preenchimento sutil */
    }

    /* Todos os Cards: Superfície #12151A e Borda #303844 */
    .stat-card, .kpi-card, .card, .dashboard-card, 
    div[style*="background: white"], div[style*="background:#fff"], div[style*="background: #fff"],
    div[style*="background: rgb(255, 255, 255)"] {
        background: #12151A !important;
        background-color: #12151A !important;
        border: 1px solid #303844 !important;
        border-radius: 8px !important;
        color: #E8EEF6 !important;
        box-shadow: none !important;
    }

    /* Elimina qualquer faixa decorativa colorida no topo dos cards */
    .stat-card::before, .kpi-card::before {
        display: none !important;
        content: none !important;
    }

    /* Títulos e Rótulos de Cabeçalho */
    h1, h2, h3, h4, .page-header h1, .page-header h2 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    .page-header p, p {
        color: #8493AD !important;
    }

    /* Valores Numéricos dos KPIs */
    .stat-value, .kpi-value, .stat-number, .kpi-big-value {
        color: #FFFFFF !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        font-variant-numeric: tabular-nums !important;
    }
    .stat-label, .kpi-label, .kpi-header {
        color: #8493AD !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        text-transform: none !important;
        letter-spacing: normal !important;
    }
    .stat-subtext, .kpi-subtext {
        color: #8493AD !important;
        font-size: 11px !important;
    }

    /* Badge Regular no Risco Documental */
    .badge-regular, .badge-success, span[style*="background: #e6f4ea"] {
        background: #14261F !important;
        color: #3FBF8F !important;
        border: 1px solid #24503F !important;
        border-radius: 999px !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        padding: 2px 8px !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 4px !important;
    }

    /* Funil de Disputa (Mesa) */
    .funnel-container, div[style*="background: #e2e8f0"], div[style*="background:#e2e8f0"] {
        background: #232932 !important;
        border-radius: 999px !important;
    }
    .funnel-bar-fill, div[style*="background: #6366f1"], div[style*="background: #4f46e5"] {
        background: #5B8DEF !important;
        border-radius: 999px !important;
    }

    /* Botão Primário: "Abrir Mesa" (Ouro Técnico #D9A62E + Texto #0A0A0A) */
    .btn-primary, button.btn-primary, [onclick*="abrirMesa"], a[href*="mesa"], #btnAbrirMesa {
        background: #D9A62E !important;
        background-color: #D9A62E !important;
        color: #0A0A0A !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        cursor: pointer !important;
        transition: background-color 0.15s ease !important;
    }
    .btn-primary:hover, [onclick*="abrirMesa"]:hover {
        background: #E6B84A !important;
        background-color: #E6B84A !important;
    }

    /* Botão Secundário: "Atualizar" / "Modo claro" / "Sair" (Neutro escuro com borda) */
    .btn-secondary, button.btn-secondary, .btn-top-neutral,
    button[onclick*="carregar"], button[onclick*="atualizar"], [onclick*="logout"], [onclick*="toggleTheme"] {
        background: transparent !important;
        color: #E8EEF6 !important;
        border: 1px solid #303844 !important;
        border-radius: 6px !important;
        padding: 7px 13px !important;
        font-weight: 500 !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }
    .btn-secondary:hover, button.btn-secondary:hover {
        background: #191D24 !important;
        border-color: #667388 !important;
    }

    /* Tabelas e Linhas */
    table {
        color: #E8EEF6 !important;
    }
    th {
        color: #8493AD !important;
        border-bottom: 1px solid #303844 !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        text-transform: none !important;
    }
    td {
        border-bottom: 1px solid #232932 !important;
        color: #E8EEF6 !important;
        font-variant-numeric: tabular-nums !important;
    }
    tr:hover td {
        background-color: #1F242C !important;
    }

    /* Botão de Linha "Abrir ↗" */
    table button, table .btn-table, table [onclick*="abrir"] {
        background: transparent !important;
        color: #E8EEF6 !important;
        border: 1px solid #303844 !important;
        border-radius: 4px !important;
        padding: 4px 10px !important;
        font-size: 11px !important;
    }
    table button:hover {
        background: #1F242C !important;
        border-color: #667388 !important;
    }

    /* Bloco "Calibração Comercial" */
    .calibration-empty, div[style*="border: 2px dashed"] {
        border: 1px dashed #303844 !important;
        color: #8493AD !important;
        border-radius: 6px !important;
    }
</style>
"""

# Substituir estilo anterior ou injetar no <head>
if "strike-exact-override" in html:
    import re
    html = re.sub(r'<style id="strike-exact-override">.*?</style>', css_fiel, html, flags=re.DOTALL)
else:
    pos_head = html.find("</head>")
    html = html[:pos_head] + css_fiel + "\n" + html[pos_head:]

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Visual STRIKE calibrado com sucesso conforme a imagem de referência!")
