
# Através do Véu – MVP

## Como rodar localmente

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Abra http://localhost:8000 no navegador.

## Como publicar no Railway

1. Suba o projeto no GitHub.
2. Vá em https://railway.app > New Project > Deploy from GitHub.
3. Adicione a variável `OPENAI_API_KEY`.
4. Railway usará o Procfile para iniciar a aplicação.

## Estrutura

- `frontend/`: Interface narrativa (game.html, oraculo.js, audio).
- `backend/`: API FastAPI para comunicação com o Oráculo.
