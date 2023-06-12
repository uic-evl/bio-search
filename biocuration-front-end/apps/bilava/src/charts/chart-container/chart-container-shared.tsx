import {PropsWithChildren, createContext, useContext} from 'react'
import {Dimensions} from '../../types'

const FrameContext = createContext(null)
// This name is a bit confusing as its the same name used
// in the hook to get the div dimensions
export const useFrameDimensions = () => useContext(FrameContext)

interface ChartContainerSharedProps {
  dimensions: Dimensions
}

const ChartContainerShared = (
  props: PropsWithChildren<ChartContainerSharedProps>,
) => {
  const {dimensions} = props
  if (dimensions.boundedHeight === 0 || dimensions.boundedWidth === 0)
    return null

  return (
    <FrameContext.Provider value={dimensions as any}>
      <svg width={dimensions.width} height={dimensions.height}>
        <g
          transform={`translate(${dimensions.marginLeft},${dimensions.marginTop})`}
        >
          {props.children}
        </g>
      </svg>
    </FrameContext.Provider>
  )
}

export default ChartContainerShared
