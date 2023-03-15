import {useState, useEffect, useMemo, useRef} from 'react'
import {Box} from '@chakra-ui/react'
import {BufferAttribute, Color, NoBlending, ShaderMaterial} from 'three'
import {Canvas, ThreeEvent} from '@react-three/fiber'
import {OrbitControls} from '@react-three/drei'
import {ScatterDot} from '../../types'
import {extent} from 'd3-array'
import {colorsMapper} from '../../utils/mapper'
import SelectionBox from './selection-box'

const fragmentShader = `
varying vec3 vInsideColor;
varying vec3 vOutsideColor;
varying vec2 vUV;

void main() {
    float distanceFromCenter = distance(gl_PointCoord, vec2(.5));
    float radius = 0.3;
    float stroke = 0.5;

    if (distanceFromCenter <= radius) {
        float circle = 1. - step(radius, distanceFromCenter);
        gl_FragColor = vec4(vInsideColor, 0.7);
    } else if (distanceFromCenter <= stroke) {
        float circle = 1. - step(radius, distanceFromCenter);
        gl_FragColor = vec4(vOutsideColor, 0.7);
    } else {
        discard;
    }
}
`

const vertexShader = `
attribute vec3 fillColor;
attribute vec3 strokeColor;
uniform float uSize;

varying vec3 vInsideColor;
varying vec3 vOutsideColor;
varying vec2 vUV;
varying float radius;
varying float strokeWidth;

float map(float value, float min1, float max1, float min2, float max2) {
  return min2 + (value - min1) * (max2 - min2) / (max1 - min1);
}

void main() {
    vec4 modelPosition = modelMatrix * vec4(position, 1.0);
    vec4 viewPosition = viewMatrix * modelPosition;
    vec4 projectedPosition = projectionMatrix * viewPosition;
    gl_Position = projectedPosition;

    gl_PointSize = uSize;

    vInsideColor = fillColor;
    vOutsideColor = strokeColor;
    vUV = uv;
    radius = map(uSize / 2., 0., uSize, 0., 1.);
    strokeWidth = radius;
}
`

const xAccessor = (d: ScatterDot) => d.x
const yAccessor = (d: ScatterDot) => d.y
const labelAccessor = (d: ScatterDot) => d.lbl
const predictionAccessor = (d: ScatterDot) => d.pred

export interface ThreeScatterplotProps {
  data: ScatterDot[]
  width: number
  height: number
}

interface CanvasPoint {
  x: number
  y: number
}

export function ThreeScatterplot(props: ThreeScatterplotProps) {
  const [cameraWidth, setCameraWidth] = useState<number | null>(null)
  const [cameraHeight, setCameraHeight] = useState<number | null>(null)
  const [pointStart, setPointStart] = useState<CanvasPoint | null>(null)
  const [selection, setSelection] = useState<number[]>([])

  const padding = 50
  const dpr = Math.min(window.devicePixelRatio, 2)

  const pointsMaterial = new ShaderMaterial({
    depthWrite: true,
    blending: NoBlending,
    vertexColors: true,
    fragmentShader: fragmentShader,
    vertexShader: vertexShader,
    uniforms: {uSize: {value: 10 * dpr}},
  })

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
      selectionBox[2] = 3

      selectionBox[3] = e.unprojectedPoint.x
      selectionBox[4] = pointStart.y
      selectionBox[5] = 3

      selectionBox[6] = e.unprojectedPoint.x
      selectionBox[7] = e.unprojectedPoint.y
      selectionBox[8] = 3

      selectionBox[9] = pointStart.x
      selectionBox[10] = e.unprojectedPoint.y
      selectionBox[11] = 3

      // to close polygon
      selectionBox[12] = pointStart.x
      selectionBox[13] = pointStart.y
      selectionBox[14] = 3

      setSelection(selectionBox)
    }
  }

  const onPointerUp = (e: ThreeEvent<PointerEvent>) => {
    // don't do anything else if we are just panning
    if (e.ctrlKey) return
    if (e.altKey) {
      // TOOD: search
    }
  }

  const points = useMemo(() => {
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
    return {
      position: new BufferAttribute(positionsBuffer, 3),
      fillColor: new BufferAttribute(fillsBuffer, 3),
      strokeColor: new BufferAttribute(strokesBuffer, 3),
    }
  }, [props.data])

  useEffect(() => {
    const extentX = extent(props.data, xAccessor)
    const extentY = extent(props.data, yAccessor)

    setCameraWidth((extentX[1] ?? 0) - (extentX[0] ?? 0) + padding)
    setCameraHeight((extentY[1] ?? 0) - (extentY[0] ?? 0) + padding)
  }, [props.data])

  return (
    <Box w={props.width} h={props.height}>
      {cameraWidth && cameraHeight ? (
        <Canvas
          orthographic={true}
          camera={{
            left: 0,
            right: cameraWidth,
            top: cameraHeight,
            bottom: 0,
            position: [0, 0, 40],
          }}
          dpr={dpr}
          color="black"
        >
          <pointLight color={'white'} position={[0, 0, 100]} />
          <OrbitControls
            enableDamping={true}
            dampingFactor={0.05}
            minDistance={10}
            maxDistance={350}
            enableRotate={false}
          />
          {/* plane to track selection events */}
          <mesh
            position={[0, 0, -1]}
            scale={[cameraWidth * 2, cameraHeight * 2, 1]}
            onPointerDown={onPointerDown}
            onPointerMove={onPointerMove}
            onPointerUp={onPointerUp}
          >
            <planeGeometry />
            <meshBasicMaterial color="green" />
          </mesh>
          {/* scatterplot dots on scene */}
          <points
            material={pointsMaterial}
            onClick={e => {
              console.log(e)
            }}
          >
            <bufferGeometry>
              <bufferAttribute
                attach="attributes-position"
                {...points.position}
              />
              <bufferAttribute
                attach="attributes-fillColor"
                {...points.fillColor}
              />
              <bufferAttribute
                attach="attributes-strokeColor"
                {...points.strokeColor}
              />
            </bufferGeometry>
          </points>
          <SelectionBox points={selection} />
        </Canvas>
      ) : null}
    </Box>
  )
}

export default ThreeScatterplot
