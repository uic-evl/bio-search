import {useReducer} from 'react'
import {Box, Flex, Spacer, useToast} from '@chakra-ui/react'
import {
  RowModalityLegend,
  SearchBar,
  searchReducer,
  initSearchState,
  HorizontalFigureResults,
  Document,
  HelpQueries,
  Page,
} from '@biocuration-front-end/common-ui'
import {ReactComponent as Taxonomy} from '../../assets/taxonomy.svg'
import {colorsMapper, namesMapper, ddlSearchOptions} from '../../utils/mapper'
import {search, getPageFigureDetails} from '../../api/index'

const COLLECTION = process.env.NX_COLLECTION
const IMAGES_BASE_URL = process.env.NX_FIGURES_ENDPOINT
const PDFS_BASE_URL = process.env.NX_PDFS_ENDPOINT

const Search = () => {
  const [{documents, isLoading, filterModalities}, dispatch] = useReducer(
    searchReducer,
    initSearchState,
  )
  const toast = useToast()
  const baseModalities = Object.keys(colorsMapper).filter(
    el => !el.includes('.'),
  )

  const getPageUrl = (document: Document, page: Page) => {
    let folderName = document.pmcid
    if (COLLECTION === 'gxd') {
      folderName = document.otherid
    }

    const paddedPage = page.page.toString().padStart(6, '0')
    const pageUrl = `${PDFS_BASE_URL}/${folderName}/${folderName}-${paddedPage}.png`
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
    // save the preferred modalities to prioritize images to show
    dispatch({type: 'START_SEARCH', payload: modalities})
    const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))
    const results = await search(
      keywords,
      startDate,
      endDate,
      maxDocs,
      modalities,
    )
    await sleep(2)
    dispatch({type: 'END_SEARCH', payload: results})
  }

  return (
    <Box className="container" minH="100vh" w="full">
      <Box w="full" h="100px" p={4} pt={2} pb={0} zIndex={400}>
        <Flex w="full">
          <RowModalityLegend
            modalities={baseModalities}
            colorsMapper={colorsMapper}
            namesMapper={namesMapper}
            taxonomyImage={<Taxonomy />}
          />
          <Spacer />
          <HelpQueries tutorialUrl="https://docs.google.com/document/d/19msOo9-Tl90aRvWWBfk4uCfiXGPSR5taNHYSghSzyMg/edit?usp=sharing" />
        </Flex>
        <SearchBar
          defaultStartYear={2000}
          defaultEndYear={2022}
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
            {
              query: 'full_text:auditory AND full_text:cortex',
              label:
                'full_text:auditory AND full_text:cortex with modalities: mic.flu',
              modalities: [
                {label: 'fluorescence microscopy', value: 'mic.flu'},
              ],
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
