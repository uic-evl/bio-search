import {Box, Text, Badge, Flex, Tooltip, chakra, Link} from '@chakra-ui/react'
// import {DownloadIcon} from '@chakra-ui/icons'
import {Long2ColorCord} from '../../utils/modalityMap'

const ModalityBadges = ({modalityCount}) =>
  Object.keys(modalityCount).map(key => (
    <Tooltip
      label={`# ${key} subfigures: ${modalityCount[key]}`}
      key={`tooltip-${key}`}
    >
      <Badge key={key} mr={1} background={Long2ColorCord[key]} color="black">
        {key}:{modalityCount[key]}
      </Badge>
    </Tooltip>
  ))

const ResultTitle = ({id, title, url, selected, onClickOpen}) => (
  <Link href={`${url}`} isExternal mr={1}>
    <chakra.p
      dangerouslySetInnerHTML={{
        __html: title,
      }}
      color="blue.600"
      _hover={{
        textDecoration: !selected ? 'underline' : 'none',
        cursor: !selected ? 'pointer' : 'auto',
      }}
      onClick={() => {
        if (!selected) {
          onClickOpen(id)
        }
      }}
    ></chakra.p>
  </Link>
)

const SearchResultCard = ({result, onClickOpen, selected, pdfEndpoint}) => {
  const year = publishDate => publishDate.substring(0, 4)

  const boxShadow = selected ? '0 4px 8px 0 rgba(0,0,0,0.2)' : null

  return (
    <Box
      pl={4}
      w="full"
      pt={1}
      mb={4}
      style={{boxShadow}}
      background={selected ? 'white' : null}
    >
      <Flex>
        <ResultTitle
          title={result.title}
          selected={selected}
          id={result.id}
          url={`https://www.google.com/search?q=${result.url}`}
          onClickOpen={onClickOpen}
        />
      </Flex>
      <Text
        fontSize={'small'}
        noOfLines={5}
        dangerouslySetInnerHTML={{
          __html: year(result.publish_date) + '&nbsp;|&nbsp;' + result.abstract,
        }}
      ></Text>
      <Box>
        {/* <Tooltip label="download article">
          <Link href={`${pdfEndpoint}/${result.id}.pdf`} isExternal mr={1}>
            <DownloadIcon mx="2px" />
          </Link>
        </Tooltip> */}
        <Badge mr={1} background="black" color="white">
          {`#FIGS: ${result.num_figures}`}
        </Badge>
        <ModalityBadges modalityCount={result.modalities_count} />
      </Box>
    </Box>
  )
}

export {SearchResultCard}
