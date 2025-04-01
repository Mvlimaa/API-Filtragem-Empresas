from fastapi import FastAPI, Query
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from fastapi.responses import JSONResponse
from datetime import date

app = FastAPI()

# Função para conectar com o banco de dados.


def get_db_connection():
    conn = psycopg2.connect(
        dbname="Scripts",
        user="postgres",
        password="98280900",
        host="localhost",
        port="5432"
    )
    return conn

# Modelo de entrada de dados.


class Operadora(BaseModel):
    registro_ans: str
    cnpj: str
    razao_social: str
    nome_fantasia: str
    modalidade: str
    logradouro: str
    numero: str
    complemento: Optional[str] = None
    bairro: str
    cidade: str
    uf: str
    cep: str
    ddd: str
    telefone: str
    fax: Optional[str] = None
    endereco_eletronico: Optional[str] = None
    representante: str
    cargo_representante: str
    regiao_de_comercializacao: str
    data_registro_ans: str

# Endpoint para buscar operadoras e Filtrar apenas por cnpj e razao_social


@app.get("/api/operadoras", response_model=List[Operadora])
async def buscar_operadoras(cnpj: Optional[str] = None, razao_social: Optional[str] = None):
    if not cnpj and not razao_social:
        return JSONResponse(status_code=400, content={"message": "É necessário passar CNPJ ou Razão Social como parâmetro"})

    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = "SELECT * FROM operadoras WHERE "
    conditions = []
    params = []

    if cnpj:
        conditions.append("cnpj = %s")
        params.append(cnpj)
    if razao_social:
        conditions.append("razao_social ILIKE %s")
        params.append(f"%{razao_social}%")

    query += " AND ".join(conditions)
    cursor.execute(query, params)

    operadoras = cursor.fetchall()

    cursor.close()
    conn.close()

    for operadora in operadoras:
        operadora['registro_ans'] = str(operadora['registro_ans'])

        if isinstance(operadora['data_registro_ans'], date):
            operadora['data_registro_ans'] = operadora['data_registro_ans'].isoformat()

    return operadoras
