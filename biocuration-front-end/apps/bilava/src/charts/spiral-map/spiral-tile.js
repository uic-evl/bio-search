import {scaleLinear} from 'd3-scale'

const getSizes = (k, x0, y0, x1, y1) => {
  const segmentWidth = (x1 - x0) / (k + 2)
  const segmentHeight = (segmentWidth * (y1 - y0)) / (x1 - x0)
  let kHorizontal = Math.floor((y1 - y0) / segmentHeight)
  if (kHorizontal % 2 !== 0) kHorizontal += 1
  return [segmentWidth, segmentHeight, kHorizontal]
}

export const spiralTile = (parent, x0, y0, x1, y1) => {
  const [EAST, SOUTH, WEST, NORTH] = [0, 1, 2, 3]

  let nodes = [...parent.children]
  let node = null

  // deeper levels will show only 4 images
  let k = !parent.depth ? nodes[0].data.k : 0
  let [segW, segH, kH] = !parent.depth
    ? getSizes(k, x0, y0, x1, y1)
    : [(x1 - x0) / 2, (y1 - y0) / 2, 2]
  let [innerX0, innerY0] = [segW, segH]
  let [innerX1, innerY1] = !parent.depth
    ? [innerX0 + k * segW, innerY0 + (kH - 2) * segH]
    : [segW, segH]

  let i = -1
  let maxDirection = {0: 1, 1: 1, 2: 1, 3: 1} // case for depth > 1
  if (!parent.depth) {
    nodes[0].x0 = innerX0
    nodes[0].y0 = innerY0
    nodes[0].x1 = innerX1
    nodes[0].y1 = innerY1
    i = 0 // we take the first image as a central one
    maxDirection = {0: k, 1: kH, 2: k, 3: kH}
  }

  let n = nodes.length
  let direction = EAST
  let segment = []

  while (++i < n) {
    node = nodes[i]
    segment.push(node)

    if (direction === EAST) {
      if (k > 0) {
        node.x0 = segment.length === 1 ? segW : segment[segment.length - 2].x1
        node.y1 = segH
      } else {
        node.x0 = (x1 - x0) / 2
        node.y1 = (y1 - y0) / 2
      }
      node.y0 = 0
      node.x1 = node.x0 + segW
    } else if (direction === SOUTH) {
      if (k > 0) {
        node.x0 = innerX1
        node.y0 = segment.length === 1 ? 0 : segment[segment.length - 2].y1
      } else {
        node.x0 = (x1 - x0) / 2
        node.y0 = (y1 - y0) / 2
      }
      node.x1 = node.x0 + segW
      node.y1 = node.y0 + segH
    } else if (direction === WEST) {
      if (k > 0) {
        node.x0 =
          segment.length === 1
            ? innerX1 - segW
            : segment[segment.length - 2].x0 - segW
        node.y0 = y1 - y0 - segH
        node.x1 = node.x0 + segW
      } else {
        node.x0 = 0
        node.y0 = (y1 - y0) / 2
        node.x1 = (x1 - x0) / 2
      }
      node.y1 = node.y0 + segH
    } else if (direction === NORTH) {
      if (k > 0) {
        node.x0 = 0
        node.y0 =
          segment.length === 1 ? innerY1 : segment[segment.length - 2].y0 - segH
        node.y1 = node.y0 + segH
      } else {
        node.x0 = 0
        node.y0 = 0
        node.y1 = segH
      }
      node.x1 = segW
    }

    if (segment.length === maxDirection[direction]) {
      direction = (direction + 1) % 4
      segment.length = 0

      if (direction === EAST && i < nodes.length - 1) {
        const newK = nodes[i + 1].data.k
        const [newSegW, newSegH, newkH] = getSizes(newK, x0, y0, x1, y1)
        segW = newSegW
        segH = newSegH
        kH = newkH
        maxDirection = {0: newK, 1: kH, 2: newK, 3: kH}

        innerX0 = segW
        innerY0 = segH
        innerX1 = innerX0 + newK * segW
        innerY1 = innerY0 + (kH - 2) * segH

        const scaleX = scaleLinear()
          .domain([0, x1 - x0])
          .range([segW, x1 - x0 - segW])
        const scaleY = scaleLinear()
          .domain([0, y1 - y0])
          .range([segH, y1 - y0 - segH])
        for (let j = 0; j <= i; j++) {
          nodes[j].x0 = scaleX(nodes[j].x0)
          nodes[j].y0 = scaleY(nodes[j].y0)
          nodes[j].x1 = scaleX(nodes[j].x1)
          nodes[j].y1 = scaleY(nodes[j].y1)
        }
      }
    }
  }
}

export const spiralStrategy = (strategy, idx) => {
  if (strategy === 'small2rings') {
    if (idx < 12) return 2
    else if (idx < 32) return 4
    else return 12
  } else if (strategy === 'medium3rings') {
    if (idx < 12) return 2
    else if (idx < 32) return 4
    else if (idx < 60) return 6
    else return 8
  } else if (strategy === 'large4rings') {
    if (idx < 12) return 2
    else if (idx < 32) return 4
    else if (idx < 60) return 6
    else if (idx < 97) return 8
    else if (idx < 150) return 20
    return 22
  } else if (strategy === 'xlarge4rings1smalls') {
    if (idx < 12) return 2
    else if (idx < 32) return 4
    else if (idx < 60) return 6
    else if (idx < 97) return 8
    else if (idx < 180) return 20
    return 34
  } else return 0
}

export const DEFAULT_STRATEGY = 'small2rings'
