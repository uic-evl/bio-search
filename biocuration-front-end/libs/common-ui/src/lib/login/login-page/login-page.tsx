import {useState} from 'react'
import {
  Input,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Text,
  Box,
} from '@chakra-ui/react'

/* eslint-disable-next-line */
export interface LoginPageProps {
  title: string
  login: (arg1: string, arg2: string) => void
  message: string
}

export function LoginPage({title, message, login}: LoginPageProps) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  const handleOnClick = async () => {
    login(username, password)
  }

  return (
    <Flex
      direction={'column'}
      align="center"
      justifyContent="center"
      minH="100vh"
    >
      <Box>
        <Text fontSize={'4xl'} fontWeight={'bold'}>
          {title}
        </Text>
      </Box>
      <form>
        <FormControl>
          <FormLabel>Username</FormLabel>
          <Input value={username} onChange={e => setUsername(e.target.value)} />
        </FormControl>
        <FormControl>
          <FormLabel>Password</FormLabel>
          <Input
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
          />
        </FormControl>
        <Button
          isDisabled={username.trim() === '' || password.trim() === ''}
          mt="2"
          onClick={handleOnClick}
          w="full"
        >
          Log in
        </Button>
        <div>{message}</div>
      </form>
    </Flex>
  )
}

export default LoginPage
