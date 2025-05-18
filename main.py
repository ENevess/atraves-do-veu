from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import openai
import os

app = FastAPI()

# CORS liberado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração da OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Armazena memória temporária por sessão
historico_sessoes = {}

# Modelo da requisição do frontend
class Consulta(BaseModel):
    mensagem: str
    sessao_id: str

# Prompt base do Oráculo
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
    print(f"\n✅ [Sessão: {dados.sessao_id}] Requisição recebida: {dados.mensagem}")

    historico = historico_sessoes.get(dados.sessao_id, [])
    mensagens = [{"role": "system", "content": SYSTEM_PROMPT}] + historico + [
        {"role": "user", "content": dados.mensagem}
    ]

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=mensagens
        )

        print(f"🔵 Resposta bruta da API: {resposta}")

        conteudo = resposta.choices[0].message.content if resposta.choices else None

        if not conteudo:
            raise ValueError("⚠️ Conteúdo da resposta vazio ou malformado.")

        print(f"🧠 [Sessão: {dados.sessao_id}] Resposta do Oráculo: {conteudo}")

        # Atualiza o histórico da sessão
        historico.append({"role": "user", "content": dados.mensagem})
        historico.append({"role": "assistant", "content": conteudo})
        historico_sessoes[dados.sessao_id] = historico[-10:]

        return {"resposta": conteudo}

    except Exception as e:
        print(f"❌ Erro ao consultar a OpenAI: {e}")
        return {"erro": str(e)}

@app.get("/")
async def index():
    return FileResponse("frontend/game.html")

app.mount("/static", StaticFiles(directory="frontend"), name="static")
