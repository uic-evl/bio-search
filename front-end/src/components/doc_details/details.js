import {useEffect, useState} from 'react'
import {Box, Flex, Image, Text, Center, Button} from '@chakra-ui/react'
import {ImageViewer} from '../image_viewer'
import useDimensions from 'react-cool-dimensions'
import {ResizeObserver} from '@juggle/resize-observer'

const API_ENDPOINT = process.env.REACT_APP_IMAGES_ENDPOINT

export const DetailsContainer = ({document}) => {
  return (
    <Box w="full" h="calc((100vh - 150px)/2)" p={1}>
      <Box w="full" h="full" bgColor="gray.400" p={4}>
        <Text h="20px">{document.title}</Text>
        <Flex w="full" h="calc(100% - 24px)" mt={1}>
          <Box h="full" w="30%">
            {document && (
              <FirstPage
                title={document.title}
                url={`${API_ENDPOINT}/${document.first_page}`}
              />
            )}
          </Box>
          <Box h="full" w="70%" ml={1}>
            {document && document.pages && (
              <FigureCarrousel pages={document.pages} />
            )}
          </Box>
        </Flex>
      </Box>
    </Box>
  )
}

const FirstPage = ({url, title}) => {
  return (
    <ImageViewer src={url} />
    // <Box h="100%" p={3}>
    //   <Image src={url} alt={`first page from ${title}`} objectFit="cover" />
    // </Box>
  )
}

const FigureCarrousel = ({pages}) => {
  const [positions, setPositions] = useState(null)
  const [cardDimensions, setCardDimensions] = useState(null)
  const [gap, setGap] = useState(null)
  const {observe, width, height} = useDimensions({
    polyfill: ResizeObserver,
  })

  const proportion = 0.8

  const leftRotate = arr => {
    let newArr = [...arr]
    let tmp = newArr[0]
    for (let i = 0; i < newArr.length - 1; i++) newArr[i] = newArr[i + 1]
    newArr[arr.length - 1] = tmp
    return newArr
  }

  const rightRotate = arr => {
    let newArr = [...arr]
    let tmp = newArr[arr.length - 1]
    for (let i = newArr.length - 1; i > 0; i--) newArr[i] = newArr[i - 1]
    newArr[0] = tmp
    return newArr
  }

  const increment = () => {
    const newPositions = rightRotate(positions)
    setPositions(newPositions)
  }

  const decrement = () => {
    const newPositions = leftRotate(positions)
    setPositions(newPositions)
  }

  useEffect(() => {
    if (width > 0 && height > 0) {
      const newCardWidth = width * proportion
      const newCardHeight = height * proportion
      const newGapW = width - newCardWidth
      const newGapH = height - newCardHeight
      const numberPages = Object.keys(pages).length

      setCardDimensions({w: newCardWidth, h: newCardHeight})
      setGap({
        w: newGapW / (numberPages - 1),
        h: newGapH / (numberPages - 1),
      })
      setPositions(Array.from(Array(numberPages).keys()))
    }
  }, [width, height, pages])

  return (
    <Box w="full" h="full">
      <Box
        ref={observe}
        w="full"
        h="90%"
        bgColor="blackAlpha.300"
        position="relative"
      >
        {pages &&
          cardDimensions &&
          gap &&
          positions &&
          pages.map((page, idx) => (
            <FigureCard
              key={idx}
              page={page}
              position={positions[idx]}
              dimensions={cardDimensions}
              container={{w: width, h: height}}
              gap={gap}
              totalPages={pages.length}
            />
          ))}
      </Box>
      <Box w="full" h="10%">
        <Center p={2}>
          <Button onClick={decrement} mr={2}>
            Prev
          </Button>
          <Button onClick={increment}>Next</Button>
        </Center>
      </Box>
    </Box>
  )
}

const FigureCard = ({
  page,
  position,
  dimensions,
  gap,
  container,
  totalPages,
}) => {
  const [current, setCurrent] = useState(page.figures[0])
  const top = container.h - dimensions.h - position * gap.h
  const left = container.w - dimensions.w - position * gap.w
  const zIndex = totalPages - position
  const subfigsWidth = current.caption.length > 0 ? 50 : 100

  return (
    <Box
      position="absolute"
      w={dimensions.w}
      h={dimensions.h}
      top={top}
      left={left}
      bgColor="gold"
      border="1px solid black"
      zIndex={zIndex}
    >
      <Flex w="full" h="full">
        <Box h="full" w="20%" bgColor={'blackAlpha.700'}>
          {/* {page.page} */}
          <ImageViewer src={`${API_ENDPOINT}/${page.page_url}`} />
        </Box>
        <Box w="80%" h="full">
          <Flex w="full" minH="calc(100% - 20px)">
            <Box w={`${subfigsWidth}%`} minH="calc(100% - 20px)"></Box>
            <Box
              w={`${100 - subfigsWidth}%`}
              minH="calc(100% - 20px)"
              bgColor="gray.100"
              p={2}
            >
              <Text fontSize={'small'} noOfLines={13}>
                {current.caption}
              </Text>
            </Box>
          </Flex>
          <Box w="full" h="20px" bgColor={'blackAlpha.900'}></Box>
        </Box>
      </Flex>
    </Box>
  )
}
