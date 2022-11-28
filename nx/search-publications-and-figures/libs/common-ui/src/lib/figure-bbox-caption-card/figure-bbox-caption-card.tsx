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
  <Box w={`${100 - width}%`} bgColor="gray.100" p={2} pb={0} overflowY="auto">
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
  // TODO: some bboxes may not need to be scaled by 1000
  const subfigureBboxes = figure.subfigures.map(sf => ({
    bbox: sf.bbox ? sf.bbox.map(el => el * 1000) : null,
    type: sf.type,
    color: colorsMapper[sf.type],
  }))
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