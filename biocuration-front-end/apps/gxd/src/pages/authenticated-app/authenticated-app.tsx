import {BrowserRouter as Router, Routes, Route} from 'react-router-dom'
import Search from '../search/search'
import {IndividualRelevancePage} from '../experiments/individual-relevance'
import {SearchRelevancePage} from '../experiments/search-relevance'

interface User {
  username: string
  token: string
}

/* eslint-disable-next-line */
export interface AuthenticatedAppProps {
  user: User
  logout: () => void
}

export function AuthenticatedApp({user, logout}: AuthenticatedAppProps) {
  return (
    <Router basename={process.env.NX_BASE_PATH}>
      <Routes>
        <Route
          path="/individual"
          element={<IndividualRelevancePage token={user.token} />}
        />
        <Route
          path="/search-relevance"
          element={
            <SearchRelevancePage authToken={user.token} logout={logout} />
          }
        />
        <Route path="/" element={<Search logout={logout} />}></Route>
      </Routes>
    </Router>
  )
}

export default AuthenticatedApp
