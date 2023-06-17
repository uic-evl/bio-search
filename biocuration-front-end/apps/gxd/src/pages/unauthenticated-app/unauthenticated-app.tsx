import {LoginPage, LoginPageProps} from '@biocuration-front-end/common-ui'

export function UnauthenticatedApp({login, message, title}: LoginPageProps) {
  return <LoginPage login={login} message={message} title={title} />
}

export default UnauthenticatedApp
