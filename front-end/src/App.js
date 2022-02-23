import {useState} from 'react'
import {SearchBar} from './components/search_bar/search_bar'
import {ResultsContainer} from './components/search_results.js/results_container'
import {DetailsContainer} from './components/doc_details/details'
import {Box, Flex} from '@chakra-ui/react'

import {search} from './api/index'

const doc1 = {
  title:
    "Dopaminergic control of autophagic-lysosomal function implicates Lmx1b in Parkinson's disease.",
  first_page: '5301479/5301479-000001.png',
  figures: ['a', 'b', 'c', 'd'],
}

function App() {
  const [documents, setDocuments] = useState(null)

  const handleSearch = async (terms, startDate, endDate) => {
    const maxDocs = 50
    const collection = 'gxd'
    const results = await search(terms, collection, startDate, endDate, maxDocs)
    console.log(results)
    setDocuments(results)
  }

  return (
    <Box className="container" minH="100vh" w="full">
      <SearchBar onSearch={handleSearch} />
      <Flex pl={4}>
        <Box w="25%">
          <ResultsContainer results={documents} />
        </Box>
        <Box w="75%">
          <DetailsContainer document={doc1} />
          <DetailsContainer document={doc1} />
        </Box>
      </Flex>
    </Box>
  )
}

export default App
