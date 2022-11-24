import {useState} from 'react'
import {Document} from '../types/document'
import useDimensions from 'react-cool-dimensions'
import {Box, Flex} from '@chakra-ui/react'

/* eslint-disable-next-line */
export interface FiguresPerPageViewerProps {
  document: Document
}

export function FiguresPerPageViewer({document}: FiguresPerPageViewerProps) {
  const [pageIdx, setPageIdx] = useState(0) // page idx in array, not page number
  const [figIdx, setFigIdx] = useState(0) // fig idx in array
  const {observe, height} = useDimensions({
    polyfill: ResizeObserver,
  })

  return (
    <Box w="full" h="full" bgColor="gray.100" p={2}>
      <Flex w="full" h="full" mt={1} ref={observe}></Flex>
    </Box>
  )
}

export default FiguresPerPageViewer
