import {Box, chakra, Spacer} from '@chakra-ui/react'
import {Dispatch, SetStateAction} from 'react'
import {
  ActionButton,
  HeaderTabs,
  HeaderTitle,
  PanelHeader,
} from '../panel-header/panel-header'

const options = [
  {label: 'Mispredicted', value: 'incorrect'},
  {label: 'Selected', value: 'selected'},
  {
    label: 'Confident',
    value: 'active-learning1',
  },
  {
    label: 'Uncertain',
    value: 'active-learning2',
  },
]

interface GalleryHeaderProps {
  numberImages: number
  currPage: number
  setCurrPage: Dispatch<SetStateAction<number>>
  setTabIndex: Dispatch<SetStateAction<number>>
  onSelectAll: () => void
  onDeselectAll: () => void
  numberPages: number
}

export const GalleryHeader = ({
  numberImages,
  currPage,
  setCurrPage,
  setTabIndex,
  onSelectAll,
  onDeselectAll,
  numberPages,
}: GalleryHeaderProps) => {
  return (
    <PanelHeader>
      <HeaderTitle>Gallery</HeaderTitle>
      <ActionButton disabled={false} isLoading={false} onClick={onSelectAll}>
        Select All
      </ActionButton>
      <ActionButton disabled={false} isLoading={false} onClick={onDeselectAll}>
        Deselect All
      </ActionButton>
      <HeaderTabs setTabIndex={setTabIndex} options={options} />
      <Spacer />
      {numberImages > 0 ? (
        <Box>
          <chakra.span color="white" mr={2}>
            {numberImages} Images
          </chakra.span>
          <ActionButton
            size="sm"
            mr="2"
            disabled={currPage === 0}
            onClick={() => setCurrPage(currPage - 1)}
          >
            Prev Page
          </ActionButton>
          <chakra.span color={'white'} mr={2}>{`p.${
            currPage + 1
          }/${numberPages}`}</chakra.span>
          <ActionButton
            size="sm"
            mr="1"
            disabled={currPage === numberPages - 1}
            onClick={() => setCurrPage(currPage + 1)}
          >
            Next Page
          </ActionButton>
        </Box>
      ) : null}
    </PanelHeader>
  )
}
