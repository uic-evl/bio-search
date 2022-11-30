import {useReducer} from 'react'
import {Box, useToast} from '@chakra-ui/react'
import {
  RowModalityLegend,
  SearchBar,
  searchReducer,
  initSearchState,
  HorizontalFigureResults,
} from '@search-publications-and-figures/common-ui'
import {ReactComponent as Taxonomy} from '../../assets/taxonomy.svg'
import {colorsMapper, namesMapper, ddlSearchOptions} from '../../utils/mapper'
import {search, getPageFigureDetails} from '../../api/index'
import {Document, Page} from 'libs/common-ui/src/lib/types/document'

/* eslint-disable-next-line */
export interface SearchProps {}

const COLLECTION = process.env.NX_COLLECTION
const IMAGES_BASE_URL = process.env.NX_FIGURES_ENDPOINT
const PDFS_BASE_URL = process.env.NX_PDFS_ENDPOINT

const Search = ({}: SearchProps) => {
  const [{documents, isLoading}, dispatch] = useReducer(
    searchReducer,
    initSearchState,
  )
  const toast = useToast()
  const baseModalities = Object.keys(colorsMapper).filter(
    el => !el.includes('.'),
  )

  const getPageUrl = (document: Document, page: Page) => {
    const paddedPage = page.page.toString().padStart(6, '0')
    const pageUrl = `${PDFS_BASE_URL}/${document.pmcid}/${document.pmcid}-${paddedPage}.png`
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
    dispatch({type: 'START_SEARCH'})
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
        <RowModalityLegend
          modalities={baseModalities}
          colorsMapper={colorsMapper}
          namesMapper={namesMapper}
          taxonomyImage={<Taxonomy />}
        />
        <SearchBar
          defaultStartYear={2000}
          defaultEndYear={2020}
          options={ddlSearchOptions}
          colorsMapper={colorsMapper}
          onSearch={handleSearch}
          keywordPlaceholderValue="e.g. disease"
          sampleKeywords={['disease', 'kinase']}
          isLoading={isLoading}
        />
        <Box w="full" mt={2}>
          <HorizontalFigureResults
            documents={documents}
            isLoading={isLoading}
            colorsMapper={colorsMapper}
            namesMapper={namesMapper}
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
