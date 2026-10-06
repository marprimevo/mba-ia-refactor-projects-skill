# code-smells-project

API de E-commerce em Python/Flask, refatorada para MVC pela skill `refactor-arch`.

## Como rodar

Na raiz do repositório:

```powershell
.\.venv\Scripts\Activate.ps1
cd code-smells-project
python app.py
```

A aplicação sobe em `http://localhost:5000`. O SQLite (`loja.db`) é criado no primeiro boot, com produtos e usuários de exemplo. Senhas do seed: `admin123`, `123456`, `senha123`.

Variáveis opcionais estão em `.env.example`.
