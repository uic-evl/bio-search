import {
  Button,
  Box,
  useDisclosure,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalContent,
  ModalHeader,
  ModalOverlay,
  Text,
  UnorderedList,
  ListItem,
  Link,
} from '@chakra-ui/react'

import {ExternalLinkIcon} from '@chakra-ui/icons'

interface ExplanationProps {
  url: string
}

const Explanation = ({url}: ExplanationProps) => (
  <Box>
    <Box mb={2}>
      <Link href={url} isExternal>
        Inteface tutorial
        <ExternalLinkIcon ml="3px" />
      </Link>
    </Box>
    <Text>
      The following sections explain the behavior of the search input box, which
      only support full-text queries over titles, abstracts and full text.
    </Text>
    <Text fontWeight={'bold'} mt={2}>
      1. Simple search:
    </Text>
    <UnorderedList>
      <ListItem>
        A search using the sample keyword{' '}
        <i>
          <b>kidney</b>
        </i>{' '}
        will search for matching titles and abstracts containing such word.
      </ListItem>
      <ListItem>
        When using multiple keywords, use quotation marks to indicate whether
        the title or abstract should contain the exact match. For example,
        <i>
          <b>"epithelial kidney"</b>
        </i>{' '}
        will search for the matching words on titles or abstracts.
      </ListItem>
      <ListItem>
        However, not using the quotation marks will only consider the first word
        as a matching keyword to the title or abstract, and the following words
        only to match the abstract. For example:{' '}
        <i>
          <b>kidney renal fibrosis</b>
        </i>{' '}
        will look for all words in the abstract and only the word <i>kidney</i>{' '}
        in the title field.
      </ListItem>
      <ListItem>
        You can also combine keywords with and without quotations. For instance,{' '}
        <i>
          <b>"epithelial kidney" renal</b>
        </i>{' '}
        looks for the words in quotations in the titles and abstracts, and also
        the word <i>renal</i> in the abstracts.
      </ListItem>
    </UnorderedList>
    <Text fontWeight={'bold'} mt={2}>
      2. Boolean Operators:
    </Text>
    <UnorderedList>
      <ListItem>
        To use boolean queries, you need to specify the affected fields
        following the syntax <i>field-name</i>
        <b>:</b>
        <i>query</i> AND|OR ... <i>field-name</i>
        <b>:</b>
        <i>query</i>. In other words, you specify the field name, followed by a
        colon, followed by a query term, and you concatenate that operator with
        and AND or OR plus any other operators.
      </ListItem>
      <ListItem>
        We currently support the fields <b>title</b> and <b>abstract</b>
      </ListItem>
      <ListItem>
        The AND and OR operators need to be in caps to differentiate them from
        query terms.
      </ListItem>
      <ListItem>
        For example, the query{' '}
        <i>
          <b>title:"epithelial kidney" AND abstract: renal</b>
        </i>{' '}
        looks for an specific words in the title and a word in the abstract.
      </ListItem>
    </UnorderedList>
  </Box>
)

interface HelpQueriesProps {
  tutorialUrl: string
}

export function HelpQueries({tutorialUrl}: HelpQueriesProps) {
  const {isOpen, onOpen, onClose} = useDisclosure()
  return (
    <>
      <Button size="xs" onClick={onOpen}>
        ?
      </Button>

      <Modal isOpen={isOpen} onClose={onClose} size="4xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Supported queries</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Explanation url={tutorialUrl} />
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  )
}

export default HelpQueries
