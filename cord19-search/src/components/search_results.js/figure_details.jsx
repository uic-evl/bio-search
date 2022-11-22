import {useState} from 'react'
import {Box, Flex, Text, Center, Button} from '@chakra-ui/react'
import {ImageViewer} from '../image_viewer'
import {Long2ColorCord} from '../../utils/modalityMap'
import ImageBoundingBoxViewer from '../image/image_bbox_viewer'
import useDimensions from 'react-cool-dimensions'

const API_ENDPOINT = process.env.REACT_APP_IMAGES_ENDPOINT
const SUBFIGURES_ENDPOINT = process.env.REACT_APP_SUBIMAGES_ENDPOINT

const EnhancedSurrogate = ({document}) => {
  const [pagePosition, setPagePosition] = useState(0)
  const {observe, height} = useDimensions({
    polyfill: ResizeObserver,
  })

  const handleClickPrevious = pageIdx => {
    const idx = pageIdx === 0 ? document.pages.length - 1 : pageIdx - 1
    setPagePosition(idx)
  }

  const handleClickNext = pageIdx => {
    const idx = pageIdx === document.pages.length - 1 ? 0 : pageIdx + 1
    setPagePosition(idx)
  }

  return (
    <Box w="full" h="full" bgColor="gray.100" p={2}>
      <Flex w="full" h="calc(100% - 24px)" mt={1} ref={observe}>
        {document && (
          <SurrogatePage
            page={document.pages[pagePosition]}
            pageIdx={pagePosition}
            onClickPrevious={handleClickPrevious}
            onClickNext={handleClickNext}
            pmcid={document.pmcid}
          />
        )}
        {document && height > 0 && (
          <SurrogateFigure
            document={document}
            page={document.pages[pagePosition]}
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
}) => {
  const paddedPage = page.page.toString().padStart(6, 0)
  const pageUrl = `${pmcid}/${pmcid}-${paddedPage}.png`

  return (
    <Box h="full" w="30%" mr={1}>
      <Box h="calc(100% - 35px)">
        {document && <ImageViewer src={`${API_ENDPOINT}/${pageUrl}`} />}
      </Box>
      <Box w="full" h="35px">
        <Center p={2}>
          <Button
            colorScheme="blue"
            size="sm"
            mr={1}
            onClick={() => onClickPrevious(pageIdx)}
          >
            Prev
          </Button>
          <span>pg.&nbsp;{page.page}</span>
          <Button
            colorScheme="blue"
            size="sm"
            ml={1}
            onClick={() => onClickNext(pageIdx)}
          >
            Next
          </Button>
        </Center>
      </Box>
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

const SurrogateFigure = ({document, page, maxHeight}) => {
  const [figureNumber, setFigureNumber] = useState(0)
  const figure = page.figures[figureNumber]
  const numberFigures = page.figures.length
  const figureWidth = figure.caption.length > 0 ? 50 : 100

  const handlePrevFigure = () => {
    const idx = figureNumber === 0 ? numberFigures - 1 : figureNumber - 1
    setFigureNumber(idx)
  }

  const handleNextFigure = () => {
    const idx = figureNumber === numberFigures - 1 ? 0 : figureNumber + 1
    setFigureNumber(idx)
  }

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
        <Flex direction={'column'} w={`${100 - figureWidth}%`}>
          <Box
            w="full"
            h={numberFigures > 1 ? '90%' : 'full'}
            bgColor="gray.100"
            p={2}
            pb={0}
            overflowY="auto"
          >
            <Text fontSize={'sm'}>{figure.caption}</Text>
          </Box>
          {numberFigures > 1 && (
            <Center>
              <Button
                colorScheme={'blue'}
                variant={'outline'}
                size="xs"
                mr={2}
                onClick={handlePrevFigure}
              >
                Prev Figure
              </Button>
              <Button
                colorScheme={'blue'}
                variant={'outline'}
                size="xs"
                onClick={handleNextFigure}
              >
                Next Figure
              </Button>
            </Center>
          )}
        </Flex>
      )}
    </Flex>
  )
}

export {EnhancedSurrogate}
