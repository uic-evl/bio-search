import {Link, chakra, Badge, Box, Flex, Text} from '@chakra-ui/react'
import {LuceneDocument} from '../types/lucene-document'
import ModalityCountBadges from '../modality-count-badges/modality-count-badges'

/* eslint-disable-next-line */
export interface SimpleResultCardProps {
  document: LuceneDocument
  onClick: (arg1: number) => void
  selected: boolean
  colorMapper: {[id: string]: string}
  namesMapper: {[id: string]: string}
}

interface TitleProps {
  id: number
  title: string
  url: string
  selected: boolean
  onClick: (arg1: number) => void
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
        if (!selected) onClick(id)
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

  return (
    <Box
      pl={4}
      w="full"
      pt={1}
      mb={4}
      style={{boxShadow: selected ? '0 4px 8px 0 rgba(0,0,0,0.2)' : undefined}}
      background={selected ? 'white' : undefined}
    >
      <Flex>
        <Title
          title={document.title}
          selected={selected}
          id={document.id}
          url={`https://www.google.com/search?q=${document.url}`}
          onClick={onClick}
        />
      </Flex>
      <Text
        fontSize={'small'}
        noOfLines={5}
        dangerouslySetInnerHTML={{
          __html:
            year(document.publish_date) + '&nbsp;|&nbsp;' + document.abstract,
        }}
      ></Text>
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
