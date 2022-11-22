import {useState} from 'react'
import {Box, Flex, Text, Center, Button, chakra, Spacer} from '@chakra-ui/react'
import {ImageViewer} from '../image_viewer'
import {Long2ColorCord} from '../../utils/modalityMap'
import ImageBoundingBoxViewer from '../image/image_bbox_viewer'
import useDimensions from 'react-cool-dimensions'

const API_ENDPOINT = process.env.REACT_APP_IMAGES_ENDPOINT
const SUBFIGURES_ENDPOINT = process.env.REACT_APP_SUBIMAGES_ENDPOINT

const EnhancedSurrogate = ({document}) => {
  const [pagePosition, setPagePosition] = useState(0)
  const [figNumber, setFigNumber] = useState(0)
  const {observe, height} = useDimensions({
    polyfill: ResizeObserver,
  })

  const handleClickPrevious = (pageIdx, figIdx) => {
    const shouldChangePage = figIdx === 0

    let newPageIdx = pageIdx
    let newFigIdx = figIdx - 1
    if (shouldChangePage) {
      newPageIdx = pageIdx === 0 ? document.pages.length - 1 : pageIdx - 1
      newFigIdx = document.pages[newPageIdx].figures.length - 1
    }

    setPagePosition(newPageIdx)
    setFigNumber(newFigIdx)
  }

  const handleClickNext = (pageIdx, figIdx) => {
    const shouldChangePage =
      figIdx === document.pages[pageIdx].figures.length - 1

    let newPageIdx = pageIdx
    let newFigIdx = figIdx + 1
    if (shouldChangePage) {
      newPageIdx = pageIdx === document.pages.length - 1 ? 0 : pageIdx + 1
      newFigIdx = 0
    }

    setPagePosition(newPageIdx)
    setFigNumber(newFigIdx)
  }

  return (
    <Box w="full" h="full" bgColor="gray.100" p={2}>
      <Flex w="full" h="calc(100%)" mt={1} ref={observe}>
        {document && (
          <SurrogatePage
            page={document.pages[pagePosition]}
            pageIdx={pagePosition}
            onClickPrevious={handleClickPrevious}
            onClickNext={handleClickNext}
            pmcid={document.pmcid}
            numberPages={document.pages.length}
            figureNumber={figNumber}
            numberFiguresInPage={document.pages[pagePosition].figures.length}
          />
        )}
        {document && height > 0 && (
          <SurrogateFigure
            document={document}
            page={document.pages[pagePosition]}
            figureNumber={figNumber}
            maxHeight={height}
          />
        )}
      </Flex>
    </Box>
  )
}

const SurrogatePage = ({
  page,
  pageIdx,
  onClickPrevious,
  onClickNext,
  pmcid,
  numberPages,
  figureNumber,
  numberFiguresInPage,
}) => {
  const paddedPage = page.page.toString().padStart(6, 0)
  const pageUrl = `${pmcid}/${pmcid}-${paddedPage}.png`

  return (
    <Box h="full" w="30%" mr={1}>
      <Box h="calc(100% - 35px)">
        {document && <ImageViewer src={`${API_ENDPOINT}/${pageUrl}`} />}
      </Box>
      <Flex w="full" h="35px" mt={1}>
        <Button
          colorScheme="blue"
          size="xs"
          ml={1}
          onClick={() => onClickPrevious(pageIdx, figureNumber)}
        >
          &#60;
        </Button>

        <Spacer />
        <chakra.span fontSize="sm">
          pg.&nbsp;{page.page} - fig. {figureNumber + 1}/{numberFiguresInPage}
        </chakra.span>
        <Spacer />

        <Button
          colorScheme="blue"
          size="xs"
          mr={1}
          onClick={() => onClickNext(pageIdx, figureNumber)}
        >
          &#62;
        </Button>
      </Flex>
    </Box>
  )
}

const FigureWBboxes = ({
  documentId,
  pageNumber,
  noFigure,
  subfigures,
  maxH,
  url,
}) => {
  const figureURL = `${SUBFIGURES_ENDPOINT}/${url}`

  const sfBboxes = subfigures.map(sf => ({
    name: sf.name,
    bbox: sf.bbox ? sf.bbox.map(el => el * 1000) : null,
    type: sf.type,
    color: Long2ColorCord[sf.type],
  }))

  return (
    <Box minH={`${maxH}px`} maxH={`${maxH}px`} w="full">
      <ImageBoundingBoxViewer img_src={figureURL} bboxes={sfBboxes} />
    </Box>
  )
}

const SurrogateFigure = ({document, page, maxHeight, figureNumber}) => {
  const figure = page.figures[figureNumber]
  const figureWidth = figure.caption.length > 1 ? 50 : 100

  return (
    <Flex h="full" w="full">
      <Box w={`${figureWidth}%`} minH="calc(100% - 10px)">
        <FigureWBboxes
          pageNumber={figure.page}
          noFigure={figure.no_subfig}
          subfigures={figure.subfigures}
          documentId={document.cord_uid}
          maxH={maxHeight}
          url={figure.url}
        />
      </Box>
      {figureWidth < 100 && (
        <Box
          w={`${100 - figureWidth}%`}
          bgColor="gray.100"
          p={2}
          pb={0}
          overflowY="auto"
        >
          <Text fontSize={'sm'}>{figure.caption}</Text>
        </Box>
      )}
    </Flex>
  )
}

export {EnhancedSurrogate}
