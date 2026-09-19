import os
import json
import base64
import traceback
from dotenv import load_dotenv
load_dotenv()

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse

from services.edital_engine import (
    isolar_paginas_tabela,
    extrair_tabela_com_ia,
    enriquecer_com_portfolio,
    gerar_excel_bytes,
    carregar_portfolio,
    ARQUIVO_PORTFOLIO
)
from services.audit_service import registrar_log_erro
from services.edital_storage import (
    salvar_edital_no_disco,
    persistir_edital_analisado,
    alimentar_memoria_equivalencia,
    obter_estatisticas_dashboard,
    listar_ultimos_editais
)
from services.edital_engine import normalizar_texto

router = APIRouter()

@router.get("/dashboard-stats")
async def get_dashboard_stats(usuario_email: str = "usuario_sessao@empresa.com"):
    stats = obter_estatisticas_dashboard()
    recentes = listar_ultimos_editais(limite=10)
    return {
        "stats": stats,
        "recentes": recentes
    }

@router.get("/portfolio-status")
async def get_portfolio_status():
    df = carregar_portfolio()
    total = len(df) if df is not None else 0
    return {
        "total_produtos": total,
        "ativo": df is not None and total > 0,
        "caminho": ARQUIVO_PORTFOLIO,
        "existe_no_disco": os.path.exists(ARQUIVO_PORTFOLIO)
    }

@router.post("/processar-edital")
async def processar_edital(
    arquivo: UploadFile = File(...),
    laboratorios: str = Form(...),
    usuario_email: str = Form(default="usuario_sessao@empresa.com")
):
    try:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            registrar_log_erro(
                usuario_email=usuario_email,
                arquivo_nome=arquivo.filename,
                etapa="CONFIGURACAO",
                tipo_erro="ChaveAusente",
                detalhe_erro="GEMINI_API_KEY não configurada no ambiente."
            )
            return JSONResponse(status_code=400, content={"detail": "GEMINI_API_KEY não configurada no .env."})

        try:
            labs_lista = json.loads(laboratorios)
        except Exception:
            labs_lista = [l.strip() for l in laboratorios.split(",") if l.strip()]

        conteudo_pdf = await arquivo.read()

        # 1. Filtro e isolamento de páginas
        try:
            texto_tabela = isolar_paginas_tabela(conteudo_pdf)
        except Exception as e_pdf:
            registrar_log_erro(
                usuario_email=usuario_email,
                arquivo_nome=arquivo.filename,
                etapa="LEITURA_PDF",
                tipo_erro=type(e_pdf).__name__,
                detalhe_erro=str(e_pdf),
                stack_trace=traceback.format_exc()
            )
            raise e_pdf

        if not texto_tabela.strip():
            registrar_log_erro(
                usuario_email=usuario_email,
                arquivo_nome=arquivo.filename,
                etapa="ISOLAMENTO_TABELA",
                tipo_erro="TextoVazio",
                detalhe_erro="O pré-processador não identificou páginas com termos de tabela/itens no PDF."
            )
            return JSONResponse(status_code=400, content={"detail": "Não foi possível extrair tabelas do PDF."})

        # 2. Extração via IA
        try:
            itens_brutos = extrair_tabela_com_ia(texto_tabela, api_key)
        except Exception as e_ia:
            registrar_log_erro(
                usuario_email=usuario_email,
                arquivo_nome=arquivo.filename,
                etapa="EXTRACAO_IA",
                tipo_erro=type(e_ia).__name__,
                detalhe_erro=str(e_ia),
                stack_trace=traceback.format_exc(),
                payload_debug=texto_tabela[:2000]
            )
            raise e_ia

        if not itens_brutos:
            registrar_log_erro(
                usuario_email=usuario_email,
                arquivo_nome=arquivo.filename,
                etapa="ESTRUTURACAO_ITENS",
                tipo_erro="ItensVazios",
                detalhe_erro="A IA leu o texto das páginas, mas retornou 0 itens farmacêuticos identificados."
            )

        # 3. Cruzamento com o Portfólio
        df_resultado = enriquecer_com_portfolio(itens_brutos, labs_lista)

        if df_resultado.empty:
            registrar_log_erro(
                usuario_email=usuario_email,
                arquivo_nome=arquivo.filename,
                etapa="CRUZAMENTO_PORTFOLIO",
                tipo_erro="SemCorrespondencia",
                detalhe_erro=f"A IA extraiu {len(itens_brutos)} itens, mas nenhum teve correspondência com os laboratórios ativos: {labs_lista}",
                payload_debug=json.dumps(itens_brutos[:10], ensure_ascii=False)
            )
            return JSONResponse({
                "itens": [],
                "total": 0,
                "excel_base64": None,
                "mensagem": "Nenhum medicamento com correspondência no portfólio dos laboratórios selecionados."
            })

        # 4. Geração do arquivo Excel
        # 4. Salva o PDF no disco permanente
        caminho_disco = salvar_edital_no_disco(conteudo_pdf, usuario_email, arquivo.filename)

        # 5. Persiste a análise no Banco de Dados
        persistir_edital_analisado(
            usuario_email=usuario_email,
            nome_arquivo=arquivo.filename,
            caminho_storage=caminho_disco,
            conteudo_pdf=conteudo_pdf,
            total_itens=len(itens_brutos),
            total_matches=len(df_resultado),
            laboratorios=labs_lista,
            resultado_itens=df_resultado.to_dict(orient="records")
        )

        # 6. Alimenta a memória semântica de equivalência (zero tokens em itens futuros)
        alimentar_memoria_equivalencia(itens_brutos, normalizar_texto)

        excel_bytes = gerar_excel_bytes(df_resultado)
        excel_b64 = base64.b64encode(excel_bytes).decode("utf-8")
        itens_tabela = df_resultado.to_dict(orient="records")
        nome_saida = arquivo.filename.replace(".pdf", "") if arquivo.filename else "edital"

        return {
            "itens": itens_tabela,
            "total": len(itens_tabela),
            "excel_base64": excel_b64,
            "nome_arquivo_excel": f"Mapa_Precos_{nome_saida}.xlsx"
        }

    except Exception as e:
        registrar_log_erro(
            usuario_email=usuario_email,
            arquivo_nome=arquivo.filename if arquivo else "desconhecido.pdf",
            etapa="PIPELINE_GERAL",
            tipo_erro=type(e).__name__,
            detalhe_erro=str(e),
            stack_trace=traceback.format_exc()
        )
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"detail": f"Erro interno: {str(e)}"})
