import {
  LoginPage,
  LoginPageProps,
} from '@search-publications-and-figures/common-ui'

export function UnauthenticatedApp({login, message, title}: LoginPageProps) {
  return <LoginPage login={login} message={message} title={title} />
}

export default UnauthenticatedApp
