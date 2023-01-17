import {Link, chakra, Badge, Box, Flex, Text} from '@chakra-ui/react'
import {LuceneDocument} from '../types/lucene-document'
import ModalityCountBadges from '../modality-count-badges/modality-count-badges'

/* eslint-disable-next-line */
export interface SimpleResultCardProps {
  document: LuceneDocument
  onClick: null | ((arg1: number) => void)
  selected: boolean
  colorMapper: {[id: string]: string}
  namesMapper: {[id: string]: string}
}

interface TitleProps {
  id: number
  title: string
  url: string
  selected: boolean
  onClick: ((arg1: number) => void) | null
}

/* innerHTML as the title may have highlighted parts to show keywords */
const Title = ({id, title, url, selected, onClick}: TitleProps) => (
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
        if (!selected && onClick) onClick(id)
      }}
    ></chakra.p>
  </Link>
)

export function SimpleResultCard({
  document,
  onClick,
  selected,
  colorMapper,
  namesMapper,
}: SimpleResultCardProps) {
  const year = (publishDate: string) => publishDate.substring(0, 4)
  const authors = (authorsStr: string) => {
    const authorsList = authorsStr.split(';')
    const formattedList = authorsList.map(el => {
      const idx = el.indexOf(',')
      return el.substring(idx + 2, idx + 3) + ' ' + el.substring(0, idx)
    })
    const authorsOutput = formattedList.join(', ')
    if (authorsOutput.length > 50) return authorsOutput.substring(0, 50) + '...'
    else return authorsOutput
  }

  return (
    <Box
      pl={4}
      w="full"
      pt={1}
      mb={4}
      style={{boxShadow: selected ? '0 4px 8px 0 rgba(0,0,0,0.2)' : undefined}}
      background={selected ? 'white' : undefined}
    >
      <Flex w="full">
        <Title
          title={document.title}
          selected={selected}
          id={document.id}
          url={`https://doi.org/${document.url}`}
          onClick={onClick}
        />
      </Flex>
      <Text fontSize={'small'} color={'#006621'}>
        {year(document.publish_date) +
          ' | ' +
          document.journal +
          ' | ' +
          authors(document.authors)}
      </Text>
      {document.abstract.length > 0 && (
        <Text
          fontSize={'small'}
          noOfLines={5}
          dangerouslySetInnerHTML={{
            __html: '...' + document.abstract,
          }}
        ></Text>
      )}

      {document.full_text ? (
        <Text
          mt={1}
          fontSize={'small'}
          fontStyle={'italic'}
          noOfLines={4}
          dangerouslySetInnerHTML={{
            __html: '...' + document.full_text,
          }}
        ></Text>
      ) : null}
      <Box>
        <Badge mr={1} background="black" color="white">
          {`#FIGS: ${document.num_figures}`}
        </Badge>
        <ModalityCountBadges
          countMapper={document.modalities_count}
          colorMapper={colorMapper}
          namesMapper={namesMapper}
        />
      </Box>
    </Box>
  )
}

export default SimpleResultCard
