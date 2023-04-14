import {Dispatch, SetStateAction, useState} from 'react'
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
import {SimpleBoxHeader} from '../panel-header/panel-header'
import {BarChartFilter} from './bar-chart-filter'
import {Dataset, Filter, ScatterDot} from '../../types'
import StackedBarChart from '../../charts/stacked-bar-chart/stacked-bar-chart'

const BAR_SIZE = 18 // pixels height for horizontal bars

interface SubtitleProps {
  text: string
  pl?: number
  mt?: number
}

const Subtitle = ({text, pl, mt}: SubtitleProps) => (
  <Box w="full" pl={pl} mt={mt}>
    <chakra.span fontWeight="bold">{text.toLowerCase()}</chakra.span>
  </Box>
)

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
  const [selection, setSelection] = useState<
    [[number, number], [number, number]]
  >([
    [0, 0],
    [0, 100],
  ])

  const handleProjectionFilters = (
    key: keyof Filter,
    value: string | number,
  ) => {
    let updatedFilters = {...props.filters}
    if (key === 'hits') {
      updatedFilters.hits = value as number
    } else if (key === 'label') {
      let keyFilters = [...updatedFilters[key]]
      if (keyFilters.includes(value as string)) {
        keyFilters = keyFilters.filter((v: string) => v !== value)
      } else {
        keyFilters.push(value as string)
      }
      updatedFilters[key] = keyFilters
    }
    // let updatedFilter = {...props.filters}
    // // if (Array.isArray(value)) {
    // //   updatedFilter = value
    // // } else {
    // if (key === 'hits') updatedFilter.hits = value as number
    // else {
    //   updatedFilter = props.filters[key].includes(value)
    //     ? props.filters[key].filter(v => v !== value)
    //     : [...props.filters[key], value]
    // }
    // // }

    props.setFilters(updatedFilters)
  }

  const barchartHeight = () =>
    `${(props.dataset.labels.length + 1) * BAR_SIZE}px`

  return (
    <Box>
      <Box w="full">
        <SimpleBoxHeader title="Info & Filters" />
      </Box>
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
        <Subtitle pl={2} text="Ground-truth labels" />
        <Box w="full" h={barchartHeight()}>
          {props.dataset.data && props.dataset.data.length > 0 ? (
            <BarChartFilter
              data={props.dataset.data}
              dataAccessor={(d: ScatterDot) => d.lbl}
              updateFilters={(value: string) =>
                handleProjectionFilters('label', value)
              }
            />
          ) : null}
        </Box>
        <Subtitle pl={2} text="Predictions" />
        <Box w="full" h={barchartHeight()}>
          {props.dataset.data && props.dataset.data.length > 0 ? (
            <BarChartFilter
              data={props.dataset.data}
              dataAccessor={(d: ScatterDot) => d.prd}
              updateFilters={(value: string) =>
                handleProjectionFilters('prediction', value)
              }
            />
          ) : null}
        </Box>
        <Box ml={5} mt={2}>
          <RangeSlider
            colorScheme="pink"
            defaultValue={[0, 100]}
            min={0}
            max={100}
            step={1}
            onChangeEnd={val => {
              // setSelection(val)
              // handleProjectionFilters('prob', val)
            }}
          >
            <RangeSliderTrack>
              <RangeSliderFilledTrack />
            </RangeSliderTrack>
            <RangeSliderThumb index={0} backgroundColor={'black'} />
            <RangeSliderThumb index={1} backgroundColor={'black'} />
          </RangeSlider>
        </Box>

        <Subtitle pl={2} text="Predicted Instances (Log)" />
        {props.dataset.data
          ? props.dataset.labels.map(label => (
              <Box w="full" h="60px" mb={1} mt={4} ml={1}>
                <StackedBarChart
                  keys={[label, 'unl']}
                  useLogs={true}
                  data={props.dataset.data.filter(el => el.prd === label)}
                  title={`${label}`}
                  minValue={0}
                  selection={selection}
                />
              </Box>
            ))
          : null}

        <Subtitle pl={2} text="Sources" />
        <Box w="full" h="90px">
          {props.dataset.data && props.dataset.data.length > 0 ? (
            <BarChartFilter
              data={props.dataset.data}
              dataAccessor={(d: ScatterDot) => d.sr}
              updateFilters={(value: string) =>
                handleProjectionFilters('source', value)
              }
            />
          ) : null}
        </Box>
      </Box>
    </Box>
  )
}

export default Filters
