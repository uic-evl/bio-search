import jwtSecret from './jwtConfig.js'
import bcrypt from 'bcrypt'
import {Strategy as LocalStrategy} from 'passport-local'
import {Strategy as JwtStrategy} from 'passport-jwt'
import {ExtractJwt} from 'passport-jwt'

const BCRYPT_SALT_ROUNDS = 12

const blankMessage = field => `${field} cannot be blank`
const checkUserAttributes = (username, password) => {
  let message = null
  if (!username) return blankMessage(username)
  if (!password) return blankMessage(password)

  return message
}

const registerStrategyOpts = {
  usernameField: 'username',
  passwordField: 'password',
  session: false,
  passReqToCallback: true,
}

const registerLocalStrategy = new LocalStrategy(
  registerStrategyOpts,
  async (req, username, password, done) => {
    try {
      const message = checkUserAttributes(username, password)
      if (message !== null) return done(null, false, {message})

      const hashedPassword = await bcrypt.hash(password, BCRYPT_SALT_ROUNDS)
      const user = {username, password: hashedPassword}
      return done(null, user)
    } catch (err) {
      return done(err)
    }
  },
)

const loginStrategyOpts = {
  usernameField: 'username',
  passwordField: 'password',
  session: false,
}
const loginLocalStrategy = new LocalStrategy(
  loginStrategyOpts,
  async (username, password, done) => {
    try {
      const isUsernameCorrect = username === jwtSecret.curry
      const isPasswordCorrect = await bcrypt.compare(password, jwtSecret.mayo)
      if (isUsernameCorrect && isPasswordCorrect) {
        return done(null, {username, password})
      } else {
        return done(null, false, {message: 'authentication error'})
      }
    } catch (err) {
      return done(err)
    }
  },
)

const jwtStrategyOpts = {
  jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
  secretOrKey: jwtSecret.secret,
}

const jwtStrategy = new JwtStrategy(
  jwtStrategyOpts,
  async (jwtPayload, done) => {
    try {
      if (jwtSecret.curry === jwtPayload.sub)
        done(null, {
          username: jwtPayload.sub,
        })
      else done(null, false)
    } catch (err) {
      done(err)
    }
  },
)

export {registerLocalStrategy, loginLocalStrategy, jwtStrategy}
