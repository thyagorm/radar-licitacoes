import re

with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. CSS limpo, simétrico e modular para Dark e Light Mode
css_temas = """
<style id="strike-theme-engine">
    /* ================= TOKENS STRIKE (WCAG AA) ================= */
    :root, [data-theme="dark"], body[data-theme="dark"] {
        --bg-app: #0A0B0D;
        --bg-surface: #12151A;
        --bg-elevated: #191D24;
        --bg-subtle: #1F242C;
        --bg-sidebar: #0D0F12;
        --bg-sidebar-active: #1F242C;

        --border-subtle: #232932;
        --border-default: #303844;
        --border-input: #667388;

        --text-primary: #E8EEF6;
        --text-secondary: #A9B4C6;
        --text-muted: #8493AD;
        --text-on-accent: #0A0A0A;
        --text-sidebar: #A9B4C6;
        --text-sidebar-active: #FFFFFF;

        --accent-action: #D9A62E;
        --accent-action-hover: #E6B84A;
        --accent-action-pressed: #BF8F22;
        --interactive: #78AEF0;

        --success-bg: #14261F;
        --success-text: #3FBF8F;
        --success-border: #24503F;

        --funnel-track: #232932;
        --funnel-fill: #5B8DEF;
        --card-shadow: none;
    }

    [data-theme="light"], body[data-theme="light"] {
        --bg-app: #F4F6FA;
        --bg-surface: #FFFFFF;
        --bg-elevated: #FFFFFF;
        --bg-subtle: #EDF1F7;
        --bg-sidebar: #0D0F12; /* Sidebar escura permanente */
        --bg-sidebar-active: #1F242C;

        --border-subtle: #E1E6EE;
        --border-default: #CBD3DF;
        --border-input: #7F8BA0;

        --text-primary: #0F1720;
        --text-secondary: #475467;
        --text-muted: #667085;
        --text-on-accent: #0A0A0A;
        --text-sidebar: #A9B4C6;
        --text-sidebar-active: #FFFFFF;

        --accent-action: #D9A62E;
        --accent-action-hover: #C4931F;
        --accent-action-pressed: #B07F14;
        --interactive: #1D5FB8;

        --success-bg: #E6F5EE;
        --success-text: #0F7B55;
        --success-border: #A7DBC5;

        --funnel-track: #E2E8F0;
        --funnel-fill: #2563EB;
        --card-shadow: 0 1px 3px rgba(15, 23, 32, 0.05);
    }

    /* Estrutura de Fundo e Tipografia */
    body {
        background-color: var(--bg-app) !important;
        color: var(--text-primary) !important;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
        margin: 0 !important;
        transition: background-color 0.2s ease, color 0.2s ease;
    }

    /* Barra Lateral */
    .sidebar {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    .sidebar-section-title {
        color: var(--text-muted) !important;
    }
    .sidebar-item {
        color: var(--text-sidebar) !important;
    }
    .sidebar-item:hover, .sidebar-item.active {
        background-color: var(--bg-sidebar-active) !important;
        color: var(--text-sidebar-active) !important;
    }

    /* Painéis, Cartões de KPI e Superfícies */
    .kpi-card, .stat-card, .card, .dashboard-card, .funnel-card, .table-card,
    div[style*="background: white"], div[style*="background:#fff"], div[style*="background: #fff"],
    div[style*="background: #12151A"] {
        background: var(--bg-surface) !important;
        background-color: var(--bg-surface) !important;
        border: 1px solid var(--border-default) !important;
        border-radius: 8px !important;
        box-shadow: var(--card-shadow) !important;
        transition: background-color 0.2s ease, border-color 0.2s ease;
    }

    /* Títulos e Textos */
    h1, h2, h3, h4, .kpi-value, .stat-value, [style*="color: #FFFFFF"], [style*="color:#fff"] {
        color: var(--text-primary) !important;
    }
    p, .kpi-title, .stat-label, .kpi-subtext, [style*="color: #8493AD"], [style*="color:#64748b"] {
        color: var(--text-secondary) !important;
    }

    /* Funil de Disputa */
    .funnel-bar-track, div[style*="background: #232932"], div[style*="background:#232932"] {
        background-color: var(--funnel-track) !important;
    }
    .funnel-bar-fill, div[style*="background: #5B8DEF"] {
        background-color: var(--funnel-fill) !important;
    }

    /* Badge Regular do Risco Documental */
    .badge-regular, span[style*="color: #10b981"], span[style*="color:#3FBF8F"] {
        background: var(--success-bg) !important;
        color: var(--success-text) !important;
        border: 1px solid var(--success-border) !important;
    }

    /* Botão Primário Dourado ("Abrir Mesa") */
    .btn-primary, button.btn-primary, [onclick*="abrirMesa"], #btnAbrirMesa {
        background-color: var(--accent-action) !important;
        color: var(--text-on-accent) !important;
        font-weight: 700 !important;
        border: none !important;
    }
    .btn-primary:hover, [onclick*="abrirMesa"]:hover {
        background-color: var(--accent-action-hover) !important;
    }

    /* Botões Secundários ("Atualizar", "Modo claro/escuro", "Sair") */
    .btn-secondary, button.btn-secondary, [onclick*="carregarDados"], [onclick*="atualizar"],
    #btnThemeToggle, [onclick*="fazerLogout"] {
        background-color: transparent !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-default) !important;
    }
    .btn-secondary:hover, #btnThemeToggle:hover, [onclick*="fazerLogout"]:hover {
        background-color: var(--bg-subtle) !important;
        border-color: var(--border-input) !important;
    }

    /* Tabelas */
    table th {
        color: var(--text-muted) !important;
        border-bottom: 1px solid var(--border-default) !important;
    }
    table td {
        border-bottom: 1px solid var(--border-subtle) !important;
        color: var(--text-primary) !important;
    }
</style>
"""

# Substitui estilos antigos pelo mecanismo mestre
padrao_estilos = re.compile(r'<style id="(strike-core-theme|strike-exact-ui|strike-exact-override|strike-visual-match|strike-pixel-perfect|strike-master-theme)">.*?</style>', re.DOTALL)
html = padrao_estilos.sub('', html)

pos_head = html.find("</head>")
html = html[:pos_head] + css_temas + "\n" + html[pos_head:]

# 2. Injetar função JS que alterna e persiste o tema (com ícone e texto correspondentes)
script_tema = """
<script id="strike-theme-script">
function alternarTemaVisual() {
    const htmlEl = document.documentElement;
    const bodyEl = document.body;
    const atual = htmlEl.getAttribute("data-theme") || "dark";
    const novo = atual === "dark" ? "light" : "dark";

    htmlEl.setAttribute("data-theme", novo);
    bodyEl.setAttribute("data-theme", novo);
    localStorage.setItem("strike-theme", novo);
    atualizarBotaoTema(novo);
}

function atualizarBotaoTema(tema) {
    const btn = document.getElementById("btnThemeToggle");
    if (!btn) return;
    if (tema === "light") {
        btn.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 5px;">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
            </svg> Modo escuro
        `;
    } else {
        btn.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 5px;">
                <circle cx="12" cy="12" r="5"></circle>
                <line x1="12" y1="1" x2="12" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="23"></line>
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                <line x1="1" y1="12" x2="3" y2="12"></line>
                <line x1="21" y1="12" x2="23" y2="12"></line>
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
            </svg> Modo claro
        `;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const temaSalvo = localStorage.getItem("strike-theme") || "dark";
    document.documentElement.setAttribute("data-theme", temaSalvo);
    document.body.setAttribute("data-theme", temaSalvo);
    atualizarBotaoTema(temaSalvo);
});
</script>
"""

# Inserir ou atualizar script do tema antes de </body>
if "strike-theme-script" in html:
    html = re.sub(r'<script id="strike-theme-script">.*?</script>', script_tema, html, flags=re.DOTALL)
else:
    pos_body = html.rfind("</body>")
    html = html[:pos_body] + script_tema + "\n" + html[pos_body:]

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Sistema de temas perfeitamente unificado com persistência e harmonia total!")
