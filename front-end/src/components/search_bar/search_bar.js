import {useState} from 'react'
import {
  Box,
  FormControl,
  FormLabel,
  Input,
  Flex,
  Button,
  Spacer,
} from '@chakra-ui/react'
import Select from 'react-select'
import {modalityOptions} from '../../utils/modalityMap'

const selectControlStyles = {
  control: styles => ({
    ...styles,
    borderRadius: '0.375rem',
    borderColor: '#E2E8F0',
    minHeight: '40px',
  }),
}

export const SearchBar = ({onSearch}) => {
  const [query, setQuery] = useState('')
  const [startYear, setStartYear] = useState(2012)
  const [endYear, setEndYear] = useState(2016)
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
    <Box w="full" h="100px" p={4} pb={0} zIndex={400}>
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
                options={modalityOptions}
                value={modalities}
                isMulti
                className="basic-multi-select"
                classNamePrefix="select"
                onChange={opts => setModalities(opts)}
                styles={selectControlStyles}
              />
            </FormControl>
            <Spacer />
            <Button w="200px" size="md" ml={2} mt={4} onClick={onClick}>
              Search
            </Button>
          </Flex>
        </Box>
      </Flex>
      {/* <Flex mt={1} w="75%">
        <FormControl id="modalities" ml={2}>
          <FormLabel mb={0} fontSize={10}>
            WITH MODALITIES:
          </FormLabel>
          <Select
            name="modalities"
            options={modalityOptions}
            value={modalities}
            isMulti
            className="basic-multi-select"
            classNamePrefix="select"
            onChange={opts => setModalities(opts)}
          />
        </FormControl>
        <Spacer />
        <Button w="200px" size="sm" ml={2} mt={4} onClick={onClick}>
          Search
        </Button>
      </Flex> */}
    </Box>
  )
}
