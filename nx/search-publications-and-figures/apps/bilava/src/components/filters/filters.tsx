import {Dispatch, SetStateAction, useEffect, useState} from 'react'
import {
  Box,
  chakra,
  Flex,
  Text,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  RangeSliderTrack,
  RangeSlider,
  RangeSliderThumb,
  RangeSliderFilledTrack,
} from '@chakra-ui/react'
import {SimpleBoxHeader, Subtitle} from '../panel-header/panel-header'
import {BarChartFilter} from './bar-chart-filter'
import {Dataset, Filter, ScatterDot} from '../../types'
import StackedBarChart from '../../charts/stacked-bar-chart/stacked-bar-chart'

const BAR_SIZE = 18 // pixels height for horizontal bars

interface SliderControllerProps {
  text: string
  textWidth: string
  min: number
  max: number
  step: number
  value: number
  setValue: Dispatch<SetStateAction<number>>
  setValueEnd?: (arg: number) => void
}

const SliderController = ({
  text,
  textWidth,
  min,
  max,
  step,
  value,
  setValue,
  setValueEnd,
}: SliderControllerProps) => (
  <Flex direction="row">
    <Text w={textWidth}>{text}</Text>
    <Slider
      colorScheme="pink"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={setValue}
      onChangeEnd={val => {
        if (setValueEnd) setValueEnd(val)
      }}
    >
      <SliderTrack>
        <SliderFilledTrack />
      </SliderTrack>
      <SliderThumb backgroundColor={'black'} />
    </Slider>
  </Flex>
)

/* eslint-disable-next-line */
export interface FiltersProps {
  dataset: Dataset
  filters: Filter
  setFilters: Dispatch<SetStateAction<Filter>>
}

export function Filters(props: FiltersProps) {
  const [hits, setHits] = useState<number>(0.5)
  const [selection, setSelection] = useState<[number, number]>([0, 100])

  console.log('min pred', props.dataset.minPrediction)

  useEffect(() => {
    setSelection([props.dataset.minPrediction * 100, 100])
  }, [props.dataset])

  const handleProjectionFilters = (
    key: keyof Filter,
    value: string | number | [number, number],
  ) => {
    let updatedFilters = {...props.filters}
    if (key === 'hits') {
      updatedFilters.hits = value as number
    } else if (key === 'label' || key === 'source' || key === 'prediction') {
      let keyFilters = [...updatedFilters[key]]
      if (keyFilters.includes(value as string)) {
        keyFilters = keyFilters.filter((v: string) => v !== value)
      } else {
        keyFilters.push(value as string)
      }
      updatedFilters[key] = keyFilters
    } else if (key === 'probability') {
      updatedFilters.probability = value as [number, number]
    }
    props.setFilters(updatedFilters)
  }

  const barchartHeight = () =>
    `${(props.dataset.labels.length + 1) * BAR_SIZE}px`

  const sourcesHeight = () =>
    `${(props.dataset.sources.length + 1) * BAR_SIZE}px`

  return (
    <Box>
      <Box w="full">
        <SimpleBoxHeader title="Info & Filters" />
      </Box>
      {/* You need to load data first to see the charts and filters */}
      {props.dataset.data.length === 0 ? (
        <Box>Load data to see filters</Box>
      ) : null}

      {/* Show data and filters */}
      {props.dataset.data.length > 0 ? (
        <Box w="full" pl={2} pr={4} maxH={'500px'} overflowY={'scroll'}>
          <Subtitle pl={2} text="Neighborhood Similarity" />
          <Box w="full" pl={2} pr={2}>
            <SliderController
              text={hits.toString()}
              value={hits}
              min={0}
              max={1}
              step={0.05}
              textWidth={'50px'}
              setValue={setHits}
              setValueEnd={value => {
                setHits(value)
                handleProjectionFilters('hits', value)
              }}
            />
          </Box>
          <Subtitle pl={2} mt={4} text="Ground-truth labels" />
          <Box w="full" h={barchartHeight()}>
            <BarChartFilter
              data={props.dataset.data}
              dataAccessor={(d: ScatterDot) => d.lbl}
              updateFilters={(value: string) =>
                handleProjectionFilters('label', value)
              }
            />
          </Box>
          <Subtitle pl={2} mt={4} text="Predictions" />
          <Box w="full" h={barchartHeight()}>
            <BarChartFilter
              data={props.dataset.data}
              dataAccessor={(d: ScatterDot) => d.prd}
              updateFilters={(value: string) =>
                handleProjectionFilters('prediction', value)
              }
            />
          </Box>

          <Subtitle pl={2} mt={4} text="Predicted Instances (Log)" />
          {props.dataset.labels.map(label => (
            <Box key={label} w="full" h="60px" mb={1} mt={4} ml={1}>
              <StackedBarChart
                keys={[label, 'unl']}
                useLogs={true}
                data={props.dataset.data.filter(el => el.prd === label)}
                title={`${label}`}
                minValue={props.dataset.minPrediction}
                selectionX={selection}
              />
            </Box>
          ))}
          <Box ml={5} mt={2}>
            <RangeSlider
              colorScheme="pink"
              defaultValue={selection}
              min={props.dataset.minPrediction * 100}
              max={100}
              step={1}
              onChangeEnd={(val: [number, number]) => {
                setSelection(val)
                handleProjectionFilters('probability', val)
              }}
            >
              <RangeSliderTrack>
                <RangeSliderFilledTrack />
              </RangeSliderTrack>
              <RangeSliderThumb index={0} backgroundColor={'black'} />
              <RangeSliderThumb index={1} backgroundColor={'black'} />
            </RangeSlider>
          </Box>

          <Subtitle pl={2} mt={4} text="Sources" />
          <Box w="full" h={sourcesHeight()}>
            <BarChartFilter
              data={props.dataset.data}
              dataAccessor={(d: ScatterDot) => d.sr}
              updateFilters={(value: string) =>
                handleProjectionFilters('source', value)
              }
            />
          </Box>
        </Box>
      ) : null}
    </Box>
  )
}

export default Filters
