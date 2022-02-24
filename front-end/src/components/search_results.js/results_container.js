import {
  Box,
  Text,
  Badge,
  Flex,
  IconButton,
  Tooltip,
  chakra,
} from '@chakra-ui/react'
import {ViewIcon} from '@chakra-ui/icons'
import {Long2Short, Long2Color} from '../../utils/modalityMap'

export const ResultsContainer = ({results, onClickOpen}) => {
  return (
    <Box bg="gray.100" h="calc(100vh - 150px)" p={4} overflowY="scroll">
      {results && <NumberResults numberResults={results.length} />}
      {results &&
        results.map(document => (
          <SearchResultCard
            key={document.id}
            result={document}
            onClickOpen={onClickOpen}
          />
        ))}
    </Box>
  )
}

const NumberResults = ({numberResults}) => {
  return <Box mb={2}>{numberResults} documents found</Box>
}

const SearchResultCard = ({result, onClickOpen}) => {
  const year = publishDate => publishDate.substring(0, 4)

  return (
    <Box pl={4} w="full" pt={1} mb={4}>
      <Flex>
        <Tooltip label="display details ">
          <IconButton
            aria-label="Open details"
            icon={<ViewIcon />}
            onClick={() => onClickOpen(result.id)}
          ></IconButton>
        </Tooltip>
        <chakra.p
          dangerouslySetInnerHTML={{
            __html: result.title,
          }}
          color="blue.600"
        ></chakra.p>
      </Flex>
      <Text
        fontSize={'small'}
        noOfLines={5}
        dangerouslySetInnerHTML={{
          __html: year(result.publish_date) + '&nbsp;|&nbsp;' + result.abstract,
        }}
      ></Text>
      <Box>
        {Object.keys(result.modalities_count).map(key => (
          <Badge key={key} mr={1} background={Long2Color[key]} color="black">
            {Long2Short[key]}:{result.modalities_count[key]}
          </Badge>
        ))}
      </Box>
    </Box>
  )
}
