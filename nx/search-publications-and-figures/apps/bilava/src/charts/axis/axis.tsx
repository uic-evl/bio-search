import {ScaleBand, ScaleContinuousNumeric} from 'd3-scale'
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
          transform={`translate(20, ${
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
