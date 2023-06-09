import {useReducer} from 'react'
import {Box, Flex, Spacer, Button, useToast, Text} from '@chakra-ui/react'
import {
  RowModalityLegend,
  SearchBar,
  searchReducer,
  initSearchState,
  HorizontalFigureResults,
  HelpQueries,
  Document,
  Page,
} from '@search-publications-and-figures/common-ui'
import {ReactComponent as Taxonomy} from '../../assets/taxonomy.svg'
import {colorsMapper, namesMapper, ddlSearchOptions} from '../../utils/mapper'
import {search, getPageFigureDetails} from '../../api'
import {About} from './about'

/* eslint-disable-next-line */
export interface SearchProps {
  logout: () => void
}

const COLLECTION = process.env.NX_COLLECTION
const IMAGES_BASE_URL = process.env.NX_FIGURES_ENDPOINT
const PDFS_BASE_URL = process.env.NX_PDFS_ENDPOINT

const Search = ({logout}: SearchProps) => {
  const [{documents, isLoading, filterModalities}, dispatch] = useReducer(
    searchReducer,
    initSearchState,
  )
  const toast = useToast()
  const baseModalities = Object.keys(colorsMapper).filter(
    el => !el.includes('.'),
  )

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
      <Box w="full" h="100px" p={4} pt={2} pb={0} zIndex={400}>
        <Flex w="full" alignItems={'center'}>
          <Text fontWeight={'bold'}>GDX Search</Text>
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
          />
        </Box>
      </Box>
    </Box>
  )
}

export default Search
