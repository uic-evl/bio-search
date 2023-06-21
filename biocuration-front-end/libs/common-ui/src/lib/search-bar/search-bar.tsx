import {
  Flex,
  FormControl,
  FormLabel,
  Input,
  Spacer,
  Button,
  Box,
  chakra,
} from '@chakra-ui/react'
import ColorMultiSelect from '../color-multi-select/color-multi-select'
import {Dispatch, SetStateAction, useState} from 'react'
import {SampleQueryType} from '../types/sampleQuery'

/* eslint-disable-next-line */
export interface SearchBarProps {
  defaultStartYear: number
  defaultEndYear: number
  colorsMapper: {[id: string]: string}
  options: {label: string; value: string}[]
  keywordPlaceholderValue: string
  sampleQueries: SampleQueryType[]
  isLoading: boolean
  onSearch: OnSearch
}

export interface OnSearch {
  (
    arg1: string | null,
    arg2: string | null,
    arg3: string | null,
    arg4: string[],
  ): void
}

interface SampleQueryProps {
  query: SampleQueryType
  onSearch: OnSearch
  setKeyword: Dispatch<SetStateAction<string>>
  setStartYear: Dispatch<SetStateAction<number>>
  setEndYear: Dispatch<SetStateAction<number>>
  setModalities: Dispatch<SetStateAction<{label: string; value: string}[]>>
}

const SampleQuery = ({
  query,
  onSearch,
  setKeyword,
  setStartYear,
  setEndYear,
  setModalities,
}: SampleQueryProps) => {
  const startDate = null
  const endDate = null
  const handleOnClick = () => {
    setKeyword(query.query)
    setStartYear(2000)
    setEndYear(2022)
    setModalities(query.modalities)
    const queryModalities = query.modalities.map(el => el.value)
    onSearch(query.query, startDate, endDate, queryModalities)
  }

  return (
    <chakra.p
      mr={4}
      color="blue.500"
      _hover={{textDecoration: 'underline', cursor: 'pointer'}}
      onClick={handleOnClick}
    >
      {query.label}
    </chakra.p>
  )
}

export function SearchBar({
  options,
  defaultStartYear,
  defaultEndYear,
  colorsMapper,
  onSearch,
  sampleQueries,
  isLoading,
  keywordPlaceholderValue = 'e.g. disease',
}: SearchBarProps) {
  const [keyword, setKeyword] = useState('')
  const [startYear, setStartYear] = useState(defaultStartYear)
  const [endYear, setEndYear] = useState(defaultEndYear)
  const [modalities, setModalities] = useState<
    {value: string; label: string}[]
  >([])

  const onClick = () => {
    let startDate = null
    if (startYear) startDate = `${startYear}-01-01`

    let endDate = null
    if (endYear) endDate = `${endYear}-12-31`

    const terms = keyword || null
    onSearch(
      terms,
      startDate,
      endDate,
      modalities.map(el => el.value),
    )
  }

  return (
    <Box>
      <form
        onSubmit={e => {
          e.preventDefault()
          onClick()
        }}
      >
        <Flex w="full">
          <Box w="25%">
            <FormControl id="search">
              <FormLabel mb={0} fontSize={10}>
                SEARCH
              </FormLabel>
              <Input
                type="text"
                value={keyword}
                onChange={e => setKeyword(e.target.value)}
                size={'md'}
                placeholder={keywordPlaceholderValue}
              />
            </FormControl>
          </Box>
          <Box w="75%">
            <Flex ml={2}>
              <FormControl id="start-date" ml={2} w="110px">
                <FormLabel mb={0} fontSize={10}>
                  FROM
                </FormLabel>
                <Input
                  type="number"
                  value={startYear}
                  onChange={e => setStartYear(parseInt(e.target.value))}
                  size={'md'}
                />
              </FormControl>

              <FormControl id="end-date" ml={2} w="110px">
                <FormLabel mb={0} fontSize={10}>
                  TO
                </FormLabel>
                <Input
                  type="number"
                  value={endYear}
                  onChange={e => setEndYear(parseInt(e.target.value))}
                  size={'md'}
                />
              </FormControl>
              <FormControl id="modalities" ml={2}>
                <FormLabel mb={0} fontSize={10}>
                  WITH MODALITIES:
                </FormLabel>
                <ColorMultiSelect
                  name="modalities"
                  options={options}
                  colorsMapper={colorsMapper}
                  values={modalities}
                  setValues={setModalities}
                />
              </FormControl>
              <Spacer />
              <Button
                type="submit"
                isLoading={isLoading}
                colorScheme={'blue'}
                w="200px"
                size="md"
                ml={2}
                mt={4}
                onClick={onClick}
              >
                Search
              </Button>
            </Flex>
          </Box>
        </Flex>
        <Flex dir="row" w="full" ml={4}>
          <chakra.p mr={2}>Try these queries:</chakra.p>
          {sampleQueries.map(el => (
            <SampleQuery
              key={`sample-${el.query}`}
              query={el}
              onSearch={onSearch}
              setKeyword={setKeyword}
              setStartYear={setStartYear}
              setEndYear={setEndYear}
              setModalities={setModalities}
            />
          ))}
        </Flex>
      </form>
    </Box>
  )
}

export default SearchBar
