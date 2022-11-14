import {useState} from 'react'
import {SearchBar} from '../../components/search_bar/search_bar'
import {ResultsContainer} from '../../components/search_results.js/results_container'
import EnhancedSurrogate from '../../components/doc_details/enhanced_surrogate'
import {Box, Flex, useToast} from '@chakra-ui/react'

import {search, getDetails} from '../../api/index'

function SearchPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [documents, setDocuments] = useState(null)
  const [detailsTop, setDetailsTop] = useState(null)
  const [detailsBottom, setDetailsBottom] = useState(null)
  const [selectedIds, setSelectedIds] = useState([])
  const toast = useToast()

  const handleSearch = async (terms, startDate, endDate, modalities) => {
    console.log(terms)

    if (terms == null) {
      toast({
        position: 'top',
        description: 'Please enter at least one keyword in the search bar',
        duration: 3000,
        isClosable: true,
        status: 'warning',
      })
      return
    }

    const maxDocs = 2000
    const collection = 'gxd'
    setDocuments(null)
    setSelectedIds([])
    setDetailsTop(null)
    setDetailsBottom(null)
    setIsLoading(true)
    const sleep = ms => new Promise(r => setTimeout(r, ms))
    const results = await search(
      terms,
      collection,
      startDate,
      endDate,
      maxDocs,
      modalities,
    )
    await sleep(1000)

    setIsLoading(false)
    setDocuments(results)
  }

  const handleOpenDetails = async documentId => {
    if (detailsTop && detailsBottom) {
      toast({
        title: 'Details panel full',
        position: 'top',
        description: 'Please first close an open document',
        duration: 5000,
        isClosable: true,
        status: 'warning',
      })
      return
    }

    const details = await getDetails(documentId)
    if (!detailsTop) setDetailsTop(details)
    else setDetailsBottom(details)
    setSelectedIds([...selectedIds, documentId])
  }

  const handleCloseDetails = position => {
    console.log('closing')
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
      <Flex pl={4} h="calc(100vh - 150px)" maxH="calc(100vh - 150px)">
        <Box w="25%">
          <ResultsContainer
            results={documents}
            onClickOpen={handleOpenDetails}
            selectedIds={selectedIds}
            isLoading={isLoading}
          />
        </Box>
        <Box w="75%" h="100%" maxH="calc(100vh - 150px)">
          {detailsTop && (
            <EnhancedSurrogate
              key={'surrogate-top'}
              document={detailsTop}
              position="top"
              onClickClose={handleCloseDetails}
            />
          )}
          {detailsBottom && (
            <EnhancedSurrogate
              key={'surrogate-bottom'}
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

export default SearchPage
