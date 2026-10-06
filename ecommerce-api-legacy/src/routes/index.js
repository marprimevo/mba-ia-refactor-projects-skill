const express = require("express");
const { checkout } = require("../controllers/checkoutController");
const { financialReport } = require("../controllers/reportController");
const { deleteUser } = require("../controllers/userController");
const { asyncHandler } = require("../middlewares/errorHandler");

const router = express.Router();

router.post("/api/checkout", asyncHandler(checkout));
router.get("/api/admin/financial-report", asyncHandler(financialReport));
router.delete("/api/users/:id", asyncHandler(deleteUser));

module.exports = router;
