import re

with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Substituir o cabeçalho "Radar de Licitações" pelo Monograma e Tipografia STRIKE
logo_strike_svg = """
        <div style="padding: 22px 16px 24px 16px; display: flex; align-items: center; gap: 10px;">
            <svg width="24" height="24" viewBox="0 0 100 100" fill="none" style="flex-shrink: 0;">
                <path d="M72 24 H34 C24 24 24 45 42 48 L56 51" stroke="#E8EEF6" stroke-width="14" stroke-linecap="round"/>
                <path d="M48 50 L58 53 C76 56 76 76 66 76 H28" stroke="#7D8CA6" stroke-width="14" stroke-linecap="round"/>
                <line x1="14" y1="76" x2="86" y2="24" stroke="#D9A62E" stroke-width="6" stroke-linecap="round"/>
            </svg>
            <span style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; font-size: 15px; font-weight: 800; letter-spacing: 0.22em; color: #FFFFFF; line-height: 1;">STRIKE</span>
        </div>
"""

# Substitui o logo do topo na sidebar
pos_radar = html.find("Radar de Licitações")
if pos_radar != -1:
    p_ini = html.rfind("<div", 0, pos_radar)
    p_fim = html.find("</div>", pos_radar) + 6
    html = html[:p_ini] + logo_strike_svg + html[p_fim:]

# 2. Ícones SVG de traço fino para substituir os emojis do menu lateral
svg_icons = {
    "Dashboard": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>',
    "Mural de Editais": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>',
    "Radar de Matches": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>',
    "Mapa de Preços": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>',
    "Mesa de Operação": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>',
    "Alertas": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>',
    "Estratégia": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"></line><line x1="4" y1="10" x2="4" y2="3"></line><line x1="12" y1="21" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="3"></line><line x1="20" y1="21" x2="20" y2="16"></line><line x1="20" y1="12" x2="20" y2="3"></line><line x1="1" y1="14" x2="7" y2="14"></line><line x1="9" y1="8" x2="15" y2="8"></line><line x1="17" y1="16" x2="23" y2="16"></line></svg>',
    "Notificações": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>',
    "Empresa & Certidões": '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><circle cx="12" cy="14" r="2"></circle></svg>'
}

# 3. Limpeza dos emojis das strings no menu
limpezas_menu = [
    ("📊 Dashboard", "Dashboard"),
    ("📜 Mural de Editais (PNCP)", "Mural de Editais (PNCP)"),
    ("🎯 Radar de Matches", "Radar de Matches"),
    ("📊 Mapa de Preços (Excel)", "Mapa de Preços (Excel)"),
    ("💼 Mesa de Operação", "Mesa de Operação"),
    ("🔔 Alertas", "Alertas"),
    ("⚙️ Estratégia & Critérios", "Estratégia e Critérios"),
    ("⚙️ Estratégia e Critérios", "Estratégia e Critérios"),
    ("🔔 Notificações", "Notificações"),
    ("📑 Empresa & Certidões", "Empresa e Certidões")
]
for de, para in limpezas_menu:
    html = html.replace(de, para)

# Injetar os SVGs nos itens da sidebar correspondentes
for nome_item, svg in svg_icons.items():
    padrao = re.compile(rf'(<div[^>]*class="sidebar-item"[^>]*>)\s*<span>\s*(?:<svg[^>]*>.*?</svg>\s*)?({nome_item}[^<]*)</span>', re.IGNORECASE | re.DOTALL)
    html = padrao.sub(rf'\1<span style="display:inline-flex; align-items:center; gap:10px;">{svg} \2</span>', html)

# 4. Folha de estilo de alta fidelidade para equiparar à imagem de referência
css_referencia = """
<style id="strike-visual-match">
    /* Superposição visual conforme a imagem exata do STRIKE */
    :root, [data-theme="dark"], body {
        --bg-app: #0A0B0D !important;
        --bg-surface: #12151A !important;
        --border-default: #303844 !important;
        --border-subtle: #232932 !important;
    }

    body {
        background-color: #0A0B0D !important;
        color: #E8EEF6 !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* Sidebar idêntica à referência */
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
        margin: 18px 12px 6px 12px !important;
    }
    .sidebar-item {
        color: #A9B4C6 !important;
        background: transparent !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
        margin: 2px 8px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    .sidebar-item:hover {
        background-color: #1F242C !important;
        color: #FFFFFF !important;
    }
    .sidebar-item.active {
        background-color: #1F242C !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    .sidebar-item.active::before {
        display: none !important;
    }

    /* Topo: Botões de ação globais */
    .btn-theme-toggle, [onclick*="toggleTheme"], .btn-mode-toggle {
        background: transparent !important;
        color: #E8EEF6 !important;
        border: 1px solid #303844 !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        padding: 6px 12px !important;
    }
    .btn-logout, [onclick*="logout"], [onclick*="sair"] {
        background: transparent !important;
        color: #E8EEF6 !important;
        border: 1px solid #303844 !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        padding: 6px 14px !important;
    }

    /* Botão Primário Dourado "Abrir Mesa" */
    .btn-primary, button.btn-primary, [onclick*="abrirMesa"], #btnAbrirMesa {
        background-color: #D9A62E !important;
        color: #0A0A0A !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        font-size: 13px !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 6px !important;
    }
    .btn-primary:hover, [onclick*="abrirMesa"]:hover {
        background-color: #E6B84A !important;
    }

    /* Botão Secundário "Atualizar" */
    .btn-secondary, button.btn-secondary, [onclick*="carregarDados"], [onclick*="atualizar"] {
        background-color: transparent !important;
        color: #E8EEF6 !important;
        border: 1px solid #303844 !important;
        border-radius: 6px !important;
        padding: 8px 14px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }
    .btn-secondary:hover {
        background-color: #191D24 !important;
        border-color: #667388 !important;
    }

    /* Cartões de KPI e Superfícies Gerais */
    .stat-card, .kpi-card, .dashboard-card,
    div[style*="background: white"], div[style*="background:#fff"], div[style*="background: #fff"] {
        background: #12151A !important;
        background-color: #12151A !important;
        border: 1px solid #303844 !important;
        border-radius: 8px !important;
        color: #E8EEF6 !important;
        box-shadow: none !important;
    }

    .stat-card::before, .kpi-card::before {
        display: none !important;
    }

    /* Tipografia de KPIs e Títulos */
    h1, h2, h3, h4, .page-header h1 {
        color: #FFFFFF !important;
    }
    .page-header p {
        color: #8493AD !important;
    }
    .stat-value, .kpi-value, .stat-number {
        color: #FFFFFF !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        font-variant-numeric: tabular-nums !important;
    }
    .stat-label, .kpi-label {
        color: #8493AD !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        text-transform: none !important;
    }
    .stat-subtext, .kpi-subtext {
        color: #8493AD !important;
        font-size: 11px !important;
    }

    /* Badge Pílula Regular no Risco Documental */
    .badge-regular, span[style*="color: #10b981"], span[style*="color:#10b981"] {
        background: #14261F !important;
        color: #3FBF8F !important;
        border: 1px solid #24503F !important;
        border-radius: 999px !important;
        padding: 2px 8px !important;
        font-size: 11px !important;
        font-weight: 600 !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 4px !important;
    }

    /* Funil de Disputa */
    .funnel-bar-fill, div[style*="background: #6366f1"] {
        background: #5B8DEF !important;
    }

    /* Badge Inteligência */
    .badge-intel, span:contains("Inteligência") {
        background: #14212F !important;
        color: #78AEF0 !important;
        border: 1px solid #24405F !important;
        border-radius: 4px !important;
        font-size: 11px !important;
        padding: 2px 6px !important;
    }

    /* Botão Abrir na tabela de Editais Ativos */
    table button, table .btn-table, table [onclick*="abrir"] {
        background: transparent !important;
        color: #E8EEF6 !important;
        border: 1px solid #303844 !important;
        border-radius: 4px !important;
        padding: 3px 8px !important;
        font-size: 11px !important;
    }
</style>
"""

# Substitui o estilo anterior ou insere antes de </head>
if "strike-visual-match" in html:
    html = re.sub(r'<style id="strike-visual-match">.*?</style>', css_referencia, html, flags=re.DOTALL)
else:
    pos_h = html.find("</head>")
    html = html[:pos_h] + css_referencia + "\n" + html[pos_h:]

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("🚀 static/dashboard.html alinhado diretamente com a imagem de referência!")
