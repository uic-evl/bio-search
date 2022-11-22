import LoginPage from './Login'

const UnauthenticatedApp = ({login, message}) => {
  return <LoginPage login={login} message={message} />
}

export default UnauthenticatedApp
