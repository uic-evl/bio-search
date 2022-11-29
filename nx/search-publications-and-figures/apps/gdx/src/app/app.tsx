import {useState, useEffect} from 'react'
import {ChakraProvider} from '@chakra-ui/react'
import AuthenticatedApp from '../pages/authenticated-app/authenticated-app'
import UnauthenticatedApp from '../pages/unauthenticated-app/unauthenticated-app'
import {login, logout, getToken, me} from '../api'
import theme from '../theme'

interface User {
  username: string
  token: string
}

export function App() {
  const [user, setUser] = useState<User | null>(null)
  const [authenticated, setAuthenticated] = useState(false)
  const [authMessage, setAuthMessage] = useState('')

  const loginUser = async (username: string, password: string) => {
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
          setUser({username: response.username, token: response.token})
        }
      }
    }
    getUser()
  }, [authenticated])

  return (
    <>
      <ChakraProvider theme={theme}>
        {user && <AuthenticatedApp user={user} logout={logoutUser} />}
        {!user && (
          <UnauthenticatedApp
            login={loginUser}
            message={authMessage}
            title="GDX Search"
          />
        )}
      </ChakraProvider>
    </>
  )
}

export default App
