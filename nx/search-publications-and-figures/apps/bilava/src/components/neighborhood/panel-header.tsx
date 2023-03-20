import {useState} from 'react'
import {Box, Spacer} from '@chakra-ui/react'
import {Dispatch, SetStateAction, SyntheticEvent} from 'react'
import {
  ActionButton,
  HeaderKeySelect,
  HeaderSelect,
  HeaderTitle,
  PanelHeader,
} from '../panel-header/panel-header'
import {GRID_LAYOUT, SPATIAL_SPIRAL_MAP, SPIRAL_MAP} from './constants'

const viewOptions = [
  {value: GRID_LAYOUT, label: 'Grid Layout'},
  {value: SPIRAL_MAP, label: 'Spiral Layout'},
  {value: SPATIAL_SPIRAL_MAP, label: 'Spatial Spiral Layout'},
]

const saliencyOptions = [
  {value: '', label: 'No Saliency'},
  {value: 'gradcam', label: 'GradCAM'},
]

const sizeOptions = [
  {value: 'small', label: 'Small'},
  {value: 'medium', label: 'Medium'},
  {value: 'large', label: 'Large'},
  {value: 'xlarge', label: 'X-Large'},
]

interface Strategy {
  nei: number
  stg: string
  maxRings: number
}

const strategiesPerLayout: Record<string, Record<string, Strategy>> = {
  [SPIRAL_MAP as string]: {
    small: {nei: 32, stg: 'small2rings', maxRings: 2},
    medium: {nei: 60, stg: 'medium3rings', maxRings: 3},
    large: {nei: 96, stg: 'large4rings', maxRings: 4},
    xlarge: {nei: 180, stg: 'xlarge4rings1smalls', maxRings: 5},
  },
  [SPATIAL_SPIRAL_MAP as string]: {
    small: {nei: 32, stg: 'small2rings', maxRings: 2},
    medium: {nei: 60, stg: 'medium3rings', maxRings: 3},
    large: {nei: 96, stg: 'large4rings', maxRings: 4},
    xlarge: {nei: 180, stg: 'xlarge4rings1smalls', maxRings: 5},
  },
  [GRID_LAYOUT as string]: {
    small: {nei: 35, stg: 'small2rings', maxRings: 2},
    medium: {nei: 63, stg: 'medium3rings', maxRings: 3},
    large: {nei: 99, stg: 'large4rings', maxRings: 4},
    xlarge: {nei: 168, stg: 'xlarge4rings1smalls', maxRings: 5},
  },
}

const objectFitOptions = ['fit', 'cover']

interface NeighborhoodPanelProps {
  layout: string
  setLayout: Dispatch<SetStateAction<string>>
  strategy: string
  setStrategy: Dispatch<SetStateAction<string>>
  saliency: string
  setSaliency: Dispatch<SetStateAction<string>>
  setNumberNeighbors: Dispatch<SetStateAction<number>>
  setMaxRings: Dispatch<SetStateAction<number>>
  objectFit: string
  setObjectFit: Dispatch<SetStateAction<string>>
  onSelectAll: () => void
  onDeselectAll: () => void
}

export const NeighborhoodPanelHeader = (props: NeighborhoodPanelProps) => {
  const [size, setSize] = useState<string>('small')

  const handleOnChangeLayout = (e: SyntheticEvent) => {
    const value = (e.target as HTMLInputElement).value
    if (
      (value === SPIRAL_MAP && props.layout === SPATIAL_SPIRAL_MAP) ||
      (value === SPATIAL_SPIRAL_MAP && props.layout === SPIRAL_MAP)
    ) {
      props.setLayout(value)
    } else {
      props.setLayout(value)
      props.setNumberNeighbors(strategiesPerLayout[value][size].nei)
      props.setStrategy(strategiesPerLayout[value][size].stg)
      props.setMaxRings(strategiesPerLayout[value][size].maxRings)
    }
  }

  const handleOnChangesize = (e: SyntheticEvent) => {
    const value = (e.target as HTMLInputElement).value
    if (value) {
      props.setNumberNeighbors(strategiesPerLayout[props.layout][value].nei)
      props.setStrategy(strategiesPerLayout[props.layout][value].stg)
      props.setMaxRings(strategiesPerLayout[props.layout][value].maxRings)
    }
    setSize(value)
  }

  const handleOnChangeSaliency = (e: SyntheticEvent) => {
    const value = (e.target as HTMLInputElement).value
    props.setSaliency(value)
  }

  return (
    <Box>
      <PanelHeader>
        <HeaderTitle>Neighborhood</HeaderTitle>
        <ActionButton
          onClick={props.onSelectAll}
          disabled={false}
          isLoading={false}
        >
          Select All
        </ActionButton>
        <ActionButton
          onClick={props.onDeselectAll}
          disabled={false}
          isLoading={false}
        >
          Deselect All
        </ActionButton>
        <Spacer />
        <HeaderKeySelect
          value={props.layout}
          onChangeFn={handleOnChangeLayout}
          options={viewOptions}
        />
        <HeaderKeySelect
          value={size}
          options={sizeOptions}
          onChangeFn={handleOnChangesize}
        />
        <HeaderKeySelect
          value={props.saliency}
          onChangeFn={handleOnChangeSaliency}
          options={saliencyOptions}
        />
        <HeaderSelect
          value={props.objectFit}
          onChangeFn={props.setObjectFit}
          options={objectFitOptions}
        />
      </PanelHeader>
    </Box>
  )
}
