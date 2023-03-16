import {useState, useEffect, useMemo, useRef} from 'react'
import {Box} from '@chakra-ui/react'
import {Color, Float32BufferAttribute, NoBlending} from 'three'
import {Canvas, ThreeEvent} from '@react-three/fiber'
import {OrbitControls} from '@react-three/drei'
import {ScatterDot, ProjectionBuffer} from '../../types'
import {extent} from 'd3-array'
import {colorsMapper} from '../../utils/mapper'
import SelectionBox from './selection-box'
import {ProjectionPoints} from './projection-points'
import {DensityContours} from './density-contours'
import {
  Quadtree,
  quadtree,
  QuadtreeInternalNode,
  QuadtreeLeaf,
} from 'd3-quadtree'

const xAccessor = (d: ScatterDot) => d.x
const yAccessor = (d: ScatterDot) => d.y
const labelAccessor = (d: ScatterDot) => d.lbl
const predictionAccessor = (d: ScatterDot) => d.prd

const searchSelected = (
  tree: Quadtree<ScatterDot>,
  xmin: number,
  ymin: number,
  xmax: number,
  ymax: number,
) => {
  const results: ScatterDot[] = []
  tree.visit((node, x1, y1, x2, y2) => {
    // node can be of two types and we want to iterate over leaves, which are
    // not arrays
    if (!node.length) {
      do {
        const nodeData = (node as QuadtreeLeaf<ScatterDot>).data
        const x = xAccessor(nodeData)
        const y = yAccessor(nodeData)

        if (x >= xmin && x < xmax && y >= ymin && y < ymax) {
          results.push(nodeData)
        }
      } while (
        (node = (node as QuadtreeLeaf<ScatterDot>).next as
          | QuadtreeInternalNode<ScatterDot>
          | QuadtreeLeaf<ScatterDot>)
      )
    }
    return x1 >= xmax || y1 >= ymax || x2 < xmin || y2 < ymin
  })
  // results.sort((a, b) => (a.hits < b.hits ? 1 : -1));
  return results
}

export interface ThreeScatterplotProps {
  classifier: string
  data: ScatterDot[]
  cameraLeft: number
  cameraBottom: number
  width: number
  height: number
}

interface CanvasPoint {
  x: number
  y: number
}

export function ThreeScatterplot(props: ThreeScatterplotProps) {
  const [data, setData] = useState<ProjectionBuffer | null>(null)
  const [cameraWidth, setCameraWidth] = useState<number | null>(null)
  const [cameraHeight, setCameraHeight] = useState<number | null>(null)
  const [pointStart, setPointStart] = useState<CanvasPoint | null>(null)
  const [selection, setSelection] = useState<number[]>([])
  const [quadTree, setQuadTree] = useState<Quadtree<ScatterDot> | null>(null)
  const [middle, setMiddle] = useState<CanvasPoint | null>(null)

  const padding = 50
  const dpr = Math.min(window.devicePixelRatio, 2)

  const onPointerDown = (e: ThreeEvent<PointerEvent>) => {
    if (e.ctrlKey) return
    e.stopPropagation()

    if (e.altKey) {
      setPointStart({x: e.unprojectedPoint.x, y: e.unprojectedPoint.y})
    }
  }

  const onPointerMove = (e: ThreeEvent<PointerEvent>) => {
    // don't do anything else if we are just panning
    if (e.ctrlKey) return
    if ((1 && e.buttons) === 0) return
    if (!pointStart) return

    if (e.altKey) {
      e.stopPropagation()

      const selectionBox = []
      selectionBox.length = 3 * 5

      selectionBox[0] = pointStart.x
      selectionBox[1] = pointStart.y
      selectionBox[2] = 10

      selectionBox[3] = e.unprojectedPoint.x
      selectionBox[4] = pointStart.y
      selectionBox[5] = 10

      selectionBox[6] = e.unprojectedPoint.x
      selectionBox[7] = e.unprojectedPoint.y
      selectionBox[8] = 10

      selectionBox[9] = pointStart.x
      selectionBox[10] = e.unprojectedPoint.y
      selectionBox[11] = 10

      // to close polygon
      selectionBox[12] = pointStart.x
      selectionBox[13] = pointStart.y
      selectionBox[14] = 10

      setSelection(selectionBox)
    }
  }

  const onPointerUp = (e: ThreeEvent<PointerEvent>) => {
    // don't do anything else if we are just panning
    if (e.ctrlKey) return
    if (e.altKey) {
      if (!quadTree) return
      const selectedPoints = searchSelected(
        quadTree,
        selection[0],
        selection[7],
        selection[3],
        selection[1],
      )
    }
  }

  useEffect(() => {
    const extentX = extent(props.data, xAccessor)
    const extentY = extent(props.data, yAccessor)
    if (extentX[0] === undefined || extentX[1] === undefined) return
    if (extentY[0] === undefined || extentY[1] === undefined) return

    // previous on useMemo
    const totalPoints = props.data.length
    const positionsBuffer = new Float32Array(totalPoints * 3)
    const fillsBuffer = new Float32Array(totalPoints * 3)
    const strokesBuffer = new Float32Array(totalPoints * 3)

    for (let i = 0; i < totalPoints; i++) {
      const i3 = i * 3
      // setup positions for 2D
      positionsBuffer[i3 + 0] = xAccessor(props.data[i])
      positionsBuffer[i3 + 1] = yAccessor(props.data[i])
      positionsBuffer[i3 + 2] = 0.0
      // colors for ground truth
      const fills = new Color(colorsMapper[labelAccessor(props.data[i])])
      // colors for prediction
      const strokes = new Color(colorsMapper[predictionAccessor(props.data[i])])
      // assign values to buffers
      fillsBuffer[i3 + 0] = fills.r
      fillsBuffer[i3 + 1] = fills.g
      fillsBuffer[i3 + 2] = fills.b

      strokesBuffer[i3 + 0] = strokes.r
      strokesBuffer[i3 + 1] = strokes.g
      strokesBuffer[i3 + 2] = strokes.b
    }

    const qTree = quadtree<ScatterDot>()
      .x(xAccessor)
      .y(yAccessor)
      .addAll(props.data)

    setData({
      position: new Float32BufferAttribute(positionsBuffer, 3, false),
      fillColor: new Float32BufferAttribute(fillsBuffer, 3, false),
      strokeColor: new Float32BufferAttribute(strokesBuffer, 3, false),
    })
    setCameraWidth(extentX[1] - extentX[0] + padding)
    setCameraHeight(extentY[1] - extentY[0] + padding)
    setSelection([])
    setQuadTree(qTree)
    setMiddle({
      x: (extentX[0] + extentX[1]) / 2,
      y: (extentY[0] + extentY[1]) / 2,
    })
  }, [props.data])

  return (
    <Box w={props.width} h={props.height}>
      {cameraWidth && cameraHeight ? (
        <Canvas
          orthographic={true}
          camera={{
            left: props.cameraLeft,
            right: cameraWidth,
            top: cameraHeight,
            bottom: props.cameraBottom,
            position: [0, 0, 40],
          }}
          dpr={dpr}
        >
          <pointLight color={'white'} position={[0, 0, 100]} />
          <OrbitControls
            makeDefault
            enableDamping={true}
            dampingFactor={0.05}
            minDistance={10}
            maxDistance={350}
            enableRotate={false}
          />
          {/* <axesHelper args={[500]} /> */}
          {/* plane to track selection events */}
          {middle ? (
            <mesh
              position={[middle.x, middle.y, -10]}
              scale={[cameraWidth * 1, cameraHeight * 1, 1]}
              onPointerDown={onPointerDown}
              onPointerMove={onPointerMove}
              onPointerUp={onPointerUp}
            >
              <planeGeometry />
              <meshBasicMaterial
                color="white"
                depthTest={true}
                blending={NoBlending}
                toneMapped={false}
              />
            </mesh>
          ) : null}
          {/* contours per classifier class */}
          {data ? (
            <DensityContours
              classifier={props.classifier}
              data={props.data}
              width={800}
              height={800}
            />
          ) : null}
          {/* scatterplot dots on scene */}
          {data ? <ProjectionPoints buffer={data} data={props.data} /> : null}
          {/* box for brushing over the scatterplot */}
          <SelectionBox points={selection} />
        </Canvas>
      ) : null}
    </Box>
  )
}

export default ThreeScatterplot
