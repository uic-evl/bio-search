import {Box, BoxProps} from '@chakra-ui/react'
import {ScatterDot} from '../../types'

export const TopLeft = (props: BoxProps) => (
  <Box position="absolute" top={0} left={0} {...props}>
    {props.children}
  </Box>
)

export interface LabelCircleIconProps {
  fill: string
  stroke: string
  size: {width: number; height: number}
  onClick?: () => void
}

export const LabelCircleIcon = ({
  fill,
  stroke,
  size = {width: 20, height: 20},
  onClick,
  ...props
}: LabelCircleIconProps) => {
  return (
    <TopLeft
      width={`${size.width / 2}px`}
      height={`${size.height / 2}px`}
      left={0.25}
      top={0.25}
      {...props}
    >
      <svg width={`${size.width}px`} height={`${size.height}px`}>
        <circle
          cx={size.width / 2}
          cy={size.height / 2}
          r={size.height / 2 - 2}
          fill={fill}
          stroke={stroke}
          strokeWidth={2}
          onClick={onClick ? onClick : undefined}
        ></circle>
      </svg>
    </TopLeft>
  )
}
