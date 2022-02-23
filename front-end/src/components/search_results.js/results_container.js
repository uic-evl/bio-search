import {Box, Text, Badge, chakra} from '@chakra-ui/react'
import {Long2Short} from '../../utils/modalityMap'

export const ResultsContainer = ({results}) => {
  return (
    <Box bg="gray.100" h="calc(100vh - 150px)" p={4} overflowY="scroll">
      {results && <NumberResults numberResults={results.length} />}
      {results &&
        results.map(document => (
          <SearchResultCard key={document.id} result={document} />
        ))}
    </Box>
  )
}

const NumberResults = ({numberResults}) => {
  return <Box mb={2}>{numberResults} documents found</Box>
}

const SearchResultCard = ({result}) => {
  const year = publishDate => publishDate.substring(0, 4)

  return (
    <Box pl={4} w="full" pt={1} mb={4}>
      <chakra.p
        dangerouslySetInnerHTML={{
          __html: result.title,
        }}
        color="blue.600"
      ></chakra.p>
      <Text
        fontSize={'small'}
        noOfLines={5}
        dangerouslySetInnerHTML={{
          __html: year(result.publish_date) + '&nbsp;|&nbsp;' + result.abstract,
        }}
      ></Text>
      <Box>
        {Object.keys(result.modalities_count).map(key => (
          <Badge key={key} mr={1} colorScheme="blue">
            {Long2Short[key]}:{result.modalities_count[key]}
          </Badge>
        ))}
      </Box>
    </Box>
  )
}
