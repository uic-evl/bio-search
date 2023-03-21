import {Box, Flex} from '@chakra-ui/react'
import {HierarchyRectangularNode} from 'd3-hierarchy'
import {ScatterDot, SpiralThumbnail} from '../../types'
import {LabelCircleIcon} from '../icons/icons'
import {colorsMapper} from '../../utils/mapper'
import styles from './html-image-thumbnail.module.css'

// for hierarchical values, x & y values are relative to parent
const top = (d: HierarchyRectangularNode<SpiralThumbnail>) => {
  if (!d.parent) return d.y0
  return d.depth > 1 ? d.parent.y0 + d.y0 : d.y0
}

const left = (d: HierarchyRectangularNode<SpiralThumbnail>) => {
  if (!d.parent) return d.x0
  return d.depth > 1 ? d.parent.x0 + d.x0 : d.x0
}

export interface HtmlImageThumbnailProps {
  imageNode: HierarchyRectangularNode<SpiralThumbnail>
  objectFit: string
  selected: boolean
  onSelectThumbnail: () => void
}

export function HtmlImageThumbnail({
  imageNode,
  objectFit,
  selected,
  onSelectThumbnail,
}: HtmlImageThumbnailProps) {
  const imgWidth = imageNode.data.w || 0
  const imgHeight = imageNode.data.h || 0
  const container = {
    width: imageNode.x1 - imageNode.x0,
    height: imageNode.y1 - imageNode.y0,
  }

  const handleOnClickImage = () => {
    onSelectThumbnail()
  }

  return (
    <Box
      position="absolute"
      w={container.width}
      h={container.height}
      top={top(imageNode)}
      left={left(imageNode)}
      backgroundColor="black"
      border={'1px solid #2a2a2a'}
    >
      <Box w="full" h="full" border={selected ? '1px solid red' : ''}>
        <ScaledImage
          imgPath={imageNode.data.uri || ''}
          size={{width: imgWidth, height: imgHeight}}
          container={container}
          opacity={0.5}
          padding={2}
          objectFit={objectFit}
          onClick={handleOnClickImage}
        />
        <LabelCircleIcon
          fill={colorsMapper[imageNode.data.lbl]}
          stroke={colorsMapper[imageNode.data.prd]}
          size={{width: 14, height: 14}}
        />
      </Box>
    </Box>
  )
}

interface ScaledImageProps {
  imgPath: string
  container: {width: number; height: number}
  size: {width: number; height: number}
  padding: number
  opacity: number
  objectFit: string
  onClick: () => void
}

const ScaledImage = ({
  imgPath,
  container,
  size,
  padding,
  opacity,
  objectFit,
  onClick,
}: ScaledImageProps) => {
  const verticalScale = (container.height - padding) / size.height
  const horizontalScale = (container.width - padding) / size.width
  const scale = Math.min(verticalScale, horizontalScale)

  return (
    <Flex
      position="relative"
      w="full"
      h="full"
      alignItems="center"
      justifyContent="center"
      _hover={{
        cursor: 'pointer',
      }}
    >
      <img
        src={imgPath}
        alt=""
        style={{
          objectFit: objectFit === 'fit' ? 'fill' : 'cover',
          width:
            objectFit === 'cover'
              ? `${container.width - 2 * padding}px`
              : `${scale * size.width - 2 * padding}px`,
          maxWidth: `${container.width - 2 * padding}px`,
          height:
            objectFit === 'cover'
              ? `${container.height - 2 * padding}px`
              : `${scale * size.height - 2 * padding}px`,
          maxHeight: `${container.height - 2 * padding}px`,
        }}
        onClick={onClick}
      />
    </Flex>
  )
}

export default HtmlImageThumbnail
