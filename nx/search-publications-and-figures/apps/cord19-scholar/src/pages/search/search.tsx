import {useReducer} from 'react'
import {Box, useToast} from '@chakra-ui/react'
import {
  RowModalityLegend,
  SearchBar,
  searchReducer,
  initSearchState,
} from '@search-publications-and-figures/common-ui'
import {ReactComponent as Taxonomy} from '../../assets/taxonomy.svg'
import {colorsMapper, namesMapper, ddlSearchOptions} from '../../utils/mapper'
import {search} from '../../api/index'

/* eslint-disable-next-line */
export interface SearchProps {}

const COLLECTION = process.env.NX_COLLECTION

const Search = ({}: SearchProps) => {
  const [state, dispatch] = useReducer(searchReducer, initSearchState)
  const toast = useToast()
  const baseModalities = Object.keys(colorsMapper).filter(
    el => !el.includes('.'),
  )

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
    console.log(results)
  }

  return (
    <Box className="container" minH="100vh" w="full">
      <Box w="full" h="100px" p={4} pt={0} pb={0} zIndex={400}>
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
        />
      </Box>
    </Box>
  )
}

export default Search
