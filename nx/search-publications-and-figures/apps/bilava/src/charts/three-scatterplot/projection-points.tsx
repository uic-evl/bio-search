import {useState, useEffect, useRef, Dispatch, SetStateAction} from 'react'
import {
  Mesh,
  MeshBasicMaterial,
  NoBlending,
  PlaneGeometry,
  Points,
  ShaderMaterial,
  TextureLoader,
} from 'three'
import {ThreeEvent, useFrame} from '@react-three/fiber'
import {ProjectionBuffer, ScatterDot} from '../../types'
import {fragmentShader, vertexShader} from './shaders/scatterdot-shader'
import {ProjectionImage} from './projection-image'

interface Thumbnail {
  data: ScatterDot
  material: MeshBasicMaterial
  geometry: PlaneGeometry
}

interface ProjectionPointsProps {
  buffer: ProjectionBuffer
  data: ScatterDot[]
  setPointInterest: Dispatch<SetStateAction<ScatterDot | null>>
}

export const ProjectionPoints = ({
  buffer,
  data,
  setPointInterest,
}: ProjectionPointsProps) => {
  const [thumbnails, setThumbnails] = useState<Thumbnail[]>([])
  const refPoints = useRef<Points>(null!)
  const dpr = Math.min(window.devicePixelRatio, 2)
  const thumbnailSize = 10

  const imageLoader = new TextureLoader()
  const pointsMaterial = new ShaderMaterial({
    depthWrite: true,
    blending: NoBlending,
    vertexColors: true,
    fragmentShader: fragmentShader,
    vertexShader: vertexShader,
    uniforms: {uSize: {value: 500 * dpr}, uSizeAttenuation: {value: true}},
  })

  const handleOnPointClick = (e: ThreeEvent<MouseEvent>) => {
    if (e.ctrlKey) return
    const index = e.index
    if (index === undefined) return
    e.stopPropagation()

    const imageUrl = data[index].uri
    console.log(imageUrl)
    imageLoader.load(imageUrl, texture => {
      const material = new MeshBasicMaterial({map: texture, toneMapped: false})
      const {width, height} = texture.image
      const aspRatio = width / height
      const geometry = new PlaneGeometry(
        thumbnailSize * aspRatio,
        thumbnailSize,
      )
      setThumbnails([
        ...thumbnails,
        {
          data: data[index],
          material,
          geometry,
        },
      ])
    })
  }

  const handleOnThumbnailClick = (e: ThreeEvent<MouseEvent>) => {
    e.stopPropagation()
    const uiud = (e.object as Mesh).geometry.uuid
    setThumbnails(thumbnails.filter(thb => thb.geometry.uuid !== uiud))
  }

  useEffect(() => {
    setThumbnails([])
  }, [buffer, data])

  useFrame(() => {
    // TODO: not sure if it's the most efficient approach but putting
    // the buffer attributes as tags inside the points don't let me update
    // the colors
    if (refPoints.current && buffer) {
      refPoints.current.geometry.setAttribute('position', buffer.position)
      refPoints.current.geometry.setAttribute('fillColor', buffer.fillColor)
      refPoints.current.geometry.setAttribute('strokeColor', buffer.strokeColor)
      refPoints.current.geometry.attributes.position.needsUpdate = true
    }
  })

  return (
    <>
      <group position={[0, 0, 5]}>
        <points
          material={pointsMaterial}
          ref={refPoints}
          onClick={handleOnPointClick}
        ></points>
      </group>
      <group>
        {thumbnails &&
          thumbnails.map(thb => (
            <ProjectionImage
              key={thb.geometry.uuid}
              scatterdot={thb.data}
              material={thb.material}
              geometry={thb.geometry}
              pointMaterial={pointsMaterial}
              onClick={handleOnThumbnailClick}
              setPointInterest={setPointInterest}
            />
          ))}
      </group>
    </>
  )
}
