const { get, run } = require("../models/db");
const { hashPassword } = require("../models/passwords");

function badRequest(message) {
    const error = new Error(message);
    error.status = 400;
    error.text = true;
    return error;
}

async function checkout(req, res) {
    const body = req.body || {};
    const name = body.usr;
    const email = body.eml;
    const password = body.pwd;
    const courseId = body.c_id;
    const card = body.card;

    if (!name || !email || !courseId || !card) {
        throw badRequest("Bad Request");
    }

    const db = req.app.locals.db;
    const course = await get(db, "SELECT * FROM courses WHERE id = ? AND active = 1", [courseId]);
    if (!course) {
        res.status(404).send("Curso não encontrado");
        return;
    }

    const existing = await get(db, "SELECT id FROM users WHERE email = ?", [email]);
    let userId = existing && existing.id;
    if (!userId) {
        const created = await run(
            db,
            "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
            [name, email, hashPassword(password || "123456")]
        );
        userId = created.lastID;
    }

    const status = String(card).startsWith("4") ? "PAID" : "DENIED";
    if (status === "DENIED") {
        res.status(400).send("Pagamento recusado");
        return;
    }

    const enrollment = await run(
        db,
        "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
        [userId, courseId]
    );
    await run(
        db,
        "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
        [enrollment.lastID, course.price, status]
    );
    await run(
        db,
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        ["Checkout curso " + courseId + " por " + userId]
    );

    res.status(200).json({ msg: "Sucesso", enrollment_id: enrollment.lastID });
}

module.exports = { checkout };
