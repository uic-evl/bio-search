import { useState } from "react";
import {
  Box,
  FormControl,
  FormLabel,
  Input,
  Flex,
  Select as ChakraSelect,
  Button,
} from "@chakra-ui/react";

const options = [
  { value: "GXD", label: "GXD" },
  { value: "CORD-19", label: "CORD-19" },
];

export const SearchBar = () => {
  const [query, setQuery] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  return (
    <Box w="full" h="150px" p={4}>
      <Flex w="full">
        <Box w="50%">
          <FormControl id="search">
            <FormLabel mb={0} fontSize={10}>
              SEARCH
            </FormLabel>
            <Input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              size={"sm"}
            />
          </FormControl>

          <Flex mt={1}>
            <FormControl id="domain" w="150px">
              <FormLabel mb={0} fontSize={10}>
                COLLECTION
              </FormLabel>
              <ChakraSelect size={"sm"}>
                {options.map((el) => (
                  <option key={el.value} value={el.value}>
                    {el.label}
                  </option>
                ))}
              </ChakraSelect>
            </FormControl>

            <FormControl id="start-date" ml={2} w="250px">
              <FormLabel mb={0} fontSize={10}>
                FROM
              </FormLabel>
              <Input
                type="text"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                size={"sm"}
              />
            </FormControl>

            <FormControl id="end-date" ml={2} w="250px">
              <FormLabel mb={0} fontSize={10}>
                TO
              </FormLabel>
              <Input
                type="text"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                size={"sm"}
              />
            </FormControl>

            <Button w="200px" size="sm" ml={2} mt={4}>
              Search
            </Button>
          </Flex>
        </Box>
        <Box w="50%"></Box>
      </Flex>
    </Box>
  );
};
