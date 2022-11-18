import {Fragment} from 'react'
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom'
import SearchOldPage from './pages/search/SearchOldPage'
import SearchPage from './pages/search/SearchPage'
import {SearchPageWide} from './pages/search/SearchPageWide'

function App() {
  return (
    <Router>
      <Fragment>
        <Routes>
          <Route path="/biosearch" element={<SearchPageWide />}></Route>
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

export default App
