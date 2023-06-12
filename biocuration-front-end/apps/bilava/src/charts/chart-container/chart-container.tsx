import {
  createContext,
  useContext,
  useRef,
  useState,
  useEffect,
  PropsWithChildren,
} from 'react'
import {select} from 'd3-selection'
import {zoom} from 'd3-zoom'
import {Box} from '@chakra-ui/react'
import {useChartDimensions} from '../use-chart-dimensions/use-chart-dimensions.js'

const ChartContext = createContext(null)

export interface ChartContainerProps {
  useZoom: boolean
  ml: number
  mr: number
  mt: number
  mb: number
}

export function ChartContainer(props: PropsWithChildren<ChartContainerProps>) {
  // Every children should assume its being translated by the first <g>
  const [ref, dimensions] = useChartDimensions({
    marginLeft: props.ml,
    marginRight: props.mr,
    marginTop: props.mt,
    marginBottom: props.mb,
  })
  // zoom transforms
  const [{x, y, k}, setTransform] = useState({x: 0, y: 0, k: 1})

  const svgRef = useRef(null)
  const [svg, setSVG] = useState(null)
  useEffect(() => setSVG(svgRef.current), [])

  useEffect(() => {
    // TODO: what are the proper types for the anys below?
    if (!svg || !props.useZoom) return
    const selection = select(svg)
    if (!selection) return

    const zoomFn = zoom()
      .scaleExtent([1, Infinity])
      .on('zoom', (event: any, datum) => {
        setTransform(event.transform)
      })
    selection.call(zoomFn as any)

    return () => selection.on('.zoom', null) as any
  }, [svg, props.useZoom])

  return (
    <Box ref={ref} w="full" h="full">
      <ChartContext.Provider value={dimensions}>
        <svg
          x={0}
          y={0}
          width={dimensions.width}
          height={dimensions.height}
          ref={svgRef}
        >
          <g
            transform={`translate(${x + dimensions.marginLeft},  ${
              y + dimensions.marginTop
            }) scale(${k})`}
          >
            {props.children}
          </g>
        </svg>
      </ChartContext.Provider>
    </Box>
  )
}

export const useChartContext = () => useContext(ChartContext)
export default ChartContainer
