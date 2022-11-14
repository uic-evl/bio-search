import {
  Box,
  Text,
  Badge,
  Flex,
  IconButton,
  Tooltip,
  Link,
  chakra,
} from '@chakra-ui/react'
import {DownloadIcon, ViewIcon} from '@chakra-ui/icons'
import {Long2Short, Long2Color} from '../../utils/modalityMap'

const PDFS_ENDPOINT = process.env.REACT_APP_PDFS_ENDPOINT

export const ResultsContainer = ({
  results,
  onClickOpen,
  selectedIds,
  isLoading,
}) => {
  return (
    <Box bg="gray.100" h="calc(100vh - 150px)" p={4} overflowY="scroll">
      {isLoading && <SearchingFeedback />}
      {results && <NumberResults numberResults={results.length} />}
      {results &&
        results.map(document => (
          <SearchResultCard
            key={document.id}
            result={document}
            onClickOpen={onClickOpen}
            selected={
              selectedIds.length > 0 && selectedIds.includes(document.id)
            }
          />
        ))}
    </Box>
  )
}

const SearchingFeedback = () => <Box mb={2}>Searching...</Box>

const NumberResults = ({numberResults}) => {
  return <Box mb={2}>{numberResults} documents found</Box>
}

const SearchResultCard = ({result, onClickOpen, selected}) => {
  const year = publishDate => publishDate.substring(0, 4)

  const boxShadow = selected ? '0 4px 8px 0 rgba(0,0,0,0.2)' : null

  return (
    <Box
      pl={4}
      w="full"
      pt={1}
      mb={4}
      style={{
        boxShadow,
      }}
      background={selected ? 'white' : null}
    >
      <Flex>
        {/* <Tooltip label="display details ">
          <IconButton
            aria-label="Open details"
            icon={<ViewIcon />}
            onClick={() => onClickOpen(result.id)}
            disabled={selected}
            variant="link"
          ></IconButton>
        </Tooltip> */}
        <chakra.p
          dangerouslySetInnerHTML={{
            __html: result.title,
          }}
          color="blue.600"
          _hover={{
            textDecoration: !selected ? 'underline' : 'none',
            cursor: !selected ? 'pointer' : 'auto',
          }}
          onClick={() => {
            if (!selected) {
              onClickOpen(result.id)
            }
          }}
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
        <Tooltip label="download article">
          <Link href={`${PDFS_ENDPOINT}/${result.id}.pdf`} isExternal mr={1}>
            <DownloadIcon mx="2px" />
          </Link>
        </Tooltip>
        {Object.keys(result.modalities_count).map(key => (
          <Tooltip
            label={`# ${key} subfigures: ${result.modalities_count[key]}`}
            key={`tooltip-${key}`}
          >
            <Badge key={key} mr={1} background={Long2Color[key]} color="black">
              {Long2Short[key]}:{result.modalities_count[key]}
            </Badge>
          </Tooltip>
        ))}
      </Box>
    </Box>
  )
}
