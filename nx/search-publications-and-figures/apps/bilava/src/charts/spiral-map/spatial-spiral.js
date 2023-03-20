const k = ring => 2 * ring

const quadrant = (x, y, cx, cy) => {
  if (x === cx && y === cy) return 'image'
  if (x > cx && y > cy) return 'q1'
  if (x > cx && y < cy) return 'q2'
  if (x < cx && y > cy) return 'q4'
  if (x < cx && y < cy) return 'q3'
}

const extractCandidates = (arr, total, ring, quadrant) => {
  const candidates = []
  for (let i = 0; i < total; i++) {
    if (arr.length > 0) {
      const el = arr.shift()
      candidates.push({...el, k: k(ring)})
    } else
      candidates.push({
        x: 0,
        y: 0,
        quadrant: quadrant,
        placeholder: true,
        name: `ec-${quadrant}-${i}`,
        k: k(ring),
      })
  }
  return candidates
}

const createChildren = (arr, quadrant, qPoints) => {
  // modifies the array by reference
  if (qPoints.length > 0) {
    for (let i = arr.length - 1; i > 0; i--) {
      if (arr[i].quadrant === quadrant) {
        const currPoint = {...arr[i]}
        let restPoints = extractCandidates(qPoints, 3, 1, quadrant) // k not relevant here
        restPoints = [{...currPoint}].concat(restPoints)
        let children = restPoints.map(p => ({...p, k: currPoint.k}))
        // transform node to have children
        arr[i] = {
          name: `cc-${quadrant}-${i}`,
          x: 0,
          y: 0,
          quadrant,
          k: children[0].k,
          children,
          placeholder: true,
        }
      }

      if (qPoints.length === 0) break
    }
  }
}

const createRing = (ringNumber, q1, q2, q3, q4) => {
  const totalElementInRing = k(ringNumber) * 4 + 4
  const totalPerQuadrant = totalElementInRing / 4
  const candidatesQ1 = extractCandidates(q1, totalPerQuadrant, ringNumber, 'q1')
  const candidatesQ2 = extractCandidates(q2, totalPerQuadrant, ringNumber, 'q2')
  const candidatesQ3 = extractCandidates(q3, totalPerQuadrant, ringNumber, 'q3')
  const candidatesQ4 = extractCandidates(q4, totalPerQuadrant, ringNumber, 'q4')
  const q4Start = candidatesQ4.slice(0, (totalPerQuadrant - 1) / 2)
  const q4End = candidatesQ4.slice((totalPerQuadrant - 1) / 2)

  return q4Start.concat(candidatesQ1, candidatesQ2, candidatesQ3, q4End)
}

export const convert2SpatiallyAwareArray = (startPoints, maxRings) => {
  const centralPoint = startPoints[0]
  const points = startPoints.map((p, i) => ({
    ...p,
    quadrant: quadrant(p.x, p.y, centralPoint.x, centralPoint.y),
  }))
  let q1 = points.filter(p => p.quadrant === 'q1')
  let q2 = points.filter(p => p.quadrant === 'q2')
  let q3 = points.filter(p => p.quadrant === 'q3')
  let q4 = points.filter(p => p.quadrant === 'q4')

  let points4Ring = []
  for (let i = 0; i < maxRings; i++)
    points4Ring = points4Ring.concat(createRing(i + 1, q1, q2, q3, q4))

  if (q1.length > 0 || q2.length > 0 || q3.length > 0 || q4.length > 0) {
    createChildren(points4Ring, 'q1', q1)
    createChildren(points4Ring, 'q2', q2)
    createChildren(points4Ring, 'q3', q3)
    createChildren(points4Ring, 'q4', q4)
  }

  return [points[0]].concat(points4Ring)
}
