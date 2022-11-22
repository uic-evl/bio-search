import {useState} from 'react'
import {
  Box,
  FormControl,
  FormLabel,
  Input,
  Flex,
  Button,
  Spacer,
  chakra,
} from '@chakra-ui/react'
import chroma from 'chroma-js'
import Select from 'react-select'
import {cordModalityOptions, Long2ColorCord} from '../../utils/modalityMap'

const selectControlStyles = {
  control: styles => ({
    ...styles,
    borderRadius: '0.375rem',
    borderColor: '#E2E8F0',
    minHeight: '40px',
  }),
  option: (styles, {data, isSelected, isFocused}) => {
    const color = chroma(Long2ColorCord[data.value])
    return {
      ...styles,
      backgroundColor: isFocused ? color.alpha(0.3).css() : undefined,
      color: color.darken().css(),
    }
  },
  multiValue: (styles, {data}) => {
    const color = chroma(Long2ColorCord[data.value])
    return {
      ...styles,
      backgroundColor: color.alpha(1.0).css(),
    }
  },
}

const SampleQuery = ({
  text,
  onSearch,
  setQuery,
  setStartYear,
  setEndYear,
  setModalities,
}) => {
  const startDate = null
  const endDate = null
  const handleOnClick = () => {
    setQuery(text)
    setStartYear(2000)
    setEndYear(2020)
    setModalities([])
    onSearch(text, startDate, endDate, [])
  }

  return (
    <chakra.p
      mr={2}
      color="blue.500"
      _hover={{textDecoration: 'underline', cursor: 'pointer'}}
      onClick={handleOnClick}
    >
      {text}
    </chakra.p>
  )
}

const SampleQueries = ({
  onSearch,
  setQuery,
  setStartYear,
  setEndYear,
  setModalities,
}) => {
  return (
    <Flex dir="row" w="full" ml={4}>
      <chakra.p mr={2}>Try these queries:</chakra.p>
      <SampleQuery
        text="disease"
        onSearch={onSearch}
        setQuery={setQuery}
        setStartYear={setStartYear}
        setEndYear={setEndYear}
        setModalities={setModalities}
      />
      <SampleQuery
        text="influenza"
        onSearch={onSearch}
        setQuery={setQuery}
        setStartYear={setStartYear}
        setEndYear={setEndYear}
        setModalities={setModalities}
      />
    </Flex>
  )
}

export const SearchBar = ({onSearch}) => {
  const [query, setQuery] = useState('')
  const [startYear, setStartYear] = useState(2000)
  const [endYear, setEndYear] = useState(2020)
  const [modalities, setModalities] = useState([])

  const onClick = () => {
    let startDate = null
    if (startYear) startDate = `${startYear}-01-01`

    let endDate = null
    if (endYear) endDate = `${endYear}-12-31`

    const terms = query || null
    onSearch(terms, startDate, endDate, modalities)
  }

  return (
    <Box w="full" h="100px" p={4} pt={0} pb={0} zIndex={400}>
      <Flex w="full">
        <Box w="25%">
          <FormControl id="search">
            <FormLabel mb={0} fontSize={10}>
              SEARCH
            </FormLabel>
            <Input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              size={'md'}
              placeholder="e.g. disease"
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
                onChange={e => setStartYear(e.target.value)}
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
                onChange={e => setEndYear(e.target.value)}
                size={'md'}
              />
            </FormControl>
            <FormControl id="modalities" ml={2}>
              <FormLabel mb={0} fontSize={10}>
                WITH MODALITIES:
              </FormLabel>
              <Select
                name="modalities"
                options={cordModalityOptions}
                value={modalities}
                isMulti
                className="basic-multi-select"
                classNamePrefix="select"
                onChange={opts => setModalities(opts)}
                styles={selectControlStyles}
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
      <SampleQueries
        onSearch={onSearch}
        setQuery={setQuery}
        setStartYear={setStartYear}
        setEndYear={setEndYear}
        setModalities={setModalities}
      />
    </Box>
  )
}
