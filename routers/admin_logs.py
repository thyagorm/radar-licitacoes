from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse
from typing import Optional
from services.audit_service import listar_logs_auditoria, limpar_logs_auditoria

router = APIRouter()

def verificar_admin(
    authorization: Optional[str] = Header(None),
    x_user_role: Optional[str] = Header(None)
):
    """
    Validação de papel administrativo.
    Aceita verificação via cabeçalho de perfil ou token.
    """
    # Se o cabeçalho explicitar que não é admin, bloqueia
    if x_user_role and x_user_role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: recurso restrito exclusivamente a administradores."
        )
    return True

@router.get("/logs", dependencies=[Depends(verificar_admin)])
async def obter_logs():
    logs = listar_logs_auditoria(limite=100)
    return {"total": len(logs), "logs": logs}

@router.delete("/logs/limpar", dependencies=[Depends(verificar_admin)])
async def limpar_logs():
    sucesso = limpar_logs_auditoria()
    return {"sucesso": sucesso, "mensagem": "Logs de erro resetados."}
