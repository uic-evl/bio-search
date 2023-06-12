import express from 'express'
import cors from 'cors'
import passport from 'passport'
import fs from 'fs'
import https from 'https'
import bodyParser from 'body-parser'
import {
  registerLocalStrategy,
  loginLocalStrategy,
  jwtStrategy,
} from './utils/auth'
import errorHandler from './utils/error-middleware'
import getRouter from './routes/index'
import {validateEnv} from './utils/utils'

try {
  validateEnv()
} catch (error) {
  console.log(error)
  process.exit()
}

let app = express()
app.use(cors())
app.use(bodyParser.json())

app.use(passport.initialize())
passport.use('register', registerLocalStrategy)
passport.use('login', loginLocalStrategy)
passport.use('jwt', jwtStrategy)

const router = getRouter(passport)
app.use('/api', router)
app.use(errorHandler)

let credentials = null
let httpsServer = null
if (process.env.HTTPS === 'true') {
  const privateKey = fs.readFileSync(process.env.PK, 'utf8')
  const certificate = fs.readFileSync(process.env.CRT, 'utf8')
  credentials = {key: privateKey, cert: certificate}
  httpsServer = https.createServer(credentials, app)
}

const expressServer = httpsServer ? httpsServer : app
const port = process.env.PORT
expressServer.listen(port, () => {
  console.log(`starting server on port ${port} in ${process.env.NODE_ENV} mode`)
})
