# task-manager-api

API de Task Manager em Python/Flask. A skill `refactor-arch` manteve `models/`, `routes/` e `services/`, acrescentou `controllers/`, `config/` e `middlewares/`, e tirou a regra de negócio das rotas.

## Como rodar

Na raiz do repositório:

```powershell
.\.venv\Scripts\Activate.ps1
cd task-manager-api
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. Login de exemplo: `joao@email.com` / `1234`. Variáveis opcionais em `.env.example`.
