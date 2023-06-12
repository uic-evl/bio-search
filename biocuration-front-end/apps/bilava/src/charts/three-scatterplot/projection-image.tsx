import {ThreeEvent} from '@react-three/fiber'
import {Dispatch, SetStateAction, useMemo} from 'react'
import {
  Color,
  Float32BufferAttribute,
  MeshBasicMaterial,
  PlaneGeometry,
  ShaderMaterial,
} from 'three'
import {ProjectionBuffer, ScatterDot} from '../../types'
import {colorsMapper} from '../../utils/mapper'

const xAccessor = (d: ScatterDot) => d.x
const yAccessor = (d: ScatterDot) => d.y
const labelAccessor = (d: ScatterDot) => d.lbl
const predictionAccessor = (d: ScatterDot) => d.prd

interface ProjectionImageProps {
  scatterdot: ScatterDot
  material: MeshBasicMaterial
  geometry: PlaneGeometry
  pointMaterial: ShaderMaterial
  onClick: (arg: ThreeEvent<MouseEvent>) => void
  setPointInterest: Dispatch<SetStateAction<ScatterDot | null>>
}

export const ProjectionImage = ({
  scatterdot,
  material,
  geometry,
  pointMaterial,
  onClick,
  setPointInterest,
}: ProjectionImageProps) => {
  const zPosition = 10

  const classMaterial = pointMaterial.clone()
  classMaterial.uniforms = {
    uSize: {value: 500},
    uSizeAttenuation: {value: true},
  }

  const dotBuffer = useMemo<ProjectionBuffer>(() => {
    const positionsBuffer = new Float32Array(3)
    const fillsBuffer = new Float32Array(3)
    const strokesBuffer = new Float32Array(3)

    positionsBuffer[0] = xAccessor(scatterdot)
    positionsBuffer[1] = yAccessor(scatterdot)
    positionsBuffer[2] = zPosition + 2

    const fillColor = new Color(colorsMapper[labelAccessor(scatterdot)])
    const strokeColor = new Color(colorsMapper[predictionAccessor(scatterdot)])
    fillsBuffer[0] = fillColor.r
    fillsBuffer[1] = fillColor.g
    fillsBuffer[2] = fillColor.b

    strokesBuffer[0] = strokeColor.r
    strokesBuffer[1] = strokeColor.g
    strokesBuffer[2] = strokeColor.b

    return {
      position: new Float32BufferAttribute(positionsBuffer, 3, false),
      fillColor: new Float32BufferAttribute(fillsBuffer, 3, false),
      strokeColor: new Float32BufferAttribute(strokesBuffer, 3, false),
    }
  }, [scatterdot])

  const handleOnClickSelect = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation()
    setPointInterest(scatterdot)
  }

  return (
    <group>
      <mesh
        geometry={geometry}
        material={material}
        position={[scatterdot.x, scatterdot.y, 10]}
        onClick={onClick}
      />
      <points material={classMaterial}>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            {...dotBuffer.position}
          />
          <bufferAttribute
            attach="attributes-fillColor"
            {...dotBuffer.fillColor}
          />
          <bufferAttribute
            attach="attributes-strokeColor"
            {...dotBuffer.strokeColor}
          />
        </bufferGeometry>
      </points>
      <mesh
        position={[
          scatterdot.x + geometry.parameters.width / 2.8,
          scatterdot.y + geometry.parameters.height / 2.8,
          zPosition + 3,
        ]}
        onClick={handleOnClickSelect}
      >
        <planeGeometry args={[2, 2]} />
        <meshBasicMaterial color={'black'} toneMapped={false} />
      </mesh>
    </group>
  )
}
