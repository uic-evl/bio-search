import {useState} from 'react'
import {SearchBar} from './components/search_bar/search_bar'
import {ResultsContainer} from './components/search_results.js/results_container'
import {DetailsContainer} from './components/doc_details/details'
import {Box, Flex, Select as ChakraSelect} from '@chakra-ui/react'

import {search, getDetails} from './api/index'

const displayModes = [
  {value: 'BBOX', label: 'Bounding Boxes'},
  {value: 'SUBFIGURES', label: 'Subfigures'},
]

function App() {
  const [documents, setDocuments] = useState(null)
  const [detailsTop, setDetailsTop] = useState(null)
  const [detailsBottom, setDetailsBottom] = useState(null)
  const [selectedIds, setSelectedIds] = useState([])
  const [displayMode, setDisplayMode] = useState('SUBFIGURES')

  const handleSearch = async (terms, startDate, endDate, modalities) => {
    const maxDocs = 2000
    const collection = 'gxd'
    const results = await search(
      terms,
      collection,
      startDate,
      endDate,
      maxDocs,
      modalities,
    )
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
    setSelectedIds([...selectedIds, documentId])
  }

  const handleCloseDetails = position => {
    let idToRemove
    if (position === 'top') {
      setDetailsTop(null)
      idToRemove = detailsTop.cord_uid
    } else {
      setDetailsBottom(null)
      idToRemove = detailsBottom.cord_uid
    }
    setSelectedIds(selectedIds.filter(id => id !== idToRemove))
  }

  return (
    <Box className="container" minH="100vh" w="full">
      <SearchBar onSearch={handleSearch} />
      <Flex pl={4}>
        <Box w="25%">
          <ResultsContainer
            results={documents}
            onClickOpen={handleOpenDetails}
            selectedIds={selectedIds}
          />
        </Box>
        <Box w="75%">
          <ChakraSelect
            size={'sm'}
            onChange={e => setDisplayMode(e.target.value)}
          >
            {displayModes.map(el => (
              <option key={el.value} value={el.value}>
                {el.label}
              </option>
            ))}
          </ChakraSelect>
          {detailsTop && (
            <DetailsContainer
              document={detailsTop}
              position="top"
              onClickClose={handleCloseDetails}
              displayMode={displayMode}
            />
          )}
          {detailsBottom && (
            <DetailsContainer
              document={detailsBottom}
              position="bottom"
              onClickClose={handleCloseDetails}
              displayMode={displayMode}
            />
          )}
        </Box>
      </Flex>
    </Box>
  )
}

export default App
