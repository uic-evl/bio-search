import {Router} from 'express'
import * as userController from '../resources/users/user-controller'
import {PassportStatic} from 'passport'

const getRouter = (passport: PassportStatic) => {
  const auth = passport.authenticate('jwt', {session: false})

  const router = Router()
  router.post('/users/register', userController.registerUser)
  router.post('/users/login', userController.login)
  router.get('/users/me', auth, userController.me)

  return router
}

export default getRouter
