import {Box, Tooltip} from '@chakra-ui/react'

/* eslint-disable-next-line */
export interface ImageViewerProps {
  src: string
  alt: string
  borderColor?: string
  bgColor?: string
  tooltipText?: string
}

export function ImageViewer({
  src,
  alt,
  borderColor,
  bgColor,
  tooltipText,
}: ImageViewerProps) {
  return (
    <Tooltip label={tooltipText ? tooltipText : ''}>
      <Box
        w="full"
        h="full"
        p={2}
        bgColor={bgColor ? bgColor : 'black'}
        border={borderColor ? `3px solid ${borderColor};` : undefined}
      >
        <img src={src} alt={alt} style={{margin: 'auto', maxHeight: '100%'}} />
      </Box>
    </Tooltip>
  )
}

export default ImageViewer
