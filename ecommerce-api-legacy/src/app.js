const express = require("express");
const settings = require("./config/settings");
const { open, init } = require("./models/db");
const routes = require("./routes");
const { errorHandler } = require("./middlewares/errorHandler");

async function main() {
    const app = express();
    app.use(express.json());

    const db = open();
    await init(db);
    app.locals.db = db;

    app.use(routes);
    app.use(errorHandler);

    app.listen(settings.port, () => {
        console.log("Frankenstein LMS rodando na porta " + settings.port + "...");
    });
}

main().catch((err) => {
    console.error(err);
    process.exit(1);
});
