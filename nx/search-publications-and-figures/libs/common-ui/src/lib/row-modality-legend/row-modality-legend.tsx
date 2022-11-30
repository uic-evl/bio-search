import {
  Badge,
  Flex,
  Text,
  Spacer,
  Button,
  useDisclosure,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
} from '@chakra-ui/react'

/* eslint-disable-next-line */
export interface RowModalityLegendProps {
  modalities: string[]
  colorsMapper: {[name: string]: string}
  namesMapper: {[name: string]: string}
  taxonomyImage: React.ReactNode
}

export function RowModalityLegend({
  modalities,
  colorsMapper,
  namesMapper,
  taxonomyImage,
}: RowModalityLegendProps) {
  const {isOpen, onOpen, onClose} = useDisclosure()

  return (
    <>
      <Flex direction="row" alignItems="center" pl={4} pr={4} mb={1}>
        <Text fontSize="sm" mr={1}>
          Modalities:
        </Text>
        {modalities.map(el => (
          <Badge
            key={`lg-short-${el}`}
            mr={1}
            background={colorsMapper[el]}
            color="black"
          >
            {namesMapper[el].substring(0, 10)}
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
          <ModalBody>{taxonomyImage}</ModalBody>
        </ModalContent>
      </Modal>
    </>
  )
}

export default RowModalityLegend
