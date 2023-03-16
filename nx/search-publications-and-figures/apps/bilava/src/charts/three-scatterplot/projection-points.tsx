import {useState, useEffect, useRef} from 'react'
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

interface Thumbnail {
  data: ScatterDot
  material: MeshBasicMaterial
  geometry: PlaneGeometry
}

interface ProjectionPointsProps {
  buffer: ProjectionBuffer
  data: ScatterDot[]
}

export const ProjectionPoints = ({buffer, data}: ProjectionPointsProps) => {
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
    uniforms: {uSize: {value: 10 * dpr}},
  })

  const handleOnPointClick = (e: ThreeEvent<MouseEvent>) => {
    if (e.ctrlKey) return
    const index = e.index
    if (index === undefined) return
    e.stopPropagation()

    const imageUrl = data[index].uri
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
        >
          {/* preferring the useFrame approach over this one
        <bufferGeometry>
          <bufferAttribute attach="attributes-position" {...data.position} />
          <bufferAttribute attach="attributes-fillColor" {...data.fillColor} />
          <bufferAttribute
            attach="attributes-strokeColor"
            {...data.strokeColor}
          />
        </bufferGeometry> */}
        </points>
      </group>
      <group>
        {thumbnails &&
          thumbnails.map(thb => (
            <mesh
              key={thb.geometry.uuid}
              geometry={thb.geometry}
              material={thb.material}
              position={[thb.data.x, thb.data.y, 10]}
              onClick={handleOnThumbnailClick}
            />
          ))}
      </group>
    </>
  )
}

/* */
