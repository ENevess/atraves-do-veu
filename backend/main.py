
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import openai
import os

app = FastAPI()
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/oraculo")
async def oraculo(req: Request):
    data = await req.json()
    prompt = data.get("mensagem", "")

    try:
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é o Oráculo, uma entidade enigmática que guia o jogador com mensagens poéticas, misteriosas e provocativas."},
                {"role": "user", "content": prompt}
            ]
        )
        texto = resposta.choices[0].message.content
        return {"resposta": texto}
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})
