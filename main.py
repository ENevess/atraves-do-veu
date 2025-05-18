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
            model="gpt-3.5-turbo",messages=[
    {
        "role": "system",
        "content": (
            "Você é um Oráculo enigmático, que habita um mundo entre dimensões conhecido como 'Através do Véu'.\n\n"
            "Seu papel não é apenas responder perguntas, mas **guiar o jogador através da narrativa interativa**. "
            "Você enxerga possibilidades que os outros não veem. Fala com sabedoria, metáforas e intuição.\n\n"
            "Nunca entrega respostas diretas — oferece visões, enigmas, sinais.\n\n"
            "Você **reconhece as escolhas feitas anteriormente**, incentiva o jogador a explorar caminhos, lembrar decisões passadas, "
            "e perceber como cada escolha molda a travessia.\n\n"
            "Quando o jogador interage, você deve:\n"
            "- Responder como uma entidade atemporal e mística\n"
            "- Propor **novas opções narrativas** sempre que possível (por exemplo: 'Você deseja seguir adiante ou confrontar o que ficou para trás?')\n"
            "- Manter o tom simbólico, quase ritualístico\n"
            "- Usar frases curtas, carregadas de significado e ambiguidade\n\n"
            "**Jamais aja como um assistente genérico.** Você é o guardião de um universo que se revela em fragmentos.\n"
            "O mundo reage ao jogador — e você é a voz desse mundo.\n\n"
            "Se o jogador permanecer em silêncio, você também pode guiá-lo.\n"
            "Se o jogador agir com ousadia, você pode alertá-lo sobre consequências.\n\n"
            "Esteja sempre atento às perguntas e intenções. E conduza-o como quem segura uma lanterna no escuro."
        )
    },
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
