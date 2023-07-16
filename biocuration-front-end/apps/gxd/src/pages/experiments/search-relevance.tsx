import {useMemo, useReducer, useState} from 'react'
import {Box, Flex, Spacer, Button, useToast, Text} from '@chakra-ui/react'
import {
  RowModalityLegend,
  SearchBar,
  searchReducer,
  initSearchState,
  HelpQueries,
  Document,
  Page,
} from '@biocuration-front-end/common-ui'
import {HorizontalFigureResults} from './result-cards'
import {ReactComponent as Taxonomy} from '../../assets/taxonomy.svg'
import {colorsMapper, namesMapper, ddlSearchOptions} from '../../utils/mapper'
import {search, getPageFigureDetails} from '../../api'
import {About} from '../search/about'
import {useLocation} from 'react-router-dom'

/* eslint-disable-next-line */
export interface SearchProps {
  logout: () => void
}

const useQuery = () => {
  const {search} = useLocation()
  return useMemo(() => new URLSearchParams(search), [search])
}

const COLLECTION = process.env.NX_COLLECTION
const IMAGES_BASE_URL = process.env.NX_FIGURES_ENDPOINT
const PDFS_BASE_URL = process.env.NX_PDFS_ENDPOINT

const SearchRelevanceExperiment = ({logout}: SearchProps) => {
  const [{documents, isLoading, filterModalities}, dispatch] = useReducer(
    searchReducer,
    initSearchState,
  )
  const [relevantIds, setRelevantIds] = useState<number[]>([])
  const toast = useToast()
  const baseModalities = Object.keys(colorsMapper).filter(
    el => !el.includes('.'),
  )
  const queryParams = useQuery()
  const condition = queryParams.get('c') || 'image'
  const targetNumber =
    queryParams.get('n') !== null ? parseInt(queryParams.get('n') || '') : 10

  const getPageUrl = (document: Document, page: Page) => {
    const paddedPage = page.page.toString().padStart(6, '0')
    const pageUrl = `${PDFS_BASE_URL}/${document.otherid}/${document.otherid}-${paddedPage}.png`
    return pageUrl
  }

  const handleSearch = async (
    keywords: string | null,
    startDate: string | null,
    endDate: string | null,
    modalities: string[],
  ) => {
    if (keywords == null) {
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
    dispatch({type: 'START_SEARCH', payload: modalities})
    const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))
    const results = await search(
      keywords,
      COLLECTION,
      startDate,
      endDate,
      maxDocs,
      modalities,
    )
    await sleep(10)
    dispatch({type: 'END_SEARCH', payload: results})
  }

  return (
    <Box className="container" minH="100vh" w="full">
      <Flex
        justifyContent={'left'}
        alignItems={'center'}
        w="full"
        h="50px"
        backgroundColor={'yellow.300'}
        p="2"
      >
        <Text>
          Use the search interface to find {targetNumber} relevant documents{' '}
        </Text>
        <Spacer />
        <Text mr={2}>
          {relevantIds.length} / {targetNumber}
        </Text>
        <Button
          disabled={relevantIds.length < targetNumber}
          colorScheme="green"
        >
          Finish Task
        </Button>
      </Flex>
      <Box w="full" h="100px" p={4} pt={2} pb={0} zIndex={400}>
        <Flex w="full" alignItems={'center'}>
          <Text fontWeight={'bold'}>GXD Search</Text>
          <RowModalityLegend
            modalities={baseModalities}
            colorsMapper={colorsMapper}
            namesMapper={namesMapper}
            taxonomyImage={<Taxonomy />}
          />
          <Spacer />
          <HelpQueries
            tutorialUrl={
              'https://docs.google.com/document/d/1c0SFMi7o14HuoLZ0Q0-Jll5nfjDoy1gZbaQkG6KnLG8/edit?usp=sharing'
            }
          />
          <About />
          <Button
            backgroundColor={undefined}
            size={'xs'}
            variant="outline"
            onClick={logout}
            ml={1}
          >
            logout
          </Button>
        </Flex>
        <SearchBar
          defaultStartYear={2012}
          defaultEndYear={2016}
          options={ddlSearchOptions}
          colorsMapper={colorsMapper}
          onSearch={handleSearch}
          keywordPlaceholderValue="e.g. disease"
          sampleQueries={[
            {query: 'disease', label: 'disease', modalities: []},
            {
              query: 'title:kinase AND abstract:transcription',
              label: 'title:kinase AND abstract:transcription',
              modalities: [],
            },
          ]}
          isLoading={isLoading}
        />

        <Box w="full" mt={2}>
          <HorizontalFigureResults
            documents={documents}
            isLoading={isLoading}
            colorsMapper={colorsMapper}
            namesMapper={namesMapper}
            preferredModalities={filterModalities}
            figuresBaseUrl={IMAGES_BASE_URL}
            getPageFigureData={getPageFigureDetails}
            getPageUrl={getPageUrl}
            condition={condition}
            relevantIds={relevantIds}
            setRelevantIds={setRelevantIds}
          />
        </Box>
      </Box>
    </Box>
  )
}

export {SearchRelevanceExperiment}
