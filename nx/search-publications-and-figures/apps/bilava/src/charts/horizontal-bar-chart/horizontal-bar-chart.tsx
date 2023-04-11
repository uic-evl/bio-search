import {max as d3Max, map as d3Map, InternSet} from 'd3-array'
import styles from './horizontal-bar-chart.module.css'
import {ScaleBand, scaleBand, scaleLinear} from 'd3-scale'
import {colorsMapper} from '../../utils/mapper'
import {AxisVertical} from '../axis/axis'
import {BarChartDatum} from '../../types'

/* eslint-disable-next-line */
export interface HorizontalBarChartProps {
  data: BarChartDatum[]
  width: number
  height: number
  xAccessor: (arg: BarChartDatum) => number | string
  yAccessor: (arg: BarChartDatum) => number | string
  onClick: ((arg: BarChartDatum) => void) | null
}

export function HorizontalBarChart({
  data,
  width,
  height,
  xAccessor,
  yAccessor,
  onClick,
}: HorizontalBarChartProps) {
  const format = (val: string) =>
    val.includes('.') ? val.split('.').at(-1) || '' : val

  const X = d3Map(data, xAccessor) as number[]
  const Y = d3Map(data, yAccessor) as string[]
  const marginLeft = 50
  const paddingY = 0.1
  const max = d3Max(X) || 0

  const xScale = scaleLinear([0, max], [marginLeft, width])
  const yScale = scaleBand(new InternSet(Y), [0, height]).padding(
    paddingY,
  ) as ScaleBand<string>
  const fill = (d: BarChartDatum, i: number) => {
    if (d.selected) {
      return colorsMapper ? colorsMapper[Y[i]] : 'steelblue'
    } else return 'white'
  }
  const stroke = (d: BarChartDatum, i: number) => {
    if (d.selected) {
      return 'none'
    } else {
      return colorsMapper ? colorsMapper[Y[i]] : 'steelblue'
    }
  }

  return data && width > 0 && height > 0 ? (
    <g>
      {data.map((d, i) => {
        const isShortBar = xScale(X[i]) - xScale(0) < 20
        return (
          <g textAnchor="end" fontFamily="sans-serif" fontSize={10}>
            <rect
              x={xScale(0)}
              y={yScale(Y[i])}
              width={d3Max([3, xScale(X[i]) - xScale(0)])}
              height={yScale.bandwidth()}
              fill={fill(d, i)}
              stroke={stroke(d, i)}
              onClick={() => (onClick ? onClick(d) : null)}
              cursor={'pointer'}
            />
            <text
              x={xScale(X[i])}
              y={yScale(Y[i]) || 0 + yScale.bandwidth() / 2}
              dy="0.35em"
              dx={isShortBar ? +4 : -4}
              textAnchor={isShortBar ? 'start' : undefined}
            >
              {X[i]}
            </text>
          </g>
        )
      })}
      {/* <g ref={axisRef} transform={`translate(${marginLeft},0)`}></g> */}
      <AxisVertical
        scale={yScale}
        dimensions={{boundedWidth: width, boundedHeight: height}}
        formatTick={format}
        isOrdinal={true}
        label={''}
      />
    </g>
  ) : null
}

export default HorizontalBarChart
