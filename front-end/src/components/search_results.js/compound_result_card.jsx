import {Box, Flex} from '@chakra-ui/react'
import {SearchResultCard} from './simple_result_card'
import {getDetails} from '../../api/index'
import {useState, useEffect} from 'react'
import {EnhancedSurrogate} from './figure_details'

const CompoundResultCard = ({result, onClickOpen, selected, pdfEndpoint}) => {
  const [figureDetails, setFigureDetails] = useState(null)
  const simpleCardProps = {result, onClickOpen, selected, pdfEndpoint}

  useEffect(() => {
    const load = async () => {
      const details = await getDetails(result.id)
      setFigureDetails(details)
    }
    load()
  }, [result.id])

  return (
    <Flex direction={'row'} h="250px">
      <Box w="40%" h="100%">
        <SearchResultCard {...simpleCardProps} />
      </Box>
      <Box w="60%" h="100%" pl={2}>
        {figureDetails && <EnhancedSurrogate document={figureDetails} />}
      </Box>
    </Flex>
  )
}

export {CompoundResultCard}
