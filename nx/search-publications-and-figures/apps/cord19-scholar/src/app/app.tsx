import {ChakraProvider} from '@chakra-ui/react'
import theme from '../theme'
import Search from '../pages/search/search'

export function App() {
  return (
    <ChakraProvider theme={theme}>
      <Search />
    </ChakraProvider>
  )
}

export default App
