import {Box, Flex, Button, Spacer, chakra} from '@chakra-ui/react'
import ImageViewer from '../image-viewer/image-viewer'

/* eslint-disable-next-line */
export interface PageThumbnailViewerProps {
  currPageIdx: number
  currPageNumber: number
  onClickPrevious: (arg1: number, arg2: number) => void
  onClickNext: (arg1: number, arg2: number) => void
  numberFiguresInPage: number
  currFigureIdx: number
  pageUrl: string
}

export function PageThumbnailViewer({
  currPageIdx,
  currPageNumber,
  onClickPrevious,
  onClickNext,
  numberFiguresInPage,
  currFigureIdx,
  pageUrl,
}: PageThumbnailViewerProps) {
  return (
    <Box w="full" h="full">
      <Box h="calc(100% - 35px)">
        <ImageViewer src={pageUrl} alt={''} />
      </Box>
      <Flex w="full" h="35px" mt={1}>
        <Button
          colorScheme="blue"
          size="xs"
          ml={1}
          onClick={() => onClickPrevious(currPageIdx, currFigureIdx)}
        >
          &#60;
        </Button>

        <Spacer />
        <chakra.span fontSize="sm">
          pg.&nbsp;{currPageNumber} - fig. {currFigureIdx + 1}/
          {numberFiguresInPage}
        </chakra.span>
        <Spacer />

        <Button
          colorScheme="blue"
          size="xs"
          mr={1}
          onClick={() => onClickNext(currPageIdx, currFigureIdx)}
        >
          &#62;
        </Button>
      </Flex>
    </Box>
  )
}

export default PageThumbnailViewer
