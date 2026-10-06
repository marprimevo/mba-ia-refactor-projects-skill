const fs = require("fs");
const path = require("path");

function loadEnvFile() {
    const file = path.join(__dirname, "..", "..", ".env");
    if (!fs.existsSync(file)) {
        return;
    }
    const lines = fs.readFileSync(file, "utf8").split("\n");
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith("#") || !trimmed.includes("=")) {
            continue;
        }
        const index = trimmed.indexOf("=");
        const key = trimmed.slice(0, index).trim();
        const value = trimmed.slice(index + 1).trim();
        if (process.env[key] === undefined) {
            process.env[key] = value;
        }
    }
}

loadEnvFile();

module.exports = {
    port: Number(process.env.PORT || 3000),
    dbUser: process.env.DB_USER || "",
    dbPass: process.env.DB_PASS || "",
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "",
    smtpUser: process.env.SMTP_USER || "",
};
