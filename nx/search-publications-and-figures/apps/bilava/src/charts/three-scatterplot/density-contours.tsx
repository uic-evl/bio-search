import {Suspense, useEffect, useRef} from 'react'
import {ScatterDot} from '../../types'
import {contourDensity} from 'd3-contour'
import {extent} from 'd3-array'
import {geoPath} from 'd3-geo'
import {color as d3_color} from 'd3-color'
import {ScaleLinear, scaleLinear} from 'd3-scale'
import {transformSVGPath} from './svg-to-path'
import {
  CustomBlending,
  ExtrudeGeometry,
  Group,
  MeshBasicMaterial,
  MinEquation,
  Mesh,
  ReverseSubtractEquation,
  BufferGeometry,
  Line,
} from 'three'
import {colorsMapper} from '../../utils/mapper'

interface DensityContoursProps {
  classifier: string
  data: ScatterDot[]
  width: number
  height: number
}

const xAccessor = (d: ScatterDot) => d.x
const yAccessor = (d: ScatterDot) => d.y
const labelAccessor = (d: ScatterDot) => d.lbl

const categories: Record<string, string[]> = {
  'higher-modality': ['exp', 'mic', 'gra', 'mol', 'pho', 'oth'],
  microscopy: ['mic.ele', 'mic.flu', 'mic.lig'],
  experimental: ['exp.gel', 'exp.pla'],
  radiology: ['rad.xra', 'rad.cmp', 'rad.ang', 'rad.uls', 'rad.oth'],
  graphics: [
    'gra.lin',
    'gra.oth',
    'gra.sca',
    'gra.his',
    'gra.flow',
    'gra.3dr',
    'gra.sig',
  ],
  molecular: ['mol.pro', 'mol.dna', 'mol.che', 'mol.3ds'],
  photography: ['pho.der', 'pho.org'],
  gel: ['exp.gel.nor', 'exp.gel.wes', 'exp.gel.rpc'],
  electron: ['mic.ele.sca', 'mic.ele.tra'],
}

export const DensityContours = (props: DensityContoursProps) => {
  const refGroup = useRef<Group>(null!)
  const clfCategories = categories[props.classifier]
  const densityGenerator = contourDensity<ScatterDot>()
    .x(xAccessor)
    .y(yAccessor)
    .size([props.width, props.height])
    .thresholds(15)
    .bandwidth(4)

  useEffect(() => {
    const densityPaths = []
    const scales: Record<string, ScaleLinear<string, string>> = {}
    const densityColors: string[] = []
    const densityNames: string[] = []

    for (const category of clfCategories) {
      const filteredPoints = props.data.filter(
        d => labelAccessor(d) === category,
      )
      const densities = densityGenerator(filteredPoints)
      for (const density of densities) {
        densityColors.push(colorsMapper[category])
        densityNames.push(category)
        if (density.coordinates.length > 0) densityPaths.push(density)
      }
      const domain = extent(densityPaths, d => d.value)
      if (domain[0] === undefined || domain[1] === undefined) return
      // console.log(d3_color(colorsMapper[category])?.formatHex())
      // console.log(setOpacity(colorsMapper[category], 0.5))

      // const maxColor = d3_color(colorsMapper[category])
      // const minColor = maxColor?.copy({opacity: 0.1})
      // console.log(minColor, maxColor)

      scales[category] = scaleLinear<string>()
        .domain(domain)
        .range(['0xffffff', colorsMapper[category]])
      console.log(scales[category].domain(), scales[category].range())
    }

    for (let i = 0; i < densityPaths.length; i++) {
      const densityElem = densityPaths[i]
      const path = geoPath()(densityElem)
      console.log(densityElem.value)
      const shapeMaterial = new MeshBasicMaterial({
        color: scales[densityNames[i]](densityElem.value),
        wireframe: false,
        depthTest: true,
        blending: CustomBlending,
        blendEquation: MinEquation,
      })
      const transformedPath = transformSVGPath(path)
      const simpleShapes = transformedPath.toShapes(true)
      for (let simpleShape of simpleShapes) {
        const shape3d = new ExtrudeGeometry(simpleShape, {
          depth: 1,
          bevelEnabled: false,
        })
        // let shape3d = new BufferGeometry().setFromPoints(
        //   simpleShape.getPoints(),
        // )
        // const lineM = new Line(shape3d, shapeMaterial)
        const densityMesh = new Mesh(shape3d, shapeMaterial)
        refGroup.current.add(densityMesh)
      }
    }
  }, [props.data, props.width, props.height])

  return <group ref={refGroup} position={[0, 0, 1]}></group>
}
