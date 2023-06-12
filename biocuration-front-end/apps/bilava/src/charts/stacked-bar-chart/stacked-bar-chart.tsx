import {BarChartDatum, ScatterDot} from '../../types'
import styles from './stacked-bar-chart.module.css'
import {bin as d3bin, max} from 'd3-array'
import {stack} from 'd3-shape'
import {scaleLinear} from 'd3-scale'
import {D3BrushEvent, brushX} from 'd3-brush'
import {select} from 'd3-selection'
import {Box} from '@chakra-ui/react'
import {useChartDimensions} from '../use-chart-dimensions/use-chart-dimensions'
import {useEffect, useRef} from 'react'
import ChartContainerShared from '../chart-container/chart-container-shared'
import {colorsMapper} from '../../utils/mapper'
import {AxisBottom} from '../axis/axis'
import {format} from 'd3-format'

/* eslint-disable-next-line */
export interface StackedBarChartProps {
  data: ScatterDot[]
  keys: string[]
  useLogs: boolean
  title: string
  selectionX: [number, number]
  minValue: number
}

interface StackBarDatum {
  label: string
  value: number
}

export function StackedBarChart(props: StackedBarChartProps) {
  const [ref, dimensions] = useChartDimensions({
    marginBottom: 12,
    marginTop: 0,
    marginLeft: 5,
    marginRight: 14,
  })
  const brushRef = useRef(null)

  const values = props.data.map(el => {
    const value = Math.round(el.mp * 100)
    return {label: el.lbl, value}
  })
  const log = (d: number) =>
    props.useLogs ? (d === 0 ? 0 : Math.log10(d + 0.1)) : d

  const bin = d3bin<StackBarDatum, number>()
    .domain([props.minValue, 101])
    .thresholds(Array.from(Array(101).keys()))
    .value(d => d.value)
  const buckets = bin(values)
  const maxBins = max(buckets, d => log(d.length)) || 0

  const stackGenerator = stack().keys(props.keys)
  const transBuckets = buckets.map(el => {
    let series: {[key: string]: number} = {x0: el.x0 || 0, x1: el.x1 || 0}
    // the bucket object
    props.keys.forEach(key => {
      series[key] = log(el.filter(d => d.label === key).length)
    })
    return series
  })
  const series = stackGenerator(transBuckets)

  const xScale = scaleLinear()
    .domain([props.minValue * 100, 100]) // minValue [0,1]
    .range([dimensions.marginLeft, dimensions.width - dimensions.marginRight])

  const yRange = [
    dimensions.height - dimensions.marginBottom,
    dimensions.marginTop,
  ]
  const yScale = scaleLinear().domain([0, maxBins]).nice().range(yRange)

  useEffect(() => {
    const brush = brushX()
      .extent([
        [0, 0],
        [
          dimensions.width - dimensions.marginRight,
          dimensions.height - dimensions.marginBottom,
        ],
      ])
      .on('end', brushed)
    function brushed(event: D3BrushEvent<BarChartDatum>) {
      if (event.selection)
        brush.extent([
          [props.selectionX[0], 0],
          [props.selectionX[1], dimensions.height],
        ])
    }
    const brushSelection = select(brushRef.current)
    brushSelection
      .call(brush as any)
      .call(brush.move as any, props.selectionX.map(xScale as any))
    // eslint-disable-next-line
  }, [dimensions, xScale, props.selectionX])

  return (
    <Box h="full" ref={ref} {...styles}>
      <ChartContainerShared dimensions={dimensions}>
        <g
          ref={brushRef}
          transform={`translate(${dimensions.marginLeft},${dimensions.marginTop})`}
        >
          <text fontSize={12} dominantBaseline="hanging" fill={'black'}>
            {props.title}
          </text>
        </g>
        {series.map(group => (
          <g key={group.key}>
            {group.map(d => (
              <rect
                key={`${group.key}-${d.data.x0}`}
                x={
                  group.key === 'unl'
                    ? xScale(d.data.x0)
                    : xScale(d.data.x0) +
                      (xScale(d.data.x1) - xScale(d.data.x0)) / 2
                }
                width={Math.max(1, (xScale(d.data.x1) - xScale(d.data.x0)) / 2)}
                y={yScale(d.data[group.key])}
                height={yScale(d[0]) - yScale(d[1])}
                fill={colorsMapper[group.key]}
              />
            ))}
          </g>
        ))}
        <AxisBottom
          dimensions={dimensions}
          scale={xScale}
          tickMargin={10}
          fontSize={10}
          showLine={false}
          showTicks={false}
          isOrdinal={false}
          formatTick={format(',')}
        />
      </ChartContainerShared>
    </Box>
  )
}

export default StackedBarChart
