import {useReducer} from 'react'
import {SearchBar} from '../../components/search_bar/search_bar'
import {Results} from '../../components/search_results.js/results'
import {Box, useToast} from '@chakra-ui/react'
import {initState, searchReducer} from './searchReducer'

import {search} from '../../api/index'

export const SearchPageWide = () => {
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

  return (
    <Box className="container" minH="100vh" w="full">
      <SearchBar onSearch={handleSearch} />
      <Box w="full">
        <Results
          results={state.documents}
          isLoading={state.isLoading}
          onClickOpen={() => {}}
        />
      </Box>
    </Box>
  )
}
