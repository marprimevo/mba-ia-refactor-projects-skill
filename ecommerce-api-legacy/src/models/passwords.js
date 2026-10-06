const crypto = require("crypto");

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString("hex");
    const digest = crypto.scryptSync(String(password), salt, 32).toString("hex");
    return salt + "$" + digest;
}

module.exports = { hashPassword };
