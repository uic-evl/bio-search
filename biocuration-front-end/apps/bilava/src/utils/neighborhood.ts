import {ScatterDot} from '../types'

export const findNClosestNeighbors = (
  data: ScatterDot[] | null,
  point: ScatterDot,
  n: number,
) => {
  if (!data) return []

  const points = data.map(d => ({
    ...d,
    distance: Math.pow(d.x - point.x, 2) + Math.pow(d.y - point.y, 2),
    selected: false,
  }))
  points.sort((a, b) => a.distance - b.distance)
  const output = Math.min(points.length - 1, n)
  return points.slice(1, output + 1)
}
