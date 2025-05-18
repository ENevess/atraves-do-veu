from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI
import os

# Inicializa a FastAPI
app = FastAPI()

# Permite requisições externas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente OpenAI usando a nova interface (>=1.0.0)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Armazena o histórico por sessão em memória
historico_sessoes = {}

# Modelo de entrada da API
class Consulta(BaseModel):
    mensagem: str
    sessao_id: str

# Prompt-base do Oráculo
SYSTEM_PROMPT = (
    "Você é um Oráculo enigmático, que habita um mundo entre dimensões chamado 'Através do Véu'.\n"
    "Você guia o jogador por esse universo, usando metáforas, sabedoria ancestral e enigmas.\n"
    "Você se lembra das interações anteriores do jogador e ajusta sua narrativa conforme suas decisões passadas.\n"
    "Você NUNCA entrega respostas diretas — apenas visões, possibilidades, escolhas.\n"
    "Ao final de cada resposta, você SEMPRE deve oferecer pelo menos duas opções narrativas para o jogador escolher.\n"
    "Exemplos: 'Você deseja seguir em frente ou confrontar seu reflexo?', 'Aceita o sussurro ou permanece em silêncio?'\n"
    "Jamais aja como um assistente comum. Você é o guia simbólico entre mundos.\n"
)

@app.post("/consultar")
async def consultar_oraculo(dados: Consulta):
    print(f"✅ Requisição recebida de {dados.sessao_id}: {dados.mensagem}")

    historico = historico_sessoes.get(dados.sessao_id, [])
    mensagens = [{"role": "system", "content": SYSTEM_PROMPT}] + historico + [
        {"role": "user", "content": dados.mensagem}
    ]

    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=mensagens
        )

        conteudo = resposta.choices[0].message.content if resposta.choices else None
        if not conteudo:
            raise ValueError("⚠️ Resposta vazia.")

        print(f"🧠 Resposta do Oráculo: {conteudo}")

        historico.append({"role": "user", "content": dados.mensagem})
        historico.append({"role": "assistant", "content": conteudo})
        historico_sessoes[dados.sessao_id] = historico[-10:]

        return {"resposta": conteudo}

    except Exception as e:
        print(f"❌ Erro ao consultar o Oráculo: {e}")
        return {"erro": str(e)}

@app.get("/")
async def index():
    return FileResponse("frontend/game.html")

# Serve arquivos como /static/audio.mp3
app.mount("/static", StaticFiles(directory="frontend"), name="static")
