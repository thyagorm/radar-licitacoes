import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime

DB_FILE = "database.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_alerts_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_alerts_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_email TEXT UNIQUE,
            whatsapp_telefone TEXT,
            ativo BOOLEAN DEFAULT 1,
            ufs TEXT DEFAULT '',
            palavras_chave TEXT DEFAULT '',
            valor_minimo REAL DEFAULT 0.0,
            horario_digest TEXT DEFAULT '07:00',
            data_atualizacao TEXT
        )
    """)
    conn.commit()
    conn.close()

def salvar_config_alertas(
    usuario_email: str,
    whatsapp_telefone: str,
    ufs: str,
    palavras_chave: str,
    valor_minimo: float = 0.0,
    ativo: bool = True
) -> bool:
    init_alerts_db()
    conn = get_conn()
    cursor = conn.cursor()
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    cursor.execute("""
        INSERT INTO user_alerts_config (
            usuario_email, whatsapp_telefone, ativo, ufs, palavras_chave, valor_minimo, data_atualizacao
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(usuario_email) DO UPDATE SET
            whatsapp_telefone = excluded.whatsapp_telefone,
            ativo = excluded.ativo,
            ufs = excluded.ufs,
            palavras_chave = excluded.palavras_chave,
            valor_minimo = excluded.valor_minimo,
            data_atualizacao = excluded.data_atualizacao
    """, (usuario_email, whatsapp_telefone, 1 if ativo else 0, ufs.upper(), palavras_chave.lower(), valor_minimo, agora))

    conn.commit()
    conn.close()
    return True

def obter_config_alertas(usuario_email: str) -> Optional[Dict[str, Any]]:
    init_alerts_db()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_alerts_config WHERE usuario_email = ?", (usuario_email,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def filtrar_oportunidades_para_usuario(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    conn = get_conn()
    cursor = conn.cursor()
    
    query = "SELECT * FROM licitacoes_pncp WHERE 1=1"
    params = []

    val_min = config.get("valor_minimo") or 0.0
    if val_min > 0:
        query += " AND valor_estimado >= ?"
        params.append(val_min)

    ufs_str = config.get("ufs") or ""
    ufs_lista = [u.strip().upper() for u in ufs_str.split(",") if u.strip()]
    if ufs_lista:
        placeholders = ",".join(["?"] * len(ufs_lista))
        query += f" AND uf IN ({placeholders})"
        params.extend(ufs_lista)

    query += " ORDER BY valor_estimado DESC LIMIT 50"
    cursor.execute(query, params)
    todos = [dict(r) for r in cursor.fetchall()]
    conn.close()

    palavras_str = config.get("palavras_chave") or ""
    palavras = [p.strip().lower() for p in palavras_str.split(",") if p.strip()]

    if not palavras:
        return todos[:6]

    filtrados = []
    for ed in todos:
        obj_lower = (ed.get("objeto") or "").lower()
        if any(p in obj_lower for p in palavras):
            filtrados.append(ed)

    return filtrados

def formatar_mensagem_whatsapp(oportunidades: List[Dict[str, Any]], nome_usuario: str = "Parceiro") -> str:
    hoje = datetime.now().strftime("%d/%m/%Y")
    total = len(oportunidades)
    
    if total == 0:
        return (
            f"🔔 *Radar de Editais | {hoje}*\n\n"
            f"Olá, {nome_usuario}!\n"
            f"Não foram encontradas novas licitações no seu perfil nas últimas 24 horas."
        )

    # Concordância gramatical adequada
    texto_total = "1 nova oportunidade selecionada" if total == 1 else f"{total} novas oportunidades selecionadas"

    msg = f"🎯 *Radar de Editais | {hoje}*\n"
    msg += f"Olá! Encontramos *{texto_total}* para o seu negócio:\n\n"

    for i, op in enumerate(oportunidades[:4], 1):
        val = op.get('valor_estimado', 0)
        val_fmt = f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if val > 0 else "Não informado"
        
        orgao = (op.get('orgao_nome') or 'Órgão Licitante').strip()
        if len(orgao) > 42:
            orgao = orgao[:40].rstrip() + "..."

        edital = op.get('numero_edital') or 'Pregão'
        uf = op.get('uf') or 'BR'
        
        abertura = op.get('data_abertura_proposta', '')[:10]
        if abertura and "-" in abertura:
            abertura = "/".join(reversed(abertura.split("-")))
        else:
            abertura = "A definir"

        # Truncamento sem cortar palavras pela metade
        obj = (op.get('objeto') or '').strip()
        if len(obj) > 130:
            obj_cortado = obj[:130]
            ultimo_espaco = obj_cortado.rfind(" ")
            obj = obj_cortado[:ultimo_espaco] + "..." if ultimo_espaco != -1 else obj_cortado + "..."

        link = op.get('link_origem') or op.get('link_pncp') or 'https://pncp.gov.br'

        msg += f"*{i}. [{uf}] {orgao}*\n"
        msg += f"📋 *Edital:* {edital} | 💰 *Valor:* {val_fmt}\n"
        msg += f"🗓️ *Abertura:* {abertura}\n"
        msg += f"📝 *Objeto:* {obj}\n"
        msg += f"🔗 *Acessar edital:* {link}\n\n"

    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    msg += "⚙️ _Acesse o painel do radar para conferir a listagem completa._"
    return msg

def formatar_email_html(oportunidades: List[Dict[str, Any]], usuario_email: str) -> str:
    hoje = datetime.now().strftime("%d/%m/%Y")
    total = len(oportunidades)
    titulo_oportunidades = "1 nova oportunidade encontrada" if total == 1 else f"{total} novas oportunidades encontradas"

    linhas_tabela = ""
    for op in oportunidades:
        val = op.get('valor_estimado', 0)
        val_fmt = f"R$ {val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if val > 0 else "Não informado"
        
        abertura = op.get('data_abertura_proposta', '')[:10]
        if abertura and "-" in abertura:
            abertura = "/".join(reversed(abertura.split("-")))
        else:
            abertura = "A definir"
            
        link = op.get('link_origem') or op.get('link_pncp') or 'https://pncp.gov.br'

        linhas_tabela += f"""
        <tr style="border-bottom: 1px solid #edf2f7;">
            <td style="padding: 12px; text-align: center;"><span style="background: #2b6cb0; color: #ffffff; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{op.get('uf', 'BR')}</span></td>
            <td style="padding: 12px; font-size: 13px; color: #2d3748;"><strong>{op.get('orgao_nome', '')}</strong></td>
            <td style="padding: 12px; font-size: 12px; color: #4a5568;">{op.get('numero_edital', '-')}</td>
            <td style="padding: 12px; font-size: 13px; font-weight: bold; color: #276749; white-space: nowrap;">{val_fmt}</td>
            <td style="padding: 12px; font-size: 12px; color: #4a5568; line-height: 1.4;">{op.get('objeto', '')[:150]}...</td>
            <td style="padding: 12px; font-size: 12px; text-align: center; white-space: nowrap;">{abertura}</td>
            <td style="padding: 12px; text-align: center;">
                <a href="{link}" target="_blank" style="background: #2b6cb0; color: #ffffff; text-decoration: none; padding: 6px 12px; border-radius: 4px; font-size: 11px; font-weight: bold; display: inline-block;">Ver Edital</a>
            </td>
        </tr>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f7fafc; padding: 20px; margin: 0;">
        <div style="max-width: 860px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; overflow: hidden;">
            <div style="background-color: #1a202c; padding: 22px 24px; color: #ffffff;">
                <h2 style="margin: 0 0 6px 0; font-size: 20px; color: #63b3ed;">🎯 Radar de Editais & Licitações</h2>
                <p style="margin: 0; font-size: 13px; color: #cbd5e0;">Relatório Diário de Oportunidades • {hoje}</p>
            </div>
            
            <div style="padding: 24px;">
                <p style="font-size: 14px; color: #4a5568; margin-top: 0;">
                    Olá, <strong>{usuario_email}</strong>. Identificamos <strong>{titulo_oportunidades}</strong> aderentes aos seus filtros de monitoramento:
                </p>
                
                <table style="width: 100%; border-collapse: collapse; text-align: left; margin-top: 15px;">
                    <thead>
                        <tr style="background-color: #edf2f7; border-bottom: 2px solid #cbd5e0; font-size: 11px; text-transform: uppercase; color: #4a5568;">
                            <th style="padding: 10px; text-align: center;">UF</th>
                            <th style="padding: 10px;">Órgão Licitante</th>
                            <th style="padding: 10px;">Edital</th>
                            <th style="padding: 10px;">Estimado</th>
                            <th style="padding: 10px;">Objeto</th>
                            <th style="padding: 10px; text-align: center;">Abertura</th>
                            <th style="padding: 10px; text-align: center;">Ação</th>
                        </tr>
                    </thead>
                    <tbody>
                        {linhas_tabela if linhas_tabela else '<tr><td colspan="7" style="text-align: center; padding: 25px; color: #a0aec0;">Nenhum edital encontrado hoje com os critérios configurados.</td></tr>'}
                    </tbody>
                </table>
            </div>

            <div style="background-color: #edf2f7; padding: 16px 24px; text-align: center; font-size: 12px; color: #718096; border-top: 1px solid #e2e8f0;">
                Relatório gerado automaticamente pelo seu <strong>Radar de Editais</strong>. Para ajustar filtros, acesse o painel.
            </div>
        </div>
    </body>
    </html>
    """
    return html
