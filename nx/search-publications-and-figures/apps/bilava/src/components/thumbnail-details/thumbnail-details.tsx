import {Box, Flex, HStack, Heading, chakra, Text} from '@chakra-ui/react'
import {useSize} from '@chakra-ui/react-use-size'
import {ImageExtras, ScatterDot} from '../../types'
import {colorsMapper} from '../../utils/mapper'
import {useEffect, useRef, useState} from 'react'
import {fetch_image_extras} from '../../api'

/* eslint-disable-next-line */
export interface ThumbnailDetailsProps {
  image: ScatterDot
  classifier: string
  labels: string[]
}

export function ThumbnailDetails({
  image,
  classifier,
  labels,
}: ThumbnailDetailsProps) {
  const [imageExtras, setImageExtras] = useState<ImageExtras | null>(null)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const dimensions = useSize(containerRef)

  useEffect(() => {
    const loadData = async () => {
      const extras = await fetch_image_extras(image.dbId, classifier)
      setImageExtras(extras)
    }
    loadData()
  }, [image])

  return (
    <Flex w="full" h="full" direction="column">
      <HStack w="full" h="90%">
        <Box w="50%" h="90%" ref={containerRef}>
          {dimensions ? (
            <Thumbnail image={image} dimensions={dimensions} />
          ) : null}
        </Box>
        <Box w="50%" h="90%" overflowY="scroll">
          <Heading size="md">Image Information</Heading>
          <Box>
            Ground Truth:{' '}
            <chakra.span color={colorsMapper[image.lbl]}>
              {image.lbl}
            </chakra.span>
          </Box>
          <Box>
            Prediction:{' '}
            <chakra.span color={colorsMapper[image.prd]}>
              {image.prd}
            </chakra.span>
          </Box>
          <Box>
            Full Ground Truth:{' '}
            {imageExtras ? (
              <chakra.span color={colorsMapper[imageExtras.fullLabel]}>
                {imageExtras.fullLabel}
              </chakra.span>
            ) : null}
          </Box>
          <Box>Source: {image.sr}</Box>
          <Box>Name: {imageExtras ? imageExtras.name : ''}</Box>
          <Box>Predictions:</Box>
          {imageExtras &&
            labels.map((key, i) => (
              <Box key={key}>
                {key}: {imageExtras.probs[i]}
              </Box>
            ))}
          <Heading size="md">Caption</Heading>
          {imageExtras ? (
            <Text>{imageExtras.caption}</Text>
          ) : (
            <Text>Image has no caption</Text>
          )}
        </Box>
      </HStack>

      <Box w="100%" h="10%">
        {/* {hasSiblings} */}
      </Box>
    </Flex>
  )
}

interface ThumbnailProps {
  image: ScatterDot
  dimensions: {width: number; height: number}
}

const Thumbnail = ({image, dimensions}: ThumbnailProps) => {
  const {w, h} = image
  const padding = 1
  const vertScale = (dimensions.width - padding) / h
  const horizScale = (dimensions.height - padding) / w
  const scale = Math.min(vertScale, horizScale)

  // const heatmap = path => `${path.slice(0, -4)}_${saliency}_${classifier}.png`
  return (
    <Flex
      w="full"
      h="full"
      alignContent="center"
      justifyContent="center"
      bg="blackAlpha.800"
      // p={padding / 2}
      position="relative"
    >
      <img
        src={image.uri}
        alt=""
        style={{
          width: `${scale * w - 2 * padding}px`,
          maxWidth: `${dimensions.width - 2 * padding}px`,
          height: `${scale * h - 2 * padding}px`,
          maxHeight: `${dimensions.height - 2 * padding}px`,
          margin: 'auto',
        }}
      />
      {/* {saliency && classifier && (
        <Flex
          w="full"
          h="full"
          position="absolute"
          alignItems="center"
          justifyContent="center"
        >
          <img
            src={`${IMAGES_PATH}/${heatmap(image.img_path)}`}
            alt=""
            style={{
              width: `${scale * width - 2 * padding}px`,
              maxWidth: `${contWidth - 2 * padding}px`,
              height: `${scale * height - 2 * padding}px`,
              maxHeight: `${contHeight - 2 * padding}px`,
              opacity: 0.5,
            }}
          />
        </Flex>
      )} */}
    </Flex>
  )
}

export default ThumbnailDetails
