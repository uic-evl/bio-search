import {Code2Long, Long2Color} from '../../utils/modalityMap'
import {
  Flex,
  Text,
  Badge,
  Spacer,
  Button,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalBody,
  ModalCloseButton,
  ModalHeader,
} from '@chakra-ui/react'
import {Taxonomy} from '../taxonomy/taxonomy'

export const ModalityLegend = () => {
  const {isOpen, onOpen, onClose} = useDisclosure()
  const modalities = Object.keys(Code2Long)

  return (
    <>
      <Flex direction={'row'} alignItems="center" pl={4} pr={4} mb={1}>
        <Text fontSize="sm" mr={1}>
          Modalities:
        </Text>
        {modalities.map(el => (
          <Badge
            key={`lg-${el}`}
            mr={1}
            background={Long2Color[Code2Long[el]]}
            color="black"
          >
            {Code2Long[el].substring(0, 10)}
          </Badge>
        ))}
        <Spacer />
        <Button size="xs" variant={'link'} onClick={onOpen}>
          see the whole taxonomy here
        </Button>
      </Flex>

      <Modal isOpen={isOpen} onClose={onClose} size="4xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Taxonomy</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Taxonomy />
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  )
}
