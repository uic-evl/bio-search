import {
  Button,
  useDisclosure,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Text,
} from '@chakra-ui/react'

export const About = () => {
  const {isOpen, onOpen, onClose} = useDisclosure()
  return (
    <>
      <Button size="xs" onClick={onOpen} ml={1} mr={1}>
        About
      </Button>

      <Modal isOpen={isOpen} onClose={onClose} size="4xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>About this project</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Text>
              This NIH National Library of Medicine (NLM)-sponsored project is
              being developed by a group of researchers at the University of
              Delaware and the University of Illinois Chicago, led by MPIs Prof.
              Shatkay and{' '}
              <Text as="u">
                <a
                  href="https://www.evl.uic.edu/marai/home/index.html"
                  target="_blank"
                >
                  Prof. Marai
                </a>
              </Text>
              , in collaboration with several biocuration groups at U Delaware,
              Caltech, and Jackson Labs.
            </Text>
            <Text>
              This specific project instantiation supports searching biomedical
              documents a subset of the CORD-19 collection based on text AND
              images. It retrieves documents that contain both the desired text
              and desired image modalities (such as “cell” and “microscopy”) and
              presents the document information along with the relevant images
              in those documents. Other search tools like Google Scholar or
              PubMed only use text data when retrieving documents and only show
              text metadata when showing the results. In contrast, our system
              enhances the search with image information and enhances the result
              presentation with image information.
            </Text>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  )
}
