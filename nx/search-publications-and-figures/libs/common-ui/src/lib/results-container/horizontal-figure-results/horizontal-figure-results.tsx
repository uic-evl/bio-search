import {useState, useEffect} from 'react'
import {LuceneDocument} from '../../types/lucene-document'
import {Document, Page} from '../../types/document'
import {Box, Flex, Divider, chakra, Button} from '@chakra-ui/react'
import SimpleResultCard from '../../simple-result-card/simple-result-card'
import FiguresPerPageViewer from '../../figures-per-page-viewer/figures-per-page-viewer'

const SearchingFeedback = () => <Box mb={2}>Searching...</Box>
const NumberResults = ({numberResults}: {numberResults: number}) => {
  return <Box mb={2}>{numberResults} documents found</Box>
}

/* eslint-disable-next-line */
interface PagButtonProps {
  selected: boolean
  val: number
  next: number
  onClick: (arg1: number) => void
}

const PagButton = ({selected, val, next, onClick}: PagButtonProps) => (
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

/* eslint-disable-next-line */
interface PaginationProps {
  currPage: number
  numberPages: number
  onClick: (arg1: number) => void
}

const Pagination = ({currPage, numberPages, onClick}: PaginationProps) => {
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

/* eslint-disable-next-line */
export interface HorizontalResultCardProps {
  document: LuceneDocument
  colorsMapper: {[id: string]: string}
  figuresBaseUrl: string
  getPageFigureData: (arg1: string) => Promise<Document>
  getPageUrl: (arg1: Document, arg2: Page) => string
}

const HorizontalResultCard = ({
  document,
  colorsMapper,
  figuresBaseUrl,
  getPageFigureData,
  getPageUrl,
}: HorizontalResultCardProps) => {
  const [docFigureInfo, setDocFigureInfo] = useState<Document | null>(null)

  useEffect(() => {
    const load = async () => {
      const details = await getPageFigureData(document.id.toString())
      setDocFigureInfo(details)
    }
    load()
  }, [document.id])

  return (
    <Flex direction={'row'} h="250px">
      <Box w="40%" h="100%">
        {docFigureInfo && (
          <SimpleResultCard
            document={document}
            onClick={() => {}}
            colorMapper={colorsMapper}
            selected={false}
          />
        )}
      </Box>
      <Box w="60%" h="100%" pl={2}>
        {docFigureInfo && (
          <FiguresPerPageViewer
            document={docFigureInfo}
            colorsMapper={colorsMapper}
            figuresBaseUrl={figuresBaseUrl}
            getPageUrl={getPageUrl}
          />
        )}
      </Box>
    </Flex>
  )
}

/* eslint-disable-next-line */
export interface HorizontalFigureResultsProps {
  documents: LuceneDocument[]
  isLoading: boolean
  colorsMapper: {[id: string]: string}
  figuresBaseUrl: string
  getPageFigureData: (arg1: string) => Promise<Document>
  getPageUrl: (arg1: Document, arg2: Page) => string
}

export function HorizontalFigureResults({
  documents,
  isLoading,
  colorsMapper,
  figuresBaseUrl,
  getPageFigureData,
  getPageUrl,
}: HorizontalFigureResultsProps) {
  const resultsPerPage = 10
  const [currPage, setCurrPage] = useState(0)
  const [numberPages, setNumberPages] = useState<number>(0)
  const [slicedResults, setSlicedResults] = useState<LuceneDocument[] | null>(
    null,
  )

  useEffect(() => {
    setCurrPage(0)
    if (documents) {
      setNumberPages(Math.floor(documents.length / resultsPerPage))
      setSlicedResults(documents.slice(0, resultsPerPage))
    } else {
      setNumberPages(0)
      setSlicedResults(null)
    }
  }, [documents])

  const handlePaginationOnClick = (pageNumber: number) => {
    if (pageNumber !== currPage) {
      setCurrPage(pageNumber)

      const startIdx = pageNumber * resultsPerPage
      const numberElements =
        pageNumber === numberPages
          ? documents.length - startIdx
          : resultsPerPage
      const endIdx = startIdx + numberElements

      setSlicedResults(documents.slice(startIdx, endIdx))
    }
  }

  return (
    <Box p={4}>
      {isLoading && <SearchingFeedback />}
      {documents && <NumberResults numberResults={documents.length} />}
      {slicedResults &&
        slicedResults.map(document => (
          <>
            <HorizontalResultCard
              key={document.id}
              document={document}
              colorsMapper={colorsMapper}
              figuresBaseUrl={figuresBaseUrl}
              getPageFigureData={getPageFigureData}
              getPageUrl={getPageUrl}
            />
            <Divider key={`divider-${document.id}`} mt={1} mb={1} />
          </>
        ))}
      {documents && documents.length > 0 && (
        <Pagination
          currPage={currPage}
          numberPages={numberPages}
          onClick={handlePaginationOnClick}
        />
      )}
    </Box>
  )
}

export default HorizontalFigureResults
