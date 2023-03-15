import {useRef} from 'react'
import {Line, Float32BufferAttribute} from 'three'
import {useFrame, extend, ReactThreeFiber} from '@react-three/fiber'

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

interface SelectionBoxProps {
  points: number[]
}

const SelectionBox = ({points}: SelectionBoxProps) => {
  const refSelection = useRef<Line>(null!)

  useFrame(() => {
    if (refSelection.current && points.length > 0) {
      refSelection.current.geometry.setAttribute(
        'position',
        new Float32BufferAttribute(points, 3, false),
      )
      refSelection.current.frustumCulled = false
      refSelection.current.geometry.attributes.position.needsUpdate = true
    }
  })

  return (
    <>
      {points.length > 0 ? (
        <line_ ref={refSelection}>
          <lineBasicMaterial
            attach="material"
            color={'red'}
            depthTest={false}
          />
        </line_>
      ) : null}
    </>
  )
}

export default SelectionBox
