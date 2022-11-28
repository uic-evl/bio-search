import bcrypt from 'bcrypt'
import {Strategy as LocalStrategy} from 'passport-local'
import {Strategy as JwtStrategy} from 'passport-jwt'
import {ExtractJwt} from 'passport-jwt'
import {JwtPayload} from 'jsonwebtoken'

const BCRYPT_SALT_ROUNDS = 12

const blankMessage = (field: string) => `${field} cannot be blank`
const checkUserAttributes = (username: string, password: string) => {
  if (!username) return blankMessage(username)
  if (!password) return blankMessage(password)

  return null
}

export const registerLocalStrategy = new LocalStrategy(
  async (username: string, password: string, done: any) => {
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
export const loginLocalStrategy = new LocalStrategy(
  loginStrategyOpts,
  async (username: string, password: string, done: any) => {
    try {
      const isUsernameCorrect = username === process.env.CURRYSOUP
      const isPasswordCorrect = await bcrypt.compare(password, process.env.MAYO)
      if (isUsernameCorrect && isPasswordCorrect) {
        return done(null, {username, password})
      } else {
        return done(null, null, {message: 'wrong credentials'})
      }
    } catch (err) {
      return done(err)
    }
  },
)

const jwtStrategyOpts = {
  jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
  secretOrKey: process.env.SECRET,
}

export const jwtStrategy = new JwtStrategy(
  jwtStrategyOpts,
  async (jwtPayload: JwtPayload, done: any) => {
    try {
      if (process.env.CURRYSOUP === jwtPayload.sub)
        done(null, {
          username: jwtPayload.sub,
        })
      else done(null, false)
    } catch (err) {
      done(err)
    }
  },
)
