from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, constr
from datetime import datetime
from typing import Optional
from enum import Enum
from uuid import uuid4


app = FastAPI()

class tiposAtendimentos(Enum):
    Normal = 'N'
    Prioritário = 'P'

class filaRequest(BaseModel):
    nomeCliente: Optional[constr(max_length=20)]
    tipoAtendimento: tiposAtendimentos

class filaResponse(BaseModel):
    id: str
    posicao: Optional[int] = None
    nomeCliente: Optional[constr(max_length=20)]
    dataChegada: datetime = datetime.now()

class Fila(BaseModel):
    id: str
    posicao: Optional[int]
    nomeCliente: Optional[constr(max_length=20)]
    dataChegada: Optional[datetime] = datetime.now()
    tipoAtendimento: tiposAtendimentos
    atendido: bool = False

db_Atendimentos = []



@app.get('/fila')
def getFILA():
    fila = [cliente for cliente in db_Atendimentos if cliente.atendido == False]
    fila.sort(key=lambda cliente: cliente.posicao)
    if len(fila) == 0:
        return {}
    return {"fila": fila}   
    

@app.get('/fila/{id}')
def busca_cliente_fila(id: str):
    cliente = [cliente for cliente in db_Atendimentos if cliente.id == id]
    if len(cliente) == 0 :
        raise HTTPException(404, 'Cliente não localizado.')
    return {"cliente": cliente}
    
    

@app.post("/fila")
def insereFila(cliente: filaRequest):

    proxPosicao = 1
    maiorPosicao = max(db_Atendimentos, key=lambda cliente: cliente.posicao, default=None)
    if maiorPosicao != None:
        proxPosicao = maiorPosicao.posicao + 1

    clienteFila = Fila(
        id = str(uuid4()),
        posicao=proxPosicao,
        nomeCliente=cliente.nomeCliente,
        tipoAtendimento=cliente.tipoAtendimento
    )

    db_Atendimentos.append(clienteFila)
    return clienteFila


@app.put("/fila")
def atualizaFila():
    fila = [cliente for cliente in db_Atendimentos if cliente.atendido == False]
    if len(fila) == 0 :
        return {"mensagem": "Fila vazia!"}

    for cliente in db_Atendimentos:
        if cliente.posicao == 1:
            cliente.atendido = True
        if cliente.posicao != 0:
            cliente.posicao -= 1

    return {"mensagem": "Fila atualizada com sucesso!", "fila": db_Atendimentos}

@app.delete("/fila/{id}")
def removerFila(id : str):
    cliente = [cliente for cliente in db_Atendimentos if cliente.id == id]

    if len(cliente) == 0:
        raise HTTPException(404, "Cliente não encontrado(a).")

    indexCliente = db_Atendimentos.index(cliente[0])

    db_Atendimentos.remove(cliente[0])

    for index, cliente in enumerate(db_Atendimentos, start = indexCliente):
        if index > indexCliente:
            if cliente.posicao == 1:
                cliente.atendido = True
            if cliente.posicao != 0:
                cliente.posicao -= 1

    return {"mensagem": "Cliente retirado da fila com sucesso!"}
