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
  Link,
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
        <ModalContent pb="4">
          <ModalHeader>About this project</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Text mb="1">
              This NIH National Library of Medicine (NLM)-sponsored project is
              being developed by a group of researchers at the University of
              Delaware and the University of Illinois Chicago, led by MPIs{' '}
              <Text as="u" color={'blue.700'}>
                <a
                  href="https://en.wikipedia.org/wiki/Hagit_Shatkay"
                  target="_blank"
                >
                  Prof. Shatkay
                </a>
              </Text>{' '}
              and{' '}
              <Text as="u" color={'blue.700'}>
                <a
                  href="https://www.evl.uic.edu/marai/home/index.html"
                  target="_blank"
                >
                  Prof. Marai
                </a>
              </Text>{' '}
              (NIH NLM R01LM012527), in collaboration with several biocuration
              groups at the University of Delaware, Caltech, and Jackson Labs.
              The system is described in this paper:
            </Text>
            <Text mb="2" backgroundColor={'gray.200'} p="4">
              J. Trelles, C. Arighi, H. Shatkay, G.E. Marai.{' '}
              <i>"Enhancing biomedical search interfaces with images"</i>.
              Bioinformatics Advances, pp. 1-8, 2023
            </Text>
            <Text mb="1">
              This specific project instantiation supports searching biomedical
              documents in a subset of the CORD-19 collection based on text AND
              images. It retrieves documents that contain both the desired text
              and desired image modalities (such as “cell” and “microscopy”) and
              presents the document information along with the relevant images
              in those documents. Other search tools like Google Scholar or
              PubMed only use text data when retrieving documents and only show
              text metadata when showing the results. In contrast, our system
              enhances the search with image information and enhances the result
              presentation with image information.
            </Text>
            <Text>
              The main contributors to this software system, in addition to the
              PIs, are:{' '}
              <Text as="u" color={'blue.700'}>
                <a href="http://www.juantrelles.com" target="_blank">
                  Juan Trelles
                </a>
              </Text>{' '}
              (University of Illinois Chicago, main design, development, and
              deployment),{' '}
              <Text as="u" color="blue.700">
                <a
                  href="https://bioinformatics.udel.edu/people/cecilia-arighi-phd/"
                  target="_blank"
                >
                  Prof. Cecilia Arighi
                </a>
              </Text>{' '}
              (biocuration taxonomy, testing plan), and{' '}
              <Text as="u" color="blue.700">
                <a href="https://www.eecis.udel.edu/~pengyuan/" target="_blank">
                  Dr. Pengyuan Li
                </a>
              </Text>{' '}
              (University of Delaware, image tagging). The system is hosted and
              maintained by the{' '}
              <Text as="u" color="blue.700">
                <a href="https://www.evl.uic.edu/" target="_blank">
                  Electronic Visualization Laboratory
                </a>
              </Text>{' '}
              (University of Illinois Chicago).
            </Text>
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  )
}
