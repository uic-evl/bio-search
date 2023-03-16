import {useRef} from 'react'
import {NoBlending, Points, ShaderMaterial} from 'three'
import {useFrame} from '@react-three/fiber'
import {ProjectionBuffer} from '../../types'

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

interface ProjectionPointsProps {
  data: ProjectionBuffer
}

export const ProjectionPoints = ({data}: ProjectionPointsProps) => {
  const refPoints = useRef<Points>(null!)
  const dpr = Math.min(window.devicePixelRatio, 2)

  const pointsMaterial = new ShaderMaterial({
    depthWrite: true,
    blending: NoBlending,
    vertexColors: true,
    fragmentShader: fragmentShader,
    vertexShader: vertexShader,
    uniforms: {uSize: {value: 10 * dpr}},
  })

  useFrame(() => {
    // TODO: not sure if it's the most efficient approach but putting
    // the buffer attributes as tags inside the points don't let me update
    // the colors
    if (refPoints.current && data) {
      refPoints.current.geometry.setAttribute('position', data.position)
      refPoints.current.geometry.setAttribute('fillColor', data.fillColor)
      refPoints.current.geometry.setAttribute('strokeColor', data.strokeColor)
      refPoints.current.geometry.attributes.position.needsUpdate = true
    }
  })

  return (
    <>
      <points material={pointsMaterial} ref={refPoints}>
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
    </>
  )
}
