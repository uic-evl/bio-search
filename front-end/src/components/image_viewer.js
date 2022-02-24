import {Box, Tooltip} from '@chakra-ui/react'

export const ImageViewer = ({src, borderColor, bgColor, label}) => {
  return (
    <Tooltip label={label ? label : ''}>
      <Box
        w="full"
        h="full"
        p={2}
        bgColor={bgColor ? bgColor : 'black'}
        border={borderColor ? `3px solid ${borderColor};` : null}
      >
        <img
          src={src}
          alt="todo"
          style={{
            margin: 'auto',
            maxHeight: '100%',
          }}
        />
      </Box>
    </Tooltip>
  )
}
