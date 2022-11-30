import passport from 'passport'
import jwt from 'jsonwebtoken'
import {Request, Response, NextFunction} from 'express'

type User = {
  username: string
  password: string
}

export const registerUser = (
  req: Request,
  res: Response,
  next: NextFunction,
) => {
  passport.authenticate('register', (err, user: User, info) => {
    if (err) return res.status(500).send(err)
    if (info) return res.status(400).send(info)

    return res.status(200).send({
      username: user.username,
      password: user.password,
    })
  })(req, res, next)
}

/** Login user and create token for 7 days */
export const login = (req: Request, res: Response, next: NextFunction) => {
  passport.authenticate('login', (err, user: User, info) => {
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
        process.env.SECRET,
      )
      res.status(200).send({
        username: user.username,
        token,
      })
    }
  })(req, res, next)
}

export const me = (req: Request, res: Response, next: NextFunction) => {
  passport.authenticate('jwt', (err, user: User, info) => {
    if (err) return res.status(500).send(err)
    if (info) return res.status(400).send(info)

    const {authorization} = req.headers
    if (authorization) {
      const token = authorization.replace('Bearer ', '')

      return res.status(200).send({
        username: user.username,
        token,
      })
    } else {
      return res.status(200).send({
        username: user.username,
        token: null,
        message: 'request is missing authorization headers',
      })
    }
  })(req, res, next)
}
