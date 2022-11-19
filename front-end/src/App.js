import {useState, useEffect} from 'react'
import AuthenticatedApp from './pages/auth/AuthenticatedApp'
import {login, logout, getToken, me} from './api/index'
import UnauthenticatedApp from './pages/auth/UnauthenticatedApp'

const GXD = ({user, login, logout, message}) => {
  if (user) {
    return <AuthenticatedApp user={user} logout={logout} />
  } else {
    return <UnauthenticatedApp login={login} message={message} />
  }
}

function App() {
  const [user, setUser] = useState(null)
  const [authenticated, setAuthenticated] = useState(false)
  const [authMessage, setAuthMessage] = useState('')

  const loginUser = async (username, password) => {
    const {user, message} = await login(username, password)
    if (user) setAuthenticated(true)
    else setAuthMessage(message)
  }

  const logoutUser = async () => {
    logout()
    setUser(null)
    setAuthenticated(false)
  }

  useEffect(() => {
    const getUser = async () => {
      const token = await getToken()
      if (token) {
        const response = await me(token)
        if (response) {
          setUser(response.user)
        }
      }
    }
    getUser()
  }, [authenticated])

  return (
    <GXD
      user={user}
      login={loginUser}
      logout={logoutUser}
      message={authMessage}
    />
  )
}

export default App
