import {Float32BufferAttribute} from 'three'

export interface TreeData {
  taxonomy: string[]
  data: string[]
}

export interface Dimensions {
  width: number
  height: number
  marginRight: number
  marginLeft: number
  marginTop: number
  marginBottom: number
}

export interface ScatterDot {
  id: number // TODO database, shit i need the schema and classifier too...
  x: number // projected x coordinate
  y: number // projected y coordinate
  lbl: string // label
  prd: string // prediction
  uri: string // relative url to image
  hit: number // neighborhood hit
  ss: string // split set
}

export interface ProjectionBuffer {
  position: Float32BufferAttribute
  fillColor: Float32BufferAttribute
  strokeColor: Float32BufferAttribute
}
