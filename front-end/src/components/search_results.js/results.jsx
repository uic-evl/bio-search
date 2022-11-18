import {useState} from 'react'
import {Box, Flex, Button, Divider, chakra} from '@chakra-ui/react'
import {CompoundResultCard} from './compound_result_card'
import {useEffect} from 'react'

const SearchingFeedback = () => <Box mb={2}>Searching...</Box>

const NumberResults = ({numberResults}) => {
  return <Box mb={2}>{numberResults} documents found</Box>
}

const PagButton = ({selected, val, next, onClick}) => (
  <Button
    colorScheme={selected ? 'blue' : 'gray'}
    onClick={() => {
      onClick(next)
    }}
    mr={2}
  >
    {val}
  </Button>
)

const Pagination = ({currPage, numberPages, onClick, results}) => {
  const nextPage = currPage < numberPages ? currPage + 1 : -1
  const defaultParams = {selected: false, onClick}

  return (
    <Flex w="full" mt={2} alignItems="center" justifyContent="center">
      {currPage > 1 && (
        <>
          <PagButton {...defaultParams} val={1} next={0} />
          <p>...</p>
        </>
      )}
      {currPage > 0 && (
        <PagButton {...defaultParams} val={currPage} next={currPage - 1} />
      )}
      <PagButton
        {...defaultParams}
        selected={true}
        val={currPage + 1}
        next={currPage}
      />
      {nextPage > 0 && (
        <PagButton {...defaultParams} val={currPage + 2} next={currPage + 1} />
      )}

      <chakra.p mr={2}>...</chakra.p>

      <PagButton {...defaultParams} val={numberPages} next={numberPages} />
    </Flex>
  )
}

const Results = ({results, isLoading}) => {
  const resultsPerPage = 10
  const [currPage, setCurrPage] = useState(0)
  const [numberPages, setNumberPages] = useState(null)
  const [slicedResults, setSlicedResults] = useState(null)

  useEffect(() => {
    setCurrPage(0)
    if (results) {
      setNumberPages(Math.floor(results.length / resultsPerPage))
      setSlicedResults(results.slice(0, resultsPerPage))
    } else {
      setNumberPages(0)
      setSlicedResults(null)
    }
  }, [results])

  const handlePaginationOnClick = pageNumber => {
    if (pageNumber !== currPage) {
      setCurrPage(pageNumber)

      const startIdx = pageNumber * resultsPerPage
      const numberElements =
        pageNumber === numberPages ? results.length - startIdx : resultsPerPage
      const endIdx = startIdx + numberElements

      setSlicedResults(results.slice(startIdx, endIdx))
    }
  }

  return (
    <Box p={4}>
      {isLoading && <SearchingFeedback />}
      {results && <NumberResults numberResults={results.length} />}
      {slicedResults &&
        slicedResults.map(document => (
          <>
            <CompoundResultCard
              key={document.id}
              result={document}
              onClickOpen={() => {}}
              selected={false}
            />
            <Divider key={`divider-${document.id}`} mt={1} mb={1} />
          </>
        ))}
      {results && results.length > 0 && (
        <Pagination
          currPage={currPage}
          resultsPerPage={resultsPerPage}
          numberPages={numberPages}
          onClick={handlePaginationOnClick}
        />
      )}
    </Box>
  )
}

export {Results}
