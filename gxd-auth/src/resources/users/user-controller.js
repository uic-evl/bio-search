import passport from 'passport'
import jwt from 'jsonwebtoken'
import jwtSecret from '../../utils/jwtConfig.js'

export const registerUser = (req, res, next) => {
  passport.authenticate('register', (err, user, info) => {
    if (err) return res.status(500).send(err)
    if (info) return res.status(400).send(info)

    return res.status(200).send({
      username: user.username,
      password: '######',
    })
  })(req, res, next)
}

/** Login user and create token for 7 days */
export const login = (req, res, next) => {
  passport.authenticate('login', (err, user, info) => {
    if (err) res.status(500).send(err)
    else if (info) {
      res.status(200).send({
        username: null,
        message: info.message,
      })
    } else {
      const token = jwt.sign(
        {
          sub: user.username,
          iat: new Date().getTime(),
          exp: Math.floor(Date.now() / 1000) + 60 * 60 * 7,
        },
        jwtSecret.secret,
      )
      res.status(200).send({
        username: user.username,
        token,
      })
    }
  })(req, res, next)
}

export const me = (req, res, next) => {
  passport.authenticate('jwt', (err, user, info) => {
    if (err) return res.status(500).send(err)
    if (info) return res.status(400).send(info)

    const {authorization} = req.headers
    const token = authorization.replace('Bearer ', '')

    return res.status(200).send({
      username: user.username,
      token,
    })
  })(req, res, next)
}
