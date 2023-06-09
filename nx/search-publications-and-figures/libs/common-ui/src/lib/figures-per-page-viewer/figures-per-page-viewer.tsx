import {useState} from 'react'
import {Document, Page} from '../types/document'
import useDimensions from 'react-cool-dimensions'
import {Box, Flex} from '@chakra-ui/react'
import PageThumbnailViewer from '../page-thumbnail-viewer/page-thumbnail-viewer'
import FigureBboxCaptionCard from '../figure-bbox-caption-card/figure-bbox-caption-card'
import {LuceneCaption} from '../types'

/* eslint-disable-next-line */
export interface FiguresPerPageViewerProps {
  document: Document
  colorsMapper: {[id: string]: string}
  figuresBaseUrl: string
  getPageUrl: (arg1: Document, arg2: Page) => string
  captionHits: LuceneCaption[]
}

export function FiguresPerPageViewer({
  document,
  colorsMapper,
  figuresBaseUrl,
  getPageUrl,
  captionHits,
}: FiguresPerPageViewerProps) {
  const [pageIdx, setPageIdx] = useState(0) // page idx in array, not page number
  const [figIdx, setFigIdx] = useState(0) // fig idx in array
  const {observe, height} = useDimensions({
    polyfill: ResizeObserver,
  })

  const handleClickPrevious = (pageIdx: number, figIdx: number) => {
    const shouldChangePage = figIdx === 0

    let newPageIdx = pageIdx
    let newFigIdx = figIdx - 1
    if (shouldChangePage) {
      newPageIdx = pageIdx === 0 ? document.pages.length - 1 : pageIdx - 1
      newFigIdx = document.pages[newPageIdx].figures.length - 1
    }

    setPageIdx(newPageIdx)
    setFigIdx(newFigIdx)
  }

  const handleClickNext = (pageIdx: number, figIdx: number) => {
    const shouldChangePage =
      figIdx === document.pages[pageIdx].figures.length - 1

    let newPageIdx = pageIdx
    let newFigIdx = figIdx + 1
    if (shouldChangePage) {
      newPageIdx = pageIdx === document.pages.length - 1 ? 0 : pageIdx + 1
      newFigIdx = 0
    }

    setPageIdx(newPageIdx)
    setFigIdx(newFigIdx)
  }

  return (
    <Box w="full" h="full" bgColor="gray.100" p={2}>
      <Flex w="full" h="full" mt={1} ref={observe}>
        <Box w="30%" h="full">
          <PageThumbnailViewer
            currPageIdx={pageIdx}
            currPageNumber={document.pages[pageIdx].page}
            currFigureIdx={figIdx}
            numberFiguresInPage={document.pages[pageIdx].figures.length}
            pageUrl={getPageUrl(document, document.pages[pageIdx])}
            onClickPrevious={handleClickPrevious}
            onClickNext={handleClickNext}
          />
        </Box>
        {height > 0 && (
          <FigureBboxCaptionCard
            figure={document.pages[pageIdx].figures[figIdx]}
            colorsMapper={colorsMapper}
            baseUrlEndpoint={figuresBaseUrl}
            maxHeight={height}
            captionHits={captionHits}
          />
        )}
      </Flex>
    </Box>
  )
}

export default FiguresPerPageViewer
