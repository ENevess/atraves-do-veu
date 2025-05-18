from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import openai
import os
import httpx

app = FastAPI()

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente httpx sem proxy (resolve conflitos no Render)
transport = httpx.HTTPTransport(proxy=None)
http_client = httpx.Client(transport=transport)

# Cliente da OpenAI com a nova sintaxe
client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=http_client
)

# Modelo de entrada
class Consulta(BaseModel):
    mensagem: str

# Endpoint da API do Oráculo
@app.post("/consultar")
async def consultar_oraculo(dados: Consulta):
    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um oráculo enigmático."},
                {"role": "user", "content": dados.mensagem}
            ]
        )
        return {"resposta": resposta.choices[0].message.content}
    except Exception as e:
        return {"erro": str(e)}

# Servir a interface HTML
@app.get("/")
async def index():
    return FileResponse("frontend/game.html")

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="frontend"), name="static")
