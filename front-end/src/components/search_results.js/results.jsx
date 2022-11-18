import {useState} from 'react'
import {Box, Flex, Button, Divider} from '@chakra-ui/react'
import {SearchResultCard} from './simple_result_card'

const SearchingFeedback = () => <Box mb={2}>Searching...</Box>

const NumberResults = ({numberResults}) => {
  return <Box mb={2}>{numberResults} documents found</Box>
}

const Pagination = ({currPage, resultsPerPage, numberPages, onClick}) => {
  const nextPage = currPage < numberPages ? currPage + 1 : -1

  return (
    <Flex w="full" mt={2} alignItems="center" justifyContent="center">
      {currPage > 0 && (
        <Button
          mr={1}
          onClick={() => {
            onClick(currPage - 1)
          }}
        >
          {currPage}
        </Button>
      )}
      <Button
        colorScheme="blue"
        mr={1}
        onClick={() => {
          onClick(currPage)
        }}
      >
        {currPage + 1}
      </Button>
      {nextPage > 0 && (
        <Button
          mr={1}
          onClick={() => {
            onClick(currPage + 1)
          }}
        >
          {currPage + 2}
        </Button>
      )}
      <p>...</p>
      <Button
        ml={1}
        onClick={() => {
          onClick(numberPages)
        }}
      >
        {numberPages}
      </Button>
    </Flex>
  )
}

const Results = ({results, onClickOpen, isLoading}) => {
  const resultsPerPage = 10
  const numberPages = results ? Math.floor(results.length / resultsPerPage) : 0
  const [currPage, setCurrPage] = useState(0)
  const [slicedResults, setSlicedResults] = useState(
    results ? results.slice(0, resultsPerPage) : null,
  )

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
      {results &&
        slicedResults.map(document => (
          <>
            <SearchResultCard
              key={document.id}
              result={document}
              onClickOpen={onClickOpen}
              selected={false}
            />
            <Divider key={`divider-${document.id}`} />
          </>
        ))}
      {results && (
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
