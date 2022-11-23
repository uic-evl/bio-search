import {createRoot} from 'react-dom/client'
import App from './App'
// import reportWebVitals from "./reportWebVitals";

import {ChakraProvider} from '@chakra-ui/react'
import theme from './theme'

const container = document.getElementById('root')
const root = createRoot(container)

function AppWithChakraProvider() {
  return (
    <ChakraProvider theme={theme}>
      <App />
    </ChakraProvider>
  )
}

root.render(<AppWithChakraProvider />)

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
// reportWebVitals();