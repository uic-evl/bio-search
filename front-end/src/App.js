import {useState} from 'react'
import {SearchBar} from './components/search_bar/search_bar'
import {ResultsContainer} from './components/search_results.js/results_container'
import {DetailsContainer} from './components/doc_details/details'
import {Box, Flex} from '@chakra-ui/react'

import {search, getDetails} from './api/index'

function App() {
  const [documents, setDocuments] = useState(null)
  const [detailsTop, setDetailsTop] = useState(null)
  const [detailsBottom, setDetailsBottom] = useState(null)

  const handleSearch = async (terms, startDate, endDate, modalities) => {
    const maxDocs = 500
    const collection = 'gxd'
    const results = await search(
      terms,
      collection,
      startDate,
      endDate,
      maxDocs,
      modalities,
    )
    console.log(results)
    setDocuments(results)
  }

  const handleOpenDetails = async documentId => {
    if (detailsTop && detailsBottom) {
      console.log('free one slot first')
      return
    }

    const details = await getDetails(documentId)
    if (!detailsTop) setDetailsTop(details)
    else setDetailsBottom(details)
  }

  const handleCloseDetails = position => {
    if (position === 'top') {
      setDetailsTop(null)
    } else {
      setDetailsBottom(null)
    }
  }

  return (
    <Box className="container" minH="100vh" w="full">
      <SearchBar onSearch={handleSearch} />
      <Flex pl={4}>
        <Box w="25%">
          <ResultsContainer
            results={documents}
            onClickOpen={handleOpenDetails}
          />
        </Box>
        <Box w="75%">
          {detailsTop && (
            <DetailsContainer
              document={detailsTop}
              position="top"
              onClickClose={handleCloseDetails}
            />
          )}
          {detailsBottom && (
            <DetailsContainer
              document={detailsBottom}
              position="bottom"
              onClickClose={handleCloseDetails}
            />
          )}
        </Box>
      </Flex>
    </Box>
  )
}

export default App
