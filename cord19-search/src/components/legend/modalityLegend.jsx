import {CordToName, Long2ColorCord} from '../../utils/modalityMap'
import {Flex, Text, Badge} from '@chakra-ui/react'

export const ModalityLegend = () => {
  const modalities = Object.keys(Long2ColorCord).filter(el => !el.includes('.'))

  return (
    <Flex direction={'row'} alignItems="center" pl={4} pr={4} mb={1}>
      <Text fontSize="sm" mr={1}>
        Modalities:
      </Text>
      {modalities.map(el => (
        <Badge
          key={`lg-${el}`}
          mr={1}
          background={Long2ColorCord[el]}
          color="black"
        >
          {CordToName[el]}
        </Badge>
      ))}
    </Flex>
  )
}
