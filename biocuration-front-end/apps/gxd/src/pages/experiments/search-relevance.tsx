import {useMemo, useReducer, useState} from 'react'
import {
  Box,
  Flex,
  Spacer,
  Button,
  useToast,
  Text,
  Stack,
} from '@chakra-ui/react'
import {
  RowModalityLegend,
  searchReducer,
  initSearchState,
  HelpQueries,
  Document,
  Page,
} from '@biocuration-front-end/common-ui'
import {SearchBar} from './search-bar'
import {HorizontalFigureResults} from './result-cards'
import {ReactComponent as Taxonomy} from '../../assets/taxonomy.svg'
import {colorsMapper, namesMapper, ddlSearchOptions} from '../../utils/mapper'
import {search, getPageFigureDetails} from '../../api'
import {About} from '../search/about'
import {useLocation} from 'react-router-dom'
import {v4 as uuidv4} from 'uuid'

/* eslint-disable-next-line */
export interface SearchProps {
  condition: string
  status: string
  setStatus: React.Dispatch<React.SetStateAction<string>>
  logout: () => void
  total: number
}

const useQuery = () => {
  const {search} = useLocation()
  return useMemo(() => new URLSearchParams(search), [search])
}

const COLLECTION = process.env.NX_COLLECTION
const IMAGES_BASE_URL = process.env.NX_FIGURES_ENDPOINT
const PDFS_BASE_URL = process.env.NX_PDFS_ENDPOINT

interface SearchRelevancePageProps {
  authToken: string
  logout: () => void
}

const CONDITIONS = ['text', 'image']

export const SearchRelevancePage = ({
  authToken,
  logout,
}: SearchRelevancePageProps) => {
  const [condition, setCondition] = useState<string>(
    CONDITIONS[Math.floor(Math.random() * CONDITIONS.length)],
  )
  const [status, setStatus] = useState<string>('introduction')
  const queryParams = useQuery()
  const total =
    queryParams.get('n') !== null ? parseInt(queryParams.get('n') || '') : 5
  const uid = useMemo<string>(() => uuidv4(), [])

  return (
    <Box w="100wv" h="100hv">
      {status === 'introduction' ? (
        <Introduction total={total} setStatus={setStatus} />
      ) : null}
      {status === 'intermediate' ? (
        <Intermediate
          setStatus={setStatus}
          condition={condition}
          setCondition={setCondition}
        />
      ) : null}
      {status === 'end' ? <End /> : null}
      {status === 'condition1' || status === 'condition2' ? (
        <SearchRelevanceExperiment
          condition={condition}
          status={status}
          setStatus={setStatus}
          logout={logout}
          total={total}
        />
      ) : null}
    </Box>
  )
}

interface IntroductionProps {
  setStatus: React.Dispatch<React.SetStateAction<string>>
  total: number
}
const Introduction = ({total, setStatus}: IntroductionProps) => {
  return (
    <>
      <Flex
        w="full"
        h="90%"
        backgroundColor={'gray.300'}
        alignItems={'center'}
        justifyContent={'left'}
        p={2}
      >
        <Text fontWeight={'bold'} fontSize={'3xl'} ml={4}>
          Task 2: Find relevant documents
        </Text>
      </Flex>
      <Flex
        alignItems={'center'}
        justifyContent={'center'}
        flexDirection={'column'}
        p={10}
      >
        <Stack>
          <Text fontSize={'2xl'} fontWeight={'bold'}>
            Instructions
          </Text>
          <Text fontSize={'xl'}>
            This task consists of two steps, one step per presentation
            condition: text-only information or text + image information. On
            each steps you need to find {total} relevant documents using the
            available search features:
          </Text>
          <Text fontSize={'xl'} as="li">
            Click on the checkbox to the left of a search result to it as
            relevant.
          </Text>
          <Text fontSize={'xl'} as="li">
            Once you mark {total} results as relevants, the{' '}
            <Button colorScheme="blue">Finish Task</Button> will be enabled.
            Click on the button to go to the next step in the experiment.
          </Text>
          <Text pt={4} pb={4} fontSize={'xl'}>
            Press <Button>Start</Button> to begin with this experiment.
          </Text>
          <Button onClick={() => setStatus('condition1')}>Start</Button>
        </Stack>
      </Flex>
    </>
  )
}

interface IntermediateProps {
  condition: string
  setCondition: React.Dispatch<React.SetStateAction<string>>
  setStatus: React.Dispatch<React.SetStateAction<string>>
}

const Intermediate = ({
  condition,
  setCondition,
  setStatus,
}: IntermediateProps) => {
  const handleStart = () => {
    const newCondition = condition === 'text' ? 'image' : 'text'
    setCondition(newCondition)
    setStatus('condition2')
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
          That is the end of the first step. Now, you will perform the same task
          using the second condition. Press <Button>Start</Button> when you are
          ready.
        </Text>
        <Button onClick={handleStart}>Start</Button>
      </Stack>
    </Flex>
  )
}

const End = () => (
  <Flex
    alignItems={'center'}
    justifyContent={'center'}
    w="full"
    h="90vh"
    flexDir={'column'}
    fontSize={'2xl'}
  >
    <Text>Awesome, you have successfully finished the first task.</Text>
    <Text>Please go to the activity document and close this page.</Text>
  </Flex>
)

const SearchRelevanceExperiment = ({
  condition,
  total,
  status,
  setStatus,
  logout,
}: SearchProps) => {
  const [{documents, isLoading, filterModalities}, dispatch] = useReducer(
    searchReducer,
    initSearchState,
  )
  const [relevantIds, setRelevantIds] = useState<number[]>([])
  const toast = useToast()
  const baseModalities = Object.keys(colorsMapper).filter(
    el => !el.includes('.'),
  )

  const getPageUrl = (document: Document, page: Page) => {
    const paddedPage = page.page.toString().padStart(6, '0')
    const pageUrl = `${PDFS_BASE_URL}/${document.otherid}/${document.otherid}-${paddedPage}.png`
    return pageUrl
  }

  const handleSearch = async (
    keywords: string | null,
    startDate: string | null,
    endDate: string | null,
    modalities: string[],
  ) => {
    if (keywords == null) {
      toast({
        position: 'top',
        description: 'Please enter at least one keyword in the search bar',
        duration: 3000,
        isClosable: true,
        status: 'warning',
      })
      return
    }

    const maxDocs = 2000
    dispatch({type: 'START_SEARCH', payload: modalities})
    const sleep = (ms: number) => new Promise(r => setTimeout(r, ms))
    const results = await search(
      keywords,
      COLLECTION,
      startDate,
      endDate,
      maxDocs,
      modalities,
    )
    await sleep(10)
    dispatch({type: 'END_SEARCH', payload: results})
  }

  const handleFinishTask = () => {
    if (status === 'condition1') {
      setStatus('intermediate')
    } else {
      setStatus('end')
    }
  }

  return (
    <Box className="container" minH="100vh" w="full">
      <Flex
        justifyContent={'left'}
        alignItems={'center'}
        w="full"
        h="50px"
        backgroundColor={'yellow.300'}
        p="2"
      >
        <Text>Task 2: Find {total} relevant documents </Text>
        <Spacer />
        <Text mr={2}>
          {relevantIds.length} / {total}
        </Text>
        <Button
          disabled={relevantIds.length < total}
          colorScheme="green"
          onClick={handleFinishTask}
        >
          Finish Task
        </Button>
      </Flex>
      <Box w="full" h="100px" p={4} pt={2} pb={0} zIndex={400}>
        <Flex w="full" alignItems={'center'}>
          <Text fontWeight={'bold'}>GXD Search</Text>
          {condition === 'image' ? (
            <RowModalityLegend
              modalities={baseModalities}
              colorsMapper={colorsMapper}
              namesMapper={namesMapper}
              taxonomyImage={<Taxonomy />}
            />
          ) : null}

          <Spacer />
          <HelpQueries
            tutorialUrl={
              'https://docs.google.com/document/d/1c0SFMi7o14HuoLZ0Q0-Jll5nfjDoy1gZbaQkG6KnLG8/edit?usp=sharing'
            }
          />
          <About />
        </Flex>
        <SearchBar
          defaultStartYear={2012}
          defaultEndYear={2016}
          options={ddlSearchOptions}
          colorsMapper={colorsMapper}
          onSearch={handleSearch}
          keywordPlaceholderValue="e.g. disease"
          sampleQueries={[
            {query: 'disease', label: 'disease', modalities: []},
            {
              query: 'title:kinase AND abstract:transcription',
              label: 'title:kinase AND abstract:transcription',
              modalities: [],
            },
          ]}
          isLoading={isLoading}
          condition={condition}
        />

        <Box w="full" mt={2}>
          <HorizontalFigureResults
            documents={documents}
            isLoading={isLoading}
            colorsMapper={colorsMapper}
            namesMapper={namesMapper}
            preferredModalities={filterModalities}
            figuresBaseUrl={IMAGES_BASE_URL}
            getPageFigureData={getPageFigureDetails}
            getPageUrl={getPageUrl}
            condition={condition}
            relevantIds={relevantIds}
            setRelevantIds={setRelevantIds}
          />
        </Box>
      </Box>
    </Box>
  )
}
