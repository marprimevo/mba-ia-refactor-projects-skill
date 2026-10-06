const { get, run } = require("../models/db");

async function deleteUser(req, res) {
    const db = req.app.locals.db;
    const id = req.params.id;
    const user = await get(db, "SELECT id FROM users WHERE id = ?", [id]);
    if (!user) {
        res.status(404).send("Usuário não encontrado");
        return;
    }

    await run(
        db,
        "DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)",
        [id]
    );
    await run(db, "DELETE FROM enrollments WHERE user_id = ?", [id]);
    await run(db, "DELETE FROM users WHERE id = ?", [id]);
    res.send("Usuário deletado e registros relacionados removidos.");
}

module.exports = { deleteUser };
