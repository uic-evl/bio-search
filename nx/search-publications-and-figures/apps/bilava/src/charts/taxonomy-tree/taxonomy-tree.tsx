import {useEffect, useState} from 'react'
import ChartContainer, {
  useChartContext,
} from '../chart-container/chart-container'
import {colorsMapper} from '../../utils/mapper'
import {TreeData, Dimensions} from '../../types'
import useTaxonomyTree from '../use-taxonomy-tree/use-taxonomy-tree'
import {HierarchyNode} from 'd3-hierarchy'
import {format as d3Format} from 'd3-format'
import {scaleLinear} from 'd3-scale'
import {sum} from 'd3-array'

export interface TaxonomyTreeProps {
  name: string
  data: TreeData
  leftContainerWidth: number
  rowHeight: number
  barHeight: number
  nodeRadius: number
  nodeWidth: number
}

export function TaxonomyTree(props: TaxonomyTreeProps) {
  const dimensions = useChartContext() as unknown as Dimensions
  const [data, setData] = useTaxonomyTree(
    props.data.taxonomy,
    props.data.data,
    props.rowHeight,
    props.name,
  )
  if (!dimensions) return null

  const calcBranchWidth = (depth: number) =>
    dimensions.width -
    dimensions.marginLeft -
    dimensions.marginRight -
    depth * props.leftContainerWidth

  const handleCircleClick = (isExpanded: boolean, i: number) => {
    const newData = [...(data as any)]
    newData[i].expanded = isExpanded
    let accumY = 0
    for (let node of newData) {
      node.y = accumY
      accumY += node.expanded
        ? props.rowHeight
        : props.rowHeight - props.barHeight
    }
    // TODO: fix by typing the useTaxonomyTree hook
    if (setData) setData(newData as any)
  }

  const handleColored = (i: number) => {
    // Make colored the selected row
    const newData = [...(data as any)]
    for (let node of newData) node.colored = false
    newData[i].colored = true
    if (setData) setData(newData as any)
  }

  // HierarchyNode<unknown>
  const connectorDPath = (d: any) => `M ${
    d.depth * props.leftContainerWidth + props.rowHeight / 4
  } ${d.y + props.rowHeight / 2 - props.rowHeight / 4}
h ${-props.leftContainerWidth / 2 - props.rowHeight / 4}
v ${-d.y + d.parent.y + props.nodeRadius}`

  return (
    <ChartContainer ml={0} mr={20} mt={5} mb={0} useZoom={false}>
      {data ? (
        <>
          <g>
            {(data as any).map((d: HierarchyNode<unknown>) => {
              if (d.depth > 0) {
                return (
                  <path
                    key={(d.data as any).id}
                    fill="none"
                    stroke="#999"
                    transform={`translate(${dimensions.marginLeft}, ${dimensions.marginTop})`}
                    d={connectorDPath(d)}
                  ></path>
                )
              } else {
                return null
              }
            })}
          </g>
          {/* Tree branches */}
          <g
            transform={`translate(${dimensions.marginLeft}, ${dimensions.marginTop})`}
          >
            {(data as any).map((d: any, i: number) => (
              <TreeBranch
                key={d.data.id}
                width={calcBranchWidth(d.depth)}
                height={props.rowHeight}
                y={d.y}
                x={d.depth * props.leftContainerWidth}
                name={d.data.id}
                expanded={d.expanded}
                value={d.value}
                children={d.children}
                barHeight={props.barHeight}
                nodeRadius={props.nodeRadius}
                nodeWidth={props.nodeWidth}
                colored={d.colored}
                onClickCircle={isExpanded => handleCircleClick(isExpanded, i)}
                onSetColored={() => handleColored(i)}
              />
            ))}
          </g>
        </>
      ) : null}
    </ChartContainer>
  )
}

interface TreeBranchProps {
  name: string // branch name
  value: number // total number of elements in branch
  width: number
  height: number // Maximum height for branch
  barHeight: number // Height allocated for stacked bar
  x: number // x displacement
  y: number // y displacement
  expanded: boolean // whether bar should show stacked bar or not
  children: HierarchyNode<unknown> // items to appear in stacked bar
  onClickCircle: (arg: boolean) => void
  onSetColored: () => void
  nodeRadius: number
  nodeWidth: number // Width for node square container
  colored: boolean // boolean, display colored stacked bar or grey
}

const TreeBranch = (props: TreeBranchProps) => {
  const [barData, setBarData] = useState(null)
  const containerHeight = () =>
    props.expanded ? props.height : props.height - props.barHeight
  // parent in charge of updating array status for rerender
  const handleClickCircle = () => props.onClickCircle(!props.expanded)
  const handleClickText = () => props.onSetColored()
  const displayName = (v: string) => {
    // return a from d.c.a
    const i = v.lastIndexOf('.')
    return i >= 0 ? v.slice(i + 1, v.length) : v
  }
  const format = d3Format(',d')

  useEffect(() => {
    const newBarData = (props.children as any).map((d: any) => ({
      name: displayName(d.data.id),
      value: d.value,
      // mapping does not include taxonomy name
      prefix: props.name.slice(props.name.indexOf('.') + 1),
    }))
    setBarData(newBarData)
  }, [props.children, props.name])

  return (
    <svg y={props.y} x={props.x} width={props.width} height={containerHeight()}>
      <circle
        className="tree-branch-node"
        cx={props.nodeWidth / 2}
        cy={(props.height - props.barHeight) / 2}
        fill={props.expanded ? 'black' : 'white'}
        stroke={'black'}
        r={props.nodeRadius}
      ></circle>

      <rect
        x={0}
        y={0}
        width={props.nodeWidth}
        height={props.height - props.barHeight}
        fillOpacity={0}
        fill="black"
        cursor="pointer"
        onClick={handleClickCircle}
      ></rect>

      <text
        className="tree-branch-text"
        transform={`translate(${props.nodeWidth},${
          (props.height - props.barHeight) / 2
        })`}
        dominantBaseline="middle"
        onClick={handleClickText}
      >
        {`${displayName(props.name)}  `}
        <tspan fontWeight="bold">{format(props.value)}</tspan>
      </text>

      {barData ? (
        <HorizontalStackedBar
          data={barData}
          size={{width: props.width - props.nodeWidth, height: props.barHeight}}
          translation={{x: props.nodeWidth, y: props.height - props.barHeight}}
          colored={props.colored}
        />
      ) : null}
    </svg>
  )
}

interface BarData {
  name: string
  value: number
  prefix: string
}

interface StackedItem {
  name: string
  value: number
  startValue: number
  endValue: number
  prefix: string
  normValue: number
}

interface StackedBarProps {
  data: BarData[]
  size: {width: number; height: number}
  translation: {x: number; y: number}
  colored: boolean
}

const HorizontalStackedBar = (props: StackedBarProps) => {
  const [stack, setStack] = useState<StackedItem[] | null>(null)

  // Scales
  const xScale = scaleLinear([0, 1], [0, props.size.width])

  // Accessors for stacked items
  const xAccessor = (d: StackedItem) => xScale(d.startValue)
  const widthAccessor = (d: StackedItem) =>
    xScale(d.endValue) - xScale(d.startValue)
  const translateTextAccessor = (d: StackedItem) =>
    `translate(${
      (xScale(d.endValue) - xScale(d.startValue)) / 2 + xScale(d.startValue)
    }, ${props.size.height / 2})`
  const textAccessor = (d: StackedItem) =>
    xScale(d.endValue) - xScale(d.startValue) > 100
      ? d.name
      : xScale(d.endValue) - xScale(d.startValue) > 50
      ? d.name.substring(0, 3)
      : d.name.substring(0, 1)

  // transform input data into stacks
  useEffect(() => {
    const total = sum(props.data, d => d.value)
    let value = 0
    let newStack = null as StackedItem[] | null

    if (total > 0) {
      newStack = props.data.map(d => ({
        name: d.name,
        value: d.value,
        normValue: d.value / total,
        startValue: value / total,
        endValue: (value += d.value) / total,
        prefix: d.prefix,
      }))
    } else {
      newStack = [
        {
          name: 'no data',
          value: props.size.width,
          normValue: 1,
          startValue: 0,
          endValue: 1,
          prefix: '',
        },
      ]
    }
    setStack(newStack)
  }, [props.data, props.size.width])

  return (
    <g
      stroke="white"
      transform={`translate(${props.translation.x}, ${props.translation.y})`}
    >
      {stack
        ? stack.map((d, i) => {
            return (
              <g key={`bar-${d.name}`}>
                <g key={d.name}>
                  <rect
                    key={`rect-${d.name}`}
                    fill={
                      props.colored && colorsMapper[`${d.prefix}.${d.name}`]
                        ? colorsMapper[`${d.prefix}.${d.name}`]
                        : 'gainsboro'
                    }
                    x={xAccessor(d)}
                    y={0}
                    width={widthAccessor(d)}
                    height={props.size.height}
                  ></rect>
                </g>
                <g
                  key={`text-${d.name}`}
                  stroke="black"
                  fontSize="12"
                  fontWeight="normal"
                >
                  <text
                    key={d.name}
                    transform={translateTextAccessor(d)}
                    textAnchor="middle"
                    fill="black"
                    dominantBaseline="middle"
                    cursor="pointer"
                  >
                    {textAccessor(d)}
                  </text>
                </g>
              </g>
            )
          })
        : null}
    </g>
  )
}

export default TaxonomyTree
