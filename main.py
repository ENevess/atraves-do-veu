from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import openai
import os

# Inicializa a API FastAPI
app = FastAPI()

# Habilita CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configura a chave da OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Armazena histórico por sessão (na memória)
historico_sessoes = {}

# Modelo da requisição
class Consulta(BaseModel):
    mensagem: str
    sessao_id: str

# Personalidade base do Oráculo
SYSTEM_PROMPT = (
    "Você é um Oráculo enigmático, que habita um mundo entre dimensões chamado 'Através do Véu'.\n"
    "Você guia o jogador por esse universo, usando metáforas, sabedoria ancestral e enigmas.\n"
    "Você se lembra das interações anteriores do jogador e ajusta sua narrativa conforme suas decisões passadas.\n"
    "Você NUNCA entrega respostas diretas — apenas visões, possibilidades, escolhas.\n"
    "Ao final de cada resposta, você SEMPRE deve oferecer pelo menos duas opções narrativas para o jogador escolher.\n"
    "Exemplos: 'Você deseja seguir em frente ou confrontar seu reflexo?', 'Aceita o sussurro ou permanece em silêncio?'\n"
    "Jamais aja como um assistente comum. Você é o guia simbólico entre mundos.\n"
)

# Rota principal para o oráculo
@app.post("/consultar")
async def consultar_oraculo(dados: Consulta):
    print(f"✅ Requisição recebida de {dados.sessao_id}: {dados.mensagem}")

    historico = historico_sessoes.get(dados.sessao_id, [])
    mensagens = [{"role": "system", "content": SYSTEM_PROMPT}] + historico + [
        {"role": "user", "content": dados.mensagem}
    ]

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=mensagens
        )
        conteudo = resposta.choices[0].message.content
        print(f"🧠 Resposta do oráculo: {conteudo}")

        # Atualiza histórico da sessão
        historico.append({"role": "user", "content": dados.mensagem})
        historico.append({"role": "assistant", "content": conteudo})
        historico_sessoes[dados.sessao_id] = historico[-10:]  # Limita para não crescer infinitamente

        return {"resposta": conteudo}

    except Exception as e:
        print(f"❌ Erro na geração da resposta: {e}")
        return {"erro": str(e)}

# Página inicial
@app.get("/")
async def index():
    return FileResponse("frontend/game.html")

# Arquivos estáticos (ex: áudio ambiente)
app.mount("/static", StaticFiles(directory="frontend"), name="static")
