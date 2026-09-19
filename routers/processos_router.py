from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from services.processo_service import (
    promover_edital_pncp,
    cadastrar_processo_manual,
    listar_processos_operacao,
    obter_detalhes_processo,
    salvar_proposta_processo,
    registrar_resultado_processo,
    descartar_processo
)

router = APIRouter(prefix="/api/mesa", tags=["Mesa de Operação ERP"])

class ProcessoPromoverSchema(BaseModel):
    numero_edital: str
    orgao_nome: str
    uf: Optional[str] = "BR"
    objeto: str
    segmento: Optional[str] = "MEDICAMENTOS"
    valor_estimado: Optional[float] = 0.0
    data_abertura: Optional[str] = ""
    link_edital: Optional[str] = ""

class ProcessoManualSchema(BaseModel):
    numero_edital: str
    orgao_nome: str
    uf: Optional[str] = "BR"
    objeto: str
    segmento: Optional[str] = "MEDICAMENTOS"
    valor_estimado: Optional[float] = 0.0
    data_abertura: Optional[str] = ""
    link_edital: Optional[str] = ""
    notas: Optional[str] = ""

class PropostaItemSchema(BaseModel):
    nome: str
    quantidade: float
    unidade: Optional[str] = "UN"
    custo_unitario: float
    preco_proposta_unitario: float
    codigo_cmed: Optional[str] = None

class SalvarPropostaSchema(BaseModel):
    itens: List[PropostaItemSchema]
    valor_total_proposta: float
    lance_minimo: float
    notas: Optional[str] = ""

class RegistrarResultadoSchema(BaseModel):
    resultado: str # GANHOU, PERDEU, CANCELADO
    motivo_perda: Optional[str] = ""
    notas: Optional[str] = ""

@router.post("/promover-pncp")
async def promover_pncp_endpoint(dados: ProcessoPromoverSchema):
    return promover_edital_pncp(dados.dict())

@router.post("/cadastrar-manual")
async def cadastrar_manual_endpoint(dados: ProcessoManualSchema):
    return cadastrar_processo_manual(dados.dict())

@router.get("/processos")
async def listar_processos_endpoint(status: Optional[str] = Query(None)):
    return listar_processos_operacao(status)

@router.get("/processos/{processo_id}")
async def detalhes_processo_endpoint(processo_id: int):
    proc = obter_detalhes_processo(processo_id)
    if not proc:
        raise HTTPException(status_code=404, detail="Processo não encontrado.")
    return proc

@router.post("/processos/{processo_id}/proposta")
async def salvar_proposta_endpoint(processo_id: int, dados: SalvarPropostaSchema):
    ok = salvar_proposta_processo(
        processo_id=processo_id,
        itens_com_custo=[i.dict() for i in dados.itens],
        valor_total_proposta=dados.valor_total_proposta,
        lance_minimo=dados.lance_minimo,
        notas=dados.notas or ""
    )
    return {"sucesso": ok, "mensagem": "Proposta registrada! Processo movido para [Em Análise]."}

@router.post("/processos/{processo_id}/resultado")
async def registrar_resultado_endpoint(processo_id: int, dados: RegistrarResultadoSchema):
    ok = registrar_resultado_processo(processo_id, dados.resultado, dados.motivo_perda or "", dados.notas or "")
    return {"sucesso": ok, "mensagem": f"Resultado registrado: {dados.resultado}."}

@router.delete("/processos/{processo_id}")
async def descartar_processo_endpoint(processo_id: int):
    ok = descartar_processo(processo_id)
    return {"sucesso": ok, "mensagem": "Edital descartado."}
