from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import io
import pandas as pd
from services.preferencias_service import obter_preferencias, salvar_preferencias

router = APIRouter(prefix="/api/preferencias", tags=["Preferências Operacionais"])

class PreferenciasSchema(BaseModel):
    margem_minima: float = 20.0
    margem_alvo: float = 30.0
    imposto_medio: float = 12.0
    ufs_atuacao: List[str] = ["RJ", "SP", "MG"]
    segmentos: List[str] = ["MEDICAMENTOS"]
    valor_minimo: float = 5000.0
    valor_maximo: float = 50000000.0
    palavras_chave: Optional[str] = ""
    blacklist_termos: Optional[str] = ""

@router.get("")
async def get_preferencias_endpoint():
    return {"sucesso": True, "preferencias": obter_preferencias()}

@router.post("")
async def save_preferencias_endpoint(dados: PreferenciasSchema):
    ok = salvar_preferencias(dados.dict())
    return {"sucesso": ok, "mensagem": "Parâmetros e preferências salvos com sucesso!"}

@router.post("/importar-termos-excel")
async def importar_termos_excel(file: UploadFile = File(...)):
    """
    Lê uma planilha Excel (.xlsx, .xls) ou CSV e extrai os termos da coluna relevante.
    """
    nome_arquivo = file.filename.lower()
    conteudo = await file.read()

    try:
        if nome_arquivo.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(conteudo))
        elif nome_arquivo.endswith('.csv'):
            try:
                df = pd.read_csv(io.BytesIO(conteudo), sep=';')
            except Exception:
                df = pd.read_csv(io.BytesIO(conteudo), sep=',')
        else:
            raise HTTPException(status_code=400, detail="Formato inválido. Envie um arquivo .xlsx, .xls ou .csv.")

        if df.empty:
            raise HTTPException(status_code=400, detail="A planilha enviada está vazia.")

        # Procura coluna preferencial
        colunas_possiveis = [
            "produto", "produtos", "principio ativo", "principio_ativo", 
            "item", "itens", "descricao", "descrição", "nome", "termo", "palavra"
        ]
        coluna_escolhida = None
        for col in df.columns:
            if str(col).strip().lower() in colunas_possiveis:
                coluna_escolhida = col
                break

        # Fallback: utiliza a primeira coluna
        if not coluna_escolhida:
            coluna_escolhida = df.columns[0]

        # Extrai valores limpos e sem repetições
        termos_brutos = df[coluna_escolhida].dropna().astype(str).tolist()
        termos_limpos = []
        for t in termos_brutos:
            termo = t.strip()
            if termo and len(termo) > 1 and termo not in termos_limpos:
                termos_limpos.append(termo)

        return {
            "sucesso": True,
            "total_importado": len(termos_limpos),
            "coluna_utilizada": str(coluna_escolhida),
            "termos_texto": ", ".join(termos_limpos)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar planilha: {str(e)}")
