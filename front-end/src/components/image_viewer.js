import {Box} from '@chakra-ui/react'

export const ImageViewer = ({src}) => {
  return (
    <Box w="full" h="full" p={2} bgColor="black">
      <img
        src={src}
        alt="todo"
        style={{
          margin: 'auto',
          maxHeight: '100%',
        }}
      />
    </Box>
  )
}
