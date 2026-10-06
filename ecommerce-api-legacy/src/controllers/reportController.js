const { all } = require("../models/db");

async function financialReport(req, res) {
    const rows = await all(
        req.app.locals.db,
        `
        SELECT c.id, c.title AS course,
               u.name AS student,
               e.id AS enrollment_id,
               COALESCE(p.amount, 0) AS paid,
               p.status AS payment_status
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u ON u.id = e.user_id
        LEFT JOIN payments p ON p.enrollment_id = e.id
        ORDER BY c.id, e.id
        `
    );

    const report = [];
    const byCourse = new Map();
    for (const row of rows) {
        if (!byCourse.has(row.id)) {
            const item = { course: row.course, revenue: 0, students: [] };
            byCourse.set(row.id, item);
            report.push(item);
        }
        if (!row.enrollment_id) {
            continue;
        }
        const item = byCourse.get(row.id);
        if (row.payment_status === "PAID") {
            item.revenue += row.paid;
        }
        item.students.push({
            student: row.student || "Unknown",
            paid: row.paid || 0,
        });
    }

    res.json(report);
}

module.exports = { financialReport };
