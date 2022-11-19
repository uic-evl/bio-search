// Based on Kent C Doods tutorials

function errorMiddleware(error, req, res, next) {
  if (res.headersSent) {
    next(error)
  } else {
    res.status(500)
    res.json({
      message: error.message,
      // we only add a `stack` property in non-production environments
      ...(process.env.NODE_ENV === 'production' ? null : {stack: error.stack}),
    })
  }
}

export default errorMiddleware
