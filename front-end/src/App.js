import { SearchBar } from "./components/search_bar/search_bar";
import { ResultsContainer } from "./components/search_results.js/results_container";
import { Box, Flex } from "@chakra-ui/react";

function App() {
  return (
    <Box className="container" minH="100vh" w="full">
      <SearchBar />
      <Flex pl={4}>
        <Box w="50%">
          <ResultsContainer />
        </Box>
      </Flex>
    </Box>
  );
}

export default App;
