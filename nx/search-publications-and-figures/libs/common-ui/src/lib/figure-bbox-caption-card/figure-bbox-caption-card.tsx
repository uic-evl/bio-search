import {Figure} from '../types/document'
import {Flex, Box, Text} from '@chakra-ui/react'
import FigureBboxViewer from '../figure-bbox-viewer/figure-bbox-viewer'

/* eslint-disable-next-line */
export interface FigureBboxCaptionCardProps {
  figure: Figure
  colorsMapper: {[id: string]: string}
  baseUrlEndpoint: string
  maxHeight: number
}

interface CaptionProps {
  width: number
  caption: string
}

const Caption = ({width, caption}: CaptionProps) => (
  <Box
    w={`${100 - width}%`}
    maxW={`${100 - width}%`}
    bgColor="gray.100"
    p={2}
    pb={0}
    overflowY="auto"
    overflowX="auto"
  >
    <Text fontSize={'sm'}>{caption}</Text>
  </Box>
)

export function FigureBboxCaptionCard({
  figure,
  colorsMapper,
  baseUrlEndpoint,
  maxHeight,
}: FigureBboxCaptionCardProps) {
  const figPanelWidth = figure.caption.length > 1 ? 50 : 100
  const subfigureBboxes = figure.subfigures.map(sf => {
    let scale = 1
    // bboxes that need scaling are typically very small
    // TODO standarize the db to avoid this scaling
    if (sf.bbox) {
      const sum = sf.bbox.reduce((a, b) => a + b, 0)
      if (sum < 10) scale = 1000
    }

    return {
      bbox: sf.bbox ? sf.bbox.map(el => el * scale) : null,
      type: sf.type,
      color: colorsMapper[sf.type],
    }
  })
  const figureUrl = `${baseUrlEndpoint}/${figure.url}`

  return (
    <Flex h="full" w="full">
      <Box w={`${figPanelWidth}%`} minH="calc(100% - 10px)">
        <Box minH={`${maxHeight}px`} maxH={`${maxHeight}px`} w="full">
          <FigureBboxViewer imageSrc={figureUrl} bboxes={subfigureBboxes} />
        </Box>
      </Box>
      {figPanelWidth < 100 && (
        <Caption width={figPanelWidth} caption={figure.caption} />
      )}
    </Flex>
  )
}

export default FigureBboxCaptionCard
