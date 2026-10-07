# ecommerce-api-legacy

LMS API com checkout, em Node.js/Express, refatorada para MVC pela skill `refactor-arch`.

## Como rodar

```powershell
cd ecommerce-api-legacy
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`, e os caminhos reais estão em api.http. O SQLite é em memória e o seed roda antes do `listen`. Exemplos em `api.http`. Variáveis opcionais em `.env.example`.
