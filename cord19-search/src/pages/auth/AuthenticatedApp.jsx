import {Fragment} from 'react'
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom'
import SearchOldPage from '../search/SearchOldPage'
import SearchPage from '../search/SearchPage'
import {SearchPageWide} from '../search/SearchPageWide'

const AuthenticatedApp = ({user, logout}) => {
  return (
    <Router basename="/cord19-search">
      <Fragment>
        <Routes>
          <Route path="/" element={<SearchPageWide logout={logout} />}></Route>
          <Route
            path="/biosearch/oldsearch"
            element={<SearchOldPage />}
          ></Route>
          <Route
            path="/biosearch/searchpanels"
            element={<SearchPage />}
          ></Route>
        </Routes>
      </Fragment>
    </Router>
  )
}

export default AuthenticatedApp
