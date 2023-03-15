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
  x: number
  y: number
  lbl: string
  pred: string
}
