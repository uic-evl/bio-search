import {useState} from 'react'
import {
  Box,
  FormControl,
  FormLabel,
  Input,
  Flex,
  Select as ChakraSelect,
  Button,
  Spacer,
} from '@chakra-ui/react'

const options = [
  {value: 'GXD', label: 'GXD'},
  // {value: 'CORD-19', label: 'CORD-19'},
]

export const SearchBar = ({onSearch}) => {
  const [query, setQuery] = useState('')
  const [startYear, setStartYear] = useState('')
  const [endYear, setEndYear] = useState('')

  const onClick = () => {
    let startDate = null
    if (startYear) startDate = `${startYear}-01-01`

    let endDate = null
    if (endYear) endDate = `${endYear}-01-01`

    const terms = query || null
    onSearch(terms, startDate, endDate)
  }

  return (
    <Box w="full" h="150px" p={4} pb={0}>
      <Flex w="full">
        <Box w="50%">
          <FormControl id="search">
            <FormLabel mb={0} fontSize={10}>
              SEARCH
            </FormLabel>
            <Input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              size={'sm'}
            />
          </FormControl>

          <Flex mt={1}>
            <FormControl id="domain" w="150px">
              <FormLabel mb={0} fontSize={10}>
                COLLECTION
              </FormLabel>
              <ChakraSelect size={'sm'}>
                {options.map(el => (
                  <option key={el.value} value={el.value}>
                    {el.label}
                  </option>
                ))}
              </ChakraSelect>
            </FormControl>

            <FormControl id="start-date" ml={2} w="100px">
              <FormLabel mb={0} fontSize={10}>
                FROM
              </FormLabel>
              <Input
                type="text"
                value={startYear}
                onChange={e => setStartYear(e.target.value)}
                size={'sm'}
              />
            </FormControl>

            <FormControl id="end-date" ml={2} w="100px">
              <FormLabel mb={0} fontSize={10}>
                TO
              </FormLabel>
              <Input
                type="text"
                value={endYear}
                onChange={e => setEndYear(e.target.value)}
                size={'sm'}
              />
            </FormControl>
            <Spacer />
            <Button w="200px" size="sm" ml={2} mt={4} onClick={onClick}>
              Search
            </Button>
          </Flex>
        </Box>
        <Box w="50%"></Box>
      </Flex>
    </Box>
  )
}
