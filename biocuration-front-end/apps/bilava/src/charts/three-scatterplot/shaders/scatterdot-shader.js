export const fragmentShader = `
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

export const vertexShader = `
attribute vec3 fillColor;
attribute vec3 strokeColor;
uniform float uSize;
uniform bool uSizeAttenuation;

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
    if (uSizeAttenuation) {
        gl_PointSize *= (1.0 / -viewPosition.z);
    }

    vInsideColor = fillColor;
    vOutsideColor = strokeColor;
    vUV = uv;
    radius = map(uSize / 2., 0., uSize, 0., 1.);
    strokeWidth = radius;
}

`
