var bodyParser = require('body-parser')
var express = require('express')
var logger = require('morgan')
var snake = require('./snake');

var app = express()

app.set('port', 7000)
app.enable('verbose errors')
app.use(logger('dev'))
app.use(bodyParser.json())

// Handle POSTs to start and move
app.post('/start', snake.start);
app.post('/move', snake.move);

app.use('*', function (req, res, next) {
  if (req.url === '/favicon.ico') {
    // Short-circuit favicon requests
    res.set({'Content-Type': 'image/x-icon'})
    res.status(200)
    res.end()
    next()
  } else {
    // Reroute all 404 routes to the 404 handler
    var err = new Error()
    err.status = 404
    next(err)
  }
})

// 404 handler middleware, respond with JSON only
app.use(function (err, req, res, next) {
  if (err.status !== 404) {
    return next(err)
  }

  res.status(404)
  res.send({
    status: 404,
    error: err.message || "These are not the snakes you're looking for"
  })
})

// 500 handler middleware, respond with JSON only
app.use(function (err, req, res, next) {
  var statusCode = err.status || 500

  console.error(err.stack)

  res.status(statusCode)
  res.send({
    status: statusCode,
    error: err
  })
})

var server = app.listen(app.get('port'), function () {
  console.log('Server listening on port %s', app.get('port'))
})
