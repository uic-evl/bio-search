import {useReducer} from 'react'
import {SearchBar} from '../../components/search_bar/search_bar'
import {ResultsContainer} from '../../components/search_results.js/results_container'
import EnhancedSurrogate from '../../components/doc_details/enhanced_surrogate'
import {Box, Flex, useToast} from '@chakra-ui/react'

import {search, getDetails} from '../../api/index'
import {initState, searchReducer} from './searchReducer'

function SearchPage() {
  const [state, dispatch] = useReducer(searchReducer, initState)
  const toast = useToast()

  const handleSearch = async (terms, startDate, endDate, modalities) => {
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
    dispatch({type: 'START_SEARCH'})
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
    dispatch({type: 'END_SEARCH', payload: results})
  }

  const handleOpenDetails = async documentId => {
    const {detailsTop, detailsBottom} = state
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
    let payload = {details, documentId}
    if (!detailsTop) payload = {...payload, position: 'top'}
    else payload = {...payload, position: 'bottom'}
    dispatch({type: 'OPEN_DETAILS', payload})
  }

  const handleCloseDetails = position => {
    const {detailsTop, detailsBottom} = state
    const documentId =
      position === 'top' ? detailsTop.cord_uid : detailsBottom.cord_uid
    dispatch({type: 'CLOSE_DETAILS', payload: {documentId}})
  }

  return (
    <Box className="container" minH="100vh" w="full">
      <SearchBar onSearch={handleSearch} />
      <Flex pl={4} h="calc(100vh - 150px)" maxH="calc(100vh - 150px)">
        <Box w="25%">
          <ResultsContainer
            results={state.documents}
            onClickOpen={handleOpenDetails}
            selectedIds={state.selectedIds}
            isLoading={state.isLoading}
          />
        </Box>
        <Box w="75%" h="100%" maxH="calc(100vh - 150px)">
          {state.detailsTop && (
            <EnhancedSurrogate
              key={'surrogate-top'}
              document={state.detailsTop}
              position="top"
              onClickClose={handleCloseDetails}
            />
          )}
          {state.detailsBottom && (
            <EnhancedSurrogate
              key={'surrogate-bottom'}
              document={state.detailsBottom}
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
