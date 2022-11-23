import TaxonomyImage from '../../utils/taxonomy.svg'
import {Flex} from '@chakra-ui/react'

export const Taxonomy = () => {
  return (
    <Flex w="full" h="full" alignItems={'center'} justifyContent="center">
      <img src={TaxonomyImage} alt="taxonomy for search interface" />
    </Flex>
  )
}
