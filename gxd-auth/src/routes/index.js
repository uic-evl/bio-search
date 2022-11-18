import express, {Router} from 'express'
import * as userController from '../resources/users/user-controller.js'

const getRouter = passport => {
  const auth = passport.authenticate('jwt', {session: false})

  const router = express.Router()
  router.post('/users/register', userController.registerUser)
  router.post('/users/login', userController.login)
  router.get('/users/me', auth, userController.me)

  return router
}

export default getRouter
