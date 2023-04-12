import {useState, useMemo, useEffect} from 'react'
import {ScatterDot, BarChartDatum, Dimensions, Filter} from '../../types'
import {rollup} from 'd3-array'
import ChartContainer from '../../charts/chart-container/chart-container'
import {useChartContext} from '../../charts/chart-container/chart-container'
import HorizontalBarChart from '../../charts/horizontal-bar-chart/horizontal-bar-chart'

interface BarChartFilterProps {
  data: ScatterDot[]
  dataAccessor: (arg: ScatterDot) => string
  updateFilters: ((arg: string) => void) | null
}

export const BarChartFilter = ({
  data,
  dataAccessor,
  updateFilters,
}: BarChartFilterProps) => {
  const [barFilters, setBarFilters] = useState<BarChartDatum[]>([])

  useEffect(() => {
    if (!data || data.length === 0) return
    const updateFilters = () => {
      const rolledDots = rollup<ScatterDot, number, string>(
        data,
        v => v.length,
        dataAccessor,
      )
      const filters = Array.from(rolledDots).map(arr => ({
        field: arr[0],
        count: arr[1] as number,
        selected: true,
      }))
      filters.sort((a, b) => {
        if (a.field < b.field) return -1
        if (a.field > b.field) return 1
        return 0
      })
      setBarFilters(filters)
    }
    updateFilters()
  }, [data])

  const handleOnBarClick = (filter: BarChartDatum) => {
    const newFilters = [...barFilters].map(v => {
      if (v.field === filter.field) return {...v, selected: !filter.selected}
      else return v
    })
    setBarFilters(newFilters)
    if (updateFilters) updateFilters(filter.field)
  }

  return (
    <ChartContainer ml={0} mr={20} mt={5} mb={0} useZoom={false}>
      <ChartWrapper data={barFilters} onClick={handleOnBarClick} />
    </ChartContainer>
  )
}

interface ChartWrapperProps {
  data: BarChartDatum[]
  onClick: (arg: BarChartDatum) => void
}

const ChartWrapper = ({data, onClick}: ChartWrapperProps) => {
  const dimensions = useChartContext() as unknown as Dimensions

  return (
    <HorizontalBarChart
      data={data}
      width={dimensions.boundedWidth}
      height={dimensions.boundedHeight}
      xAccessor={(d: BarChartDatum) => d.count}
      yAccessor={(d: BarChartDatum) => d.field}
      onClick={onClick}
    />
  )
}
