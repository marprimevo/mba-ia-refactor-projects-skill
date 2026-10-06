function asyncHandler(fn) {
    return function wrapped(req, res, next) {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
}

function errorHandler(err, req, res, next) {
    if (res.headersSent) {
        next(err);
        return;
    }
    const status = err.status || 500;
    if (status >= 500) {
        console.error(err);
        res.status(500).send("Erro interno");
        return;
    }
    res.status(status).send(err.message);
}

module.exports = { asyncHandler, errorHandler };
