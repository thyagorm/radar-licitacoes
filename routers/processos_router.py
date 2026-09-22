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

# ==========================================
# ROTAS DE CONTRATOS, ATAS E ITENS
# ==========================================
from services.contrato_service import (
    salvar_itens_processo,
    listar_itens_processo,
    homologar_vitoria_e_criar_contrato,
    registrar_ordem_fornecimento,
    atualizar_entrega_af,
    obter_resumo_contrato
)

class SalvarItensSchema(BaseModel):
    itens: List[Dict[str, Any]]

class HomologarContratoSchema(BaseModel):
    tipo_instrumento: str  # 'ARP' ou 'CONTRATO'
    numero_instrumento: str
    data_inicio_vigencia: str
    data_fim_vigencia: str
    itens_ganhos: List[Dict[str, Any]]
    observacoes: Optional[str] = ""

class RegistrarAFSchema(BaseModel):
    numero_af_empenho: str
    prazo_limite_entrega: str
    itens_af: List[Dict[str, Any]]
    data_emissao: Optional[str] = ""
    observacoes: Optional[str] = ""

class BaixaAFSchema(BaseModel):
    data_entrega_efetiva: str

@router.get("/processos/{processo_id}/itens")
async def obter_itens_processo_endpoint(processo_id: int):
    return listar_itens_processo(processo_id)

@router.post("/processos/{processo_id}/itens")
async def salvar_itens_processo_endpoint(processo_id: int, dados: SalvarItensSchema):
    salvar_itens_processo(processo_id, dados.itens)
    return {"sucesso": True, "mensagem": "Itens atualizados com sucesso!"}

@router.post("/processos/{processo_id}/homologar-contrato")
async def homologar_contrato_endpoint(processo_id: int, dados: HomologarContratoSchema):
    res = homologar_vitoria_e_criar_contrato(
        processo_id=processo_id,
        tipo_instrumento=dados.tipo_instrumento,
        numero_instrumento=dados.numero_instrumento,
        data_inicio_vigencia=dados.data_inicio_vigencia,
        data_fim_vigencia=dados.data_fim_vigencia,
        itens_ganhos=dados.itens_ganhos,
        observacoes=dados.observacoes or ""
    )
    return res

@router.get("/processos/{processo_id}/contrato-resumo")
async def contrato_resumo_endpoint(processo_id: int):
    res = obter_resumo_contrato(processo_id)
    if not res:
        raise HTTPException(status_code=404, detail="Contrato/ARP não encontrado para este processo.")
    return res

@router.post("/contratos/{contrato_id}/ordens-fornecimento")
async def registrar_af_endpoint(contrato_id: int, dados: RegistrarAFSchema):
    return registrar_ordem_fornecimento(
        contrato_id=contrato_id,
        numero_af_empenho=dados.numero_af_empenho,
        prazo_limite_entrega=dados.prazo_limite_entrega,
        itens_af=dados.itens_af,
        data_emissao=dados.data_emissao or "",
        observacoes=dados.observacoes or ""
    )

@router.put("/ordens-fornecimento/{ordem_id}/baixa")
async def baixa_af_endpoint(ordem_id: int, dados: BaixaAFSchema):
    return atualizar_entrega_af(ordem_id, dados.data_entrega_efetiva)


# ========================================================
# ROTAS COMPATÍVEIS COM O FRONTEND LEGADO / DASHBOARD
# ========================================================

@router.get("/processos", include_in_schema=False)
async def listar_processos_mesa_alias(status: Optional[str] = Query(None)):
    return listar_processos_operacao(status)

# Criamos um sub-roteador sem prefixo /api/mesa para mapear /api/processos e /promover-pncp
from fastapi import APIRouter
router_compat = APIRouter(tags=["Compatibilidade Frontend"])

@router_compat.get("/api/processos")
async def api_processos_alias(status: Optional[str] = Query(None)):
    return listar_processos_operacao(status)

@router_compat.post("/api/promover-pncp")
@router_compat.post("/promover-pncp")
async def promover_pncp_alias(dados: ProcessoPromoverSchema):
    return promover_edital_pncp(dados.dict())
