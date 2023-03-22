import {Float32BufferAttribute, Line} from 'three'
import {extend, ReactThreeFiber} from '@react-three/fiber'
import {Point} from '../../utils/convex-hull'

// https://github.com/pmndrs/react-three-fiber/discussions/1387
// extend line to line_ because typescript confuses line with svgline
extend({Line_: Line})

declare global {
  namespace JSX {
    interface IntrinsicElements {
      line_: ReactThreeFiber.Object3DNode<THREE.Line, typeof Line>
    }
  }
}

interface NeighborhoodPolygonProps {
  points2D: Point[]
  zPosition: number
}

export const NeighborhoodPolygon = ({
  points2D,
  zPosition,
}: NeighborhoodPolygonProps) => {
  // close the polygon
  const positions = new Float32Array((points2D.length + 1) * 3)
  for (let i = 0; i < points2D.length - 1; i++) {
    const i3 = i * 3
    positions[i3 + 0] = points2D[i].x
    positions[i3 + 1] = points2D[i].y
    positions[i3 + 2] = zPosition
  }
  const i3 = (points2D.length - 1) * 3
  positions[i3 + 0] = points2D[0].x
  positions[i3 + 1] = points2D[0].y
  positions[i3 + 2] = zPosition

  const bufferAttribute = new Float32BufferAttribute(positions, 3, false)
  console.log(bufferAttribute)

  return (
    <line_>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" {...bufferAttribute} />
      </bufferGeometry>
      <lineBasicMaterial attach="material" color={'black'} depthTest={true} />
    </line_>
  )
}
