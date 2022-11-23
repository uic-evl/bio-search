/* eslint-disable-next-line */
export interface SearchProps {}

import {Box} from '@chakra-ui/react'
import {
  RowModalityLegend,
  SearchBar,
} from '@search-publications-and-figures/common-ui'
import {ReactComponent as Taxonomy} from '../../assets/taxonomy.svg'
import {colorsMapper, namesMapper, ddlSearchOptions} from '../../utils/mapper'

const Search = ({}: SearchProps) => {
  const baseModalities = Object.keys(colorsMapper).filter(
    el => !el.includes('.'),
  )

  const handleSearch = async (
    keywords: string | null,
    startDate: string | null,
    endDate: string | null,
    modalities: string[],
  ) => {}

  return (
    <Box className="container" minH="100vh" w="full">
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
      />
    </Box>
  )
}

export default Search
