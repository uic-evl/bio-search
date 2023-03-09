import {
  PropsWithChildren,
  SyntheticEvent,
  ChangeEventHandler,
  Dispatch,
  SetStateAction,
} from 'react'
import {Box, Flex, Text, Spacer, Select, Button} from '@chakra-ui/react'

/** Components for the headers of panels */

export const PanelHeader = (props: PropsWithChildren) => {
  return (
    <Flex
      {...props}
      w="100%"
      direction="row"
      m={0}
      p={0}
      bg="blackAlpha.800"
      alignItems="center"
    >
      {props.children}
    </Flex>
  )
}

export const HeaderTitle = (props: PropsWithChildren) => (
  <Box ml={2} mr={2}>
    <Text
      fontSize="sm"
      color="white"
      casing="uppercase"
      p={0.5}
      letterSpacing="1px"
      fontWeight="bold"
    >
      {props.children}
    </Text>
  </Box>
)

interface MenuSelectProps {
  placeholder?: string
  value: string
  onChangeFn: ChangeEventHandler<HTMLSelectElement>
}

export const MenuSelect = (props: PropsWithChildren<MenuSelectProps>) => (
  <Select
    value={props.value}
    placeholder={props.placeholder}
    size="xs"
    borderColor="blackAlpha.800"
    color="white"
    onChange={props.onChangeFn}
  >
    {props.children}
  </Select>
)

interface HeaderSelectProps {
  placeholder?: string
  value: string
  options: Array<string>
  onChangeFn: Dispatch<SetStateAction<string>>
}

const optionStyle = {background: '#2A342D', color: 'white'}
interface OptionProps {
  label: string
  value: string
}

export const Option = ({label, value}: OptionProps) => (
  <option value={value} style={optionStyle}>
    {label}
  </option>
)

export const HeaderSelect = (props: HeaderSelectProps) => (
  <Box>
    <MenuSelect
      value={props.value}
      placeholder={props.placeholder}
      onChangeFn={(e: SyntheticEvent) => {
        const value = (e.target as HTMLInputElement).value
        props.onChangeFn(value)
      }}
    >
      {props.options.map(t => (
        <Option key={t} value={t} label={t} />
      ))}
    </MenuSelect>
  </Box>
)

interface BoxHeaderAndOptionsProps {
  title: string
  options: Array<string>
  value: string
  onChangeFn: Dispatch<SetStateAction<string>>
}

export const BoxHeaderAndOptions = ({
  title,
  options,
  value,
  onChangeFn,
}: BoxHeaderAndOptionsProps) => (
  <PanelHeader>
    <HeaderTitle>{title}</HeaderTitle>
    <Spacer />
    <HeaderSelect options={options} value={value} onChangeFn={onChangeFn} />
  </PanelHeader>
)

interface ActionButtonProps {
  disabled: boolean
  isLoading: boolean
  onClick: () => void
}

export const ActionButton = (props: PropsWithChildren<ActionButtonProps>) => (
  <Button
    {...props}
    bg="none"
    size="xs"
    color="white"
    colorScheme="whiteAlpha"
    variant="outline"
    borderRadius="0px"
  >
    {props.children}
  </Button>
)
