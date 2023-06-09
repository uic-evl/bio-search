import {ScaleBand, ScaleContinuousNumeric, ScaleLinear} from 'd3-scale'
import {ticks as d3Ticks} from 'd3-array'

import styles from './axis.module.css'

interface AxisHorizontalProps {
  dimensions: {boundedWidth: number; boundedHeight: number}
  label: string
  isOrdinal: boolean
  formatTick?: (arg: number | string) => string
  scale: ScaleContinuousNumeric<number, number>
}

export const AxisHorizontal = ({
  dimensions,
  label,
  isOrdinal,
  formatTick,
  scale,
}: AxisHorizontalProps) => {
  const numberTicks =
    dimensions.boundedWidth < 600
      ? dimensions.boundedWidth / 100
      : dimensions.boundedWidth / 250

  const [min, max] = scale.range()
  const ticks = isOrdinal ? scale.domain() : d3Ticks(min, max, numberTicks)

  return (
    <g
      className={styles['Axis AxisHorizontal']}
      transform={`translate(0, 13)`}
      // {...props}
    >
      {ticks.map((tick, i) => (
        <text
          key={tick}
          className={styles['Axis__tick']}
          transform={`translate(${scale(tick)}, ${
            dimensions.boundedHeight - 5
          })`}
        >
          {formatTick ? formatTick(tick) : tick}
        </text>
      ))}
      {label && (
        <text
          className={styles['Axis__label']}
          transform={`translate(${dimensions.boundedWidth / 2}, 0)`}
        >
          {label}
        </text>
      )}
    </g>
  )
}

interface AxisVerticalProps {
  dimensions: {boundedWidth: number; boundedHeight: number}
  label: string
  isOrdinal: boolean
  formatTick?: ((arg: number) => string) | ((arg: string) => string)
  scale: ScaleBand<string>
}

export const AxisVertical = ({
  dimensions,
  label,
  isOrdinal,
  formatTick,
  scale,
}: AxisVerticalProps) => {
  const numberTicks = dimensions.boundedHeight / 70
  const [min, max] = scale.range()
  const ticks = isOrdinal ? scale.domain() : d3Ticks(min, max, numberTicks)

  // {...props}>
  return (
    <g className={styles['Axis AxisVertical']}>
      {ticks.map((tick, i) => (
        <text
          key={tick}
          className={styles['Axis__tick']}
          transform={`translate(12, ${
            (scale(tick as string) || 0) + scale.bandwidth() / 2
          })`}
        >
          {formatTick ? formatTick(tick as never) : tick}
        </text>
      ))}
      {label && (
        <text
          className={styles['Axis__label']}
          transform={`translate(50px, ${
            dimensions.boundedHeight / 2
          }px) rotate(-90deg)`}
        >
          {label}
        </text>
      )}
    </g>
  )
}

interface AxisBottomProps {
  dimensions: {boundedWidth: number; boundedHeight: number}
  formatTick: ((arg: number) => string) | ((arg: string) => string)
  scale: ScaleLinear<number, number>
  showLine: boolean
  showTicks: boolean
  tickMargin: number
  fontSize: number
  isOrdinal: boolean
}

export const AxisBottom = (props: AxisBottomProps) => {
  const numberTicks = props.isOrdinal
    ? props.scale.domain().length
    : props.dimensions.boundedWidth < 600
    ? props.dimensions.boundedWidth / 100
    : props.dimensions.boundedWidth / 250

  const ticks = props.isOrdinal
    ? props.scale.domain()
    : props.scale.ticks(numberTicks)

  const textProps = (tick: number) => ({
    dominantBaseline: 'auto',
    transform: `translate(${props.scale(tick)}, ${+props.tickMargin})`,
    textAnchor: 'middle',
  })

  const tickProps = (tick: number) => ({
    x1: props.scale(tick),
    x2: props.scale(tick),
    y2: +5,
    stroke: 'black',
  })

  return (
    <g transform={`translate(0, ${props.dimensions.boundedHeight})`}>
      <line
        x2={props.dimensions.boundedWidth}
        stroke={props.showLine ? 'black' : undefined}
      />
      {ticks.map(tick => (
        <g key={`tick-info=${tick}`}>
          <text
            key={`ax-bt-${tick}`}
            {...textProps(tick)}
            fontSize={props.fontSize}
          >
            {props.formatTick(tick as never)}
          </text>
          {props.showTicks && (
            <line key={`ax-bl-${tick}`} {...tickProps(tick)} />
          )}
        </g>
      ))}
    </g>
  )
}

// const axisComponentsByDimension = {
//   x: AxisHorizontal,
//   y: AxisVertical,
// }

// /* eslint-disable-next-line */
// export interface AxisProps {
//   axis: 'x' | 'y'
//   dimensions: {boundedWidth: number; boundedHeight: number}
//   isOrdinal: boolean
//   label: string
//   formatTick?: (arg: number | string) => string
//   scale: ScaleContinuousNumeric<number, number> | ScaleBand<string>
// }

// export const Axis = ({
//   axis,
//   dimensions,
//   isOrdinal,
//   label,
//   scale,
//   formatTick,
// }: AxisProps) => {
//   const Component = axisComponentsByDimension[axis]

//   return (
//     <Component
//       dimensions={dimensions}
//       isOrdinal={isOrdinal}
//       label={label}
//       formatTick={formatTick}
//       scale={scale}
//     />
//   )
// }
