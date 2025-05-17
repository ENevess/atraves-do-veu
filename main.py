from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import openai
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()
app.mount("/", StaticFiles(directory=BASE_DIR, html=True), name="static")

openai.api_key = "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"#os.getenv("OPENAI_API_KEY")

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
