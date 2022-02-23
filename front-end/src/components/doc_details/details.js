import {useEffect, useState} from 'react'
import {Box, Flex, Image, Text, Center, Button} from '@chakra-ui/react'
import useDimensions from 'react-cool-dimensions'
import {ResizeObserver} from '@juggle/resize-observer'

const API_ENDPOINT = process.env.REACT_APP_IMAGES_ENDPOINT

export const DetailsContainer = ({document}) => {
  return (
    <Box w="full" h="calc((100vh - 150px)/2)" p={1}>
      <Box w="full" h="full" bgColor="gray.400" p={4}>
        <Text h="20px">{document.title}</Text>
        <Flex w="full" h="calc(100% - 20px)">
          <Box h="full" w="30%">
            {document && (
              <FirstPage
                title={document.title}
                url={`${API_ENDPOINT}/${document.first_page}`}
              />
            )}
          </Box>
          <Box h="full" w="70%" pt={3}>
            {document && document.figures && (
              <FigureCarrousel figures={document.figures} />
            )}
          </Box>
        </Flex>
      </Box>
    </Box>
  )
}

const FirstPage = ({url, title}) => {
  return (
    <Box h="100%" p={3}>
      <Image src={url} alt={`first page from ${title}`} objectFit="cover" />
    </Box>
  )
}

const FigureCarrousel = ({figures}) => {
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

      setCardDimensions({w: newCardWidth, h: newCardHeight})
      setGap({
        w: newGapW / (figures.length - 1),
        h: newGapH / (figures.length - 1),
      })
      setPositions(Array.from(Array(figures.length).keys()))
    }
  }, [width, height, figures.length])

  return (
    <Box w="full" h="full">
      <Box
        ref={observe}
        w="full"
        h="90%"
        bgColor="blackAlpha.300"
        position="relative"
      >
        {figures &&
          cardDimensions &&
          gap &&
          positions &&
          figures.map((fig, idx) => (
            <FigureCard
              figure={fig}
              position={positions[idx]}
              dimensions={cardDimensions}
              container={{w: width, h: height}}
              gap={gap}
              totalFigures={figures.length}
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
  figure,
  position,
  dimensions,
  gap,
  container,
  totalFigures,
}) => {
  const top = container.h - dimensions.h - position * gap.h
  const left = container.w - dimensions.w - position * gap.w
  const zIndex = totalFigures - position

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
          {position} - {figure}
        </Box>
        <Box w="80%" h="full">
          <Flex w="full" minH="calc(100% - 20px)">
            <Box w="50%" minH="calc(100% - 20px)"></Box>
            <Box w="50%" minH="calc(100% - 20px)" bgColor={'green'}></Box>
          </Flex>
          <Box w="full" h="20px" bgColor={'blackAlpha.900'}></Box>
        </Box>
      </Flex>
    </Box>
  )
}
