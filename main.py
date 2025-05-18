from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import openai
import os
import uuid

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cliente OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Progresso do jogador por sessao_id
progresso = {}  # {sessao_id: {'etapa': int, 'enigma_resolvido': bool}}

# Enigma do universo 1 - Reflexivo
ENIGMA = (
    "Você encontra um espelho partido em dois.\n"
    "Um lado reflete quem você é, e diz: 'Eu sou quem você realmente é.'\n"
    "O outro lado mostra quem você poderia ter sido, e diz: 'Eu sou quem você escolheu não ser.'\n"
    "Qual espelho você atravessa: o que afirma sua verdade ou o que representa sua negação?"
)
RESPOSTAS_VALIDAS_ENIGMA = ["verdade", "realidade", "negação", "escolha", "possibilidade"]

# Modelos
class Consulta(BaseModel):
    mensagem: str
    sessao_id: str

@app.post("/consultar")
async def consultar_oraculo(dados: Consulta):
    print(f"\n[Requisição de {dados.sessao_id}] {dados.mensagem}")

    # Inicializa progresso da sessão se for novo jogador
    if dados.sessao_id not in progresso:
        progresso[dados.sessao_id] = {"etapa": 1, "enigma_resolvido": False}
    etapa = progresso[dados.sessao_id]["etapa"]

    # Etapa do enigma
    if etapa >= 9 and not progresso[dados.sessao_id]["enigma_resolvido"]:
        if any(palavra in dados.mensagem.lower() for palavra in RESPOSTAS_VALIDAS_ENIGMA):
            progresso[dados.sessao_id]["enigma_resolvido"] = True
            return {
                "resposta": "\U0001f300 Você encarou a verdade. O espelho se desfaz... e o próximo universo se revela."
            }
        else:
            return {
                "resposta": "\u2753 O espelho não reage. Você precisa escolher: atravessar a verdade ou a negação?\n\n" + ENIGMA
            }

    # Define tipo de interação com base na etapa
    tipo = "livre"
    if etapa in [2, 5]:
        tipo = "direcionada"
    elif etapa in [3, 6, 8]:
        tipo = "reflexiva"

    if tipo == "direcionada":
        conteudo_sistema = (
            "Você é um oráculo enigmático. Sempre que o tipo de interação for 'direcionada',"
            " ofereça três caminhos distintos para o jogador, como por exemplo: 'Deseja seguir pela floresta, explorar a torre ou conversar com a sombra?'."
            " Cada caminho deve ser simbólico e misterioso. Aguarde uma palavra-chave como resposta."
        )
    elif tipo == "reflexiva":
        conteudo_sistema = (
            "Você é um oráculo enigmático que provoca reflexões morais e emocionais profundas."
            " Proponha uma afirmação filosófica ao jogador e aguarde uma reação curta como 'sim', 'não' ou 'não sei'."
        )
    else:
        conteudo_sistema = "Você é um oráculo enigmático que guia o jogador através do Véu. Responda com profundidade, mistério e elegância."

    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": conteudo_sistema},
                {"role": "user", "content": dados.mensagem}
            ]
        )
        conteudo = resposta.choices[0].message.content
        progresso[dados.sessao_id]["etapa"] += 1
        print(f"[Resposta ao {dados.sessao_id}] Tipo: {tipo} | Etapa: {progresso[dados.sessao_id]['etapa']}\n{conteudo}")
        return {"resposta": conteudo}

    except Exception as e:
        print(f"❌ Erro ao consultar Oráculo: {e}")
        return {"erro": str(e)}

@app.get("/")
async def index():
    return FileResponse("frontend/game.html")

app.mount("/static", StaticFiles(directory="frontend"), name="static")
