import {useEffect, useMemo, useState} from 'react'
import {useLocation} from 'react-router-dom'
import {Box, Flex, Text, Button, Stack, Spacer} from '@chakra-ui/react'
import {
  Document,
  HorizontalResultCard,
  LuceneDocument,
  Page,
} from '@biocuration-front-end/common-ui'
import {colorsMapper, namesMapper} from '../../utils/mapper'
import {search, getPageFigureDetails, logExperimenterResult} from '../../api'
import SimpleResultCard from 'libs/common-ui/src/lib/simple-result-card/simple-result-card'
import {v4 as uuidv4} from 'uuid'

const COLLECTION = process.env.NX_COLLECTION
const IMAGES_BASE_URL = process.env.NX_FIGURES_ENDPOINT
const PDFS_BASE_URL = process.env.NX_PDFS_ENDPOINT

const useQuery = () => {
  const {search} = useLocation()
  return useMemo(() => new URLSearchParams(search), [search])
}

const getPageUrl = (document: Document, page: Page) => {
  const paddedPage = page.page.toString().padStart(6, '0')
  const pageUrl = `${PDFS_BASE_URL}/${document.otherid}/${document.otherid}-${paddedPage}.png`
  return pageUrl
}

const conditions = ['text', 'image']

interface PageProps {
  token: string
}

const IndividualRelevancePage = ({token}: PageProps) => {
  const [condition, setCondition] = useState<string>(
    conditions[Math.floor(Math.random() * conditions.length)],
  )
  const [status, setStatus] = useState<string>('introduction')
  const [completedConditions, setCompletedConditions] = useState<string[]>([])
  let query = useQuery()
  const [documents, setDocuments] = useState<LuceneDocument[]>([])
  const [docIndex, setDocIndex] = useState<number>(0)

  const NUM_RESULTS_PER_CONDITION = parseInt(query.get('e') || '10')
  const uid = useMemo<string>(() => {
    return uuidv4()
  }, [])

  useEffect(() => {
    async function loadDocuments() {
      const results = await search(
        'gene',
        COLLECTION,
        null,
        null,
        NUM_RESULTS_PER_CONDITION * 10,
        [],
      )
      const shuffled = shuffle(results)
      console.log(shuffled.map(el => el.id))
      setDocuments(shuffled)
    }
    loadDocuments()
  }, [])

  return (
    <Box w="100wv" h="100hv">
      <Flex
        w="full"
        h="90%"
        backgroundColor={'gray.300'}
        alignItems={'center'}
        justifyContent={'left'}
        p={2}
      >
        <Text fontWeight={'bold'} fontSize={'3xl'}>
          Experiment: Is this a relevant search result?
        </Text>
        <Spacer />
        {status === 'experiment' ? (
          <Counter index={docIndex} total={NUM_RESULTS_PER_CONDITION} />
        ) : null}
      </Flex>
      {status === 'introduction' ? (
        <Introduction total={NUM_RESULTS_PER_CONDITION} setStatus={setStatus} />
      ) : null}
      {status === 'experiment' ? (
        <DecisionContainer
          document={documents[docIndex]}
          condition={condition}
          setStatus={setStatus}
          index={docIndex}
          setIndex={setDocIndex}
          completedConditions={completedConditions}
          total={NUM_RESULTS_PER_CONDITION}
          token={token}
          uid={uid}
        />
      ) : null}
      {status === 'intermediate' ? (
        <Intermediate
          condition={condition}
          setCondition={setCondition}
          setStatus={setStatus}
          setCompletedConditions={setCompletedConditions}
          total={NUM_RESULTS_PER_CONDITION}
        />
      ) : null}
      {status === 'end' ? <End /> : null}
    </Box>
  )
}

interface IntroductionProps {
  setStatus: React.Dispatch<React.SetStateAction<string>>
  total: number
}

const Introduction = ({total, setStatus}: IntroductionProps) => {
  const handleStart = () => {
    setStatus('experiment')
  }

  return (
    <Flex
      alignItems={'center'}
      justifyContent={'center'}
      flexDirection={'column'}
      p={10}
    >
      <Stack>
        <Text fontSize={'2xl'} fontWeight={'bold'}>
          About This Project
        </Text>
        <Text fontSize={'xl'}>
          This NIH National Library of Medicine (NLM)-sponsored project is being
          developed by a group of researchers at the University of Delaware and
          University of Illinois Chicago, led by MPIs Prof. Shatkay and Prof.
          Marai, in collaboration with several biocuration groups at U Delaware,
          Caltech, and Jackson Labs. In this experiment, we aim to evaluate the
          effect of presenting images and image-based information when
          displaying results of a document search, in addition to common text
          information. Text information includes title, authors, and relevant
          sentences from the abstract that match a query keyword. Image
          information include the document figures while image-based information
          includes the type of image modalities found in the figures. In
          addition, this condition includes the figure captions.
        </Text>
        <Text></Text>

        <Text fontSize={'2xl'} fontWeight={'bold'}>
          About This Experiment
        </Text>
        <Text fontSize={'xl'}>
          In this experiment, the interface will present {total} query results,
          on at the time, per condition: text-only information and text + image
          information. You are asked to indicate whether the query result is
          relevant or not to the research interests of the Gene Expression
          Database. Our dataset is a subset of 2000 documents from the GXD
          collection filtered by the query keyword 'gene'.
        </Text>
        <Text fontSize={'2xl'} fontWeight={'bold'}>
          Instructions
        </Text>
        <Text fontSize={'xl'} as="li">
          Click on the red button to indicate that the result is not relevant
        </Text>
        <Text fontSize={'xl'} as="li">
          Clicking on the green button indicates that the result is relevant.
        </Text>
        <Text fontSize={'xl'}>
          Clicking any button advances to the next image.
        </Text>

        <Text pt={4} pb={4} fontSize={'xl'}>
          Press 'Start' to begin with this experiment. Thank you for your
          cooperation.
        </Text>
        <Button onClick={handleStart}>Start</Button>
      </Stack>
    </Flex>
  )
}

interface IntermediateProps {
  condition: string
  setCondition: React.Dispatch<React.SetStateAction<string>>
  setStatus: React.Dispatch<React.SetStateAction<string>>
  setCompletedConditions: React.Dispatch<React.SetStateAction<string[]>>
  total: number
}

const Intermediate = ({
  condition,
  setCondition,
  setStatus,
  setCompletedConditions,
  total,
}: IntermediateProps) => {
  const handleStart = () => {
    const newCondition = condition === 'text' ? 'image' : 'text'
    setCondition(newCondition)
    setStatus('experiment')
    setCompletedConditions([condition])
  }

  return (
    <Flex
      alignItems={'center'}
      justifyContent={'center'}
      flexDirection={'column'}
      p={10}
    >
      <Stack fontSize={'2xl'}>
        <Text pt={4} pb={4}>
          After you press 'Start', you will see {total} query results showing
          the second condition.
        </Text>
        <Button onClick={handleStart}>Start</Button>
      </Stack>
    </Flex>
  )
}

const End = () => (
  <Flex alignItems={'center'} justifyContent={'center'} w="full" h="90vh">
    Thank you
  </Flex>
)

interface DecisionProps {
  document: LuceneDocument
  condition: string
  setStatus: React.Dispatch<React.SetStateAction<string>>
  index: number
  setIndex: React.Dispatch<React.SetStateAction<number>>
  completedConditions: string[]
  total: number
  token: string
  uid: string
}

const DecisionContainer = ({
  document,
  condition,
  index,
  setStatus,
  setIndex,
  completedConditions,
  total,
  token,
  uid,
}: DecisionProps) => {
  const startTime = useMemo(() => {
    return new Date()
  }, [document])

  const handleOnClick = async (relevant: boolean) => {
    const clickTime = new Date()

    const response = await logExperimenterResult(
      token,
      uid,
      condition,
      document.id.toString(),
      relevant,
      clickTime.getTime() - startTime.getTime(),
    )
    console.log(response)

    const newIndex = index + 1
    if (newIndex % total === 0) {
      if (completedConditions.length === 1) {
        setStatus('end')
      } else {
        setStatus('intermediate')
        setIndex(newIndex)
      }
    } else {
      setIndex(newIndex)
    }
  }

  return (
    <Flex
      w="full"
      h="90vh"
      justifyContent={'center'}
      alignItems={'center'}
      flexDirection={'column'}
    >
      <Box p={4}>
        {condition === 'image' ? (
          <ImageResult document={document} />
        ) : condition === 'text' ? (
          <TextResult document={document} />
        ) : null}
      </Box>

      <Flex w="full" p={2}>
        <Button
          w="50%"
          mr={1}
          colorScheme="red"
          onClick={() => handleOnClick(false)}
        >
          Not Relevant
        </Button>
        <Spacer />
        <Button
          w="50%"
          ml={1}
          colorScheme="green"
          onClick={() => handleOnClick(true)}
        >
          Relevant
        </Button>
      </Flex>
    </Flex>
  )
}

interface ResultProps {
  document: LuceneDocument
}

const ImageResult = ({document}: ResultProps) => {
  return (
    <HorizontalResultCard
      key={document.id}
      document={document}
      colorsMapper={colorsMapper}
      namesMapper={namesMapper}
      figuresBaseUrl={IMAGES_BASE_URL}
      preferredModalities={[]}
      getPageFigureData={getPageFigureDetails}
      getPageUrl={getPageUrl}
    />
  )
}

const TextResult = ({document}: ResultProps) => {
  return (
    <Box maxW="700px">
      <SimpleResultCard
        key={document.id}
        document={document}
        onClick={null}
        colorMapper={colorsMapper}
        namesMapper={namesMapper}
        selected={false}
        showModalities={false}
      />
    </Box>
  )
}

interface CounterProps {
  index: number
  total: number
}
const Counter = ({index, total}: CounterProps) => (
  <Box>
    {(index % total) + 1}/{total}
  </Box>
)

function shuffle(array: LuceneDocument[]) {
  //https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle
  let currentIndex = array.length,
    randomIndex

  // While there remain elements to shuffle.
  while (currentIndex != 0) {
    // Pick a remaining element.
    randomIndex = Math.floor(Math.random() * currentIndex)
    currentIndex--

    // And swap it with the current element.
    ;[array[currentIndex], array[randomIndex]] = [
      array[randomIndex],
      array[currentIndex],
    ]
  }

  return array
}

export {IndividualRelevancePage}
