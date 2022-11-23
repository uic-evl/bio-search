import {
  Flex,
  FormControl,
  FormLabel,
  Input,
  Spacer,
  Button,
  Box,
} from '@chakra-ui/react'
import ColorMultiSelect from '../color-multi-select/color-multi-select'
import {useState} from 'react'

/* eslint-disable-next-line */
export interface SearchBarProps {
  defaultStartYear: number
  defaultEndYear: number
  colorsMapper: {[id: string]: string}
  options: {label: string; value: string}[]
  keywordPlaceholderValue: string
  onSearch: (
    arg1: string | null,
    arg2: string | null,
    arg3: string | null,
    arg4: string[],
  ) => Object
}

export function SearchBar({
  options,
  defaultStartYear,
  defaultEndYear,
  colorsMapper,
  onSearch,
  keywordPlaceholderValue = 'e.g. disease',
}: SearchBarProps) {
  const [keyword, setKeyword] = useState('')
  const [startYear, setStartYear] = useState(defaultStartYear)
  const [endYear, setEndYear] = useState(defaultEndYear)
  const [modalities, setModalities] = useState([])

  const onClick = () => {
    let startDate = null
    if (startYear) startDate = `${startYear}-01-01`

    let endDate = null
    if (endYear) endDate = `${endYear}-12-31`

    const terms = keyword || null
    onSearch(terms, startDate, endDate, modalities)
  }

  return (
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
  )
}

export default SearchBar
