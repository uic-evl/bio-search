import type {ComponentStory, ComponentMeta} from '@storybook/react'
import {Annotations} from './annotations'
import {Box} from '@chakra-ui/react'

const Story: ComponentMeta<typeof Annotations> = {
  component: Annotations,
  title: 'Annotations',
}
export default Story

const Template: ComponentStory<typeof Annotations> = args => (
  <Box w={500} h={500} ml={50}>
    <Annotations {...args} />
  </Box>
)

export const Primary = Template.bind({})
Primary.args = {
  padding: 0,
  imageSrc:
    'https://upload.wikimedia.org/wikipedia/commons/1/18/Dog_Breeds.jpg',
}
