import {Fragment} from 'react'
import {BrowserRouter as Router, Routes, Route} from 'react-router-dom'
import SearchOldPage from './pages/search/SearchOldPage'
import SearchPage from './pages/search/SearchPage'

function App() {
  return (
    <Router>
      <Fragment>
        <Routes>
          <Route path="/biosearch" element={<SearchPage />}></Route>
          <Route
            path="/biosearch/oldsearch"
            element={<SearchOldPage />}
          ></Route>
        </Routes>
      </Fragment>
    </Router>
  )
}

export default App
