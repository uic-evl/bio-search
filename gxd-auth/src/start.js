import 'dotenv/config'
import express from 'express'
import cors from 'cors'
import passport from 'passport'
import {
  registerLocalStrategy,
  loginLocalStrategy,
  jwtStrategy,
} from './utils/auth.js'
import getRouter from './routes/index.js'
import errorMiddleware from './utils/error-middleware.js'
import bodyParser from 'body-parser'

const startServer = ({port = process.env.PORT} = {}) => {
  let app = express()
  app.use(cors())
  app.use(bodyParser.json())

  app.use(passport.initialize())
  passport.use('register', registerLocalStrategy)
  passport.use('login', loginLocalStrategy)
  passport.use('jwt', jwtStrategy)

  const router = getRouter(passport)
  app.use('/api', router)
  app.use(errorMiddleware)

  return new Promise(resolve => {
    const server = app.listen(port, () => {
      console.log(`starting server on port ${port}`)
      const originalClose = server.close.bind(server)
      server.close = () => {
        return new Promise(resolveClose => {
          originalClose(resolveClose)
        })
      }
    })
    resolve(server)
  })
}

export default startServer
