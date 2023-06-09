import {Suspense, useEffect, useRef, useMemo} from 'react'
import {ScatterDot} from '../../types'
import {contourDensity} from 'd3-contour'
import {extent} from 'd3-array'
import {geoPath} from 'd3-geo'
import {color as d3_color} from 'd3-color'
import {ScaleLinear, scaleLinear} from 'd3-scale'
import {transformSVGPath} from './svg-to-path'
import {
  AddEquation,
  CustomBlending,
  MeshBasicMaterial,
  ShapeGeometry,
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

interface MeshProps {
  geometries: ShapeGeometry[]
  materials: MeshBasicMaterial[]
}

export const DensityContours = (props: DensityContoursProps) => {
  const meshProps = useMemo<MeshProps | undefined>(() => {
    const clfCategories = categories[props.classifier]
    const densityGenerator = contourDensity<ScatterDot>()
      .x(xAccessor)
      .y(yAccessor)
      // .size([props.width, props.height])
      .thresholds(30)
      .bandwidth(5)

    const densityPaths = []
    const scales: Record<string, ScaleLinear<string, string>> = {}
    const densityColors: string[] = []
    const densityNames: string[] = []
    const contourGeometries = []
    const contourMaterials: MeshBasicMaterial[] = []

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

      const maxColor = d3_color(colorsMapper[category])
      if (!maxColor) return
      const minColor = maxColor.brighter(1)
      scales[category] = scaleLinear<string>()
        .domain(domain)
        .range([minColor.formatRgb(), maxColor.formatRgb()])
    }

    console.log('build shapes')
    for (let i = 0; i < densityPaths.length; i++) {
      const densityElem = densityPaths[i]
      const path = geoPath()(densityElem)
      const shapeMaterial = new MeshBasicMaterial({
        color: scales[densityNames[i]](densityElem.value),
        depthTest: true,
        depthWrite: false,
        blending: CustomBlending,
        blendEquation: AddEquation,
        toneMapped: false,
        opacity: 0.7,
      })
      const transformedPath = transformSVGPath(path)
      const simpleShapes = transformedPath.toShapes(true)
      for (let simpleShape of simpleShapes) {
        contourGeometries.push(new ShapeGeometry(simpleShape))
        contourMaterials.push(shapeMaterial)
      }
    }

    return {
      geometries: contourGeometries,
      materials: contourMaterials,
    }
  }, [props.data, props.classifier, props.width, props.height])

  return (
    <>
      <group position={[0, 0, 1]}>
        {meshProps &&
          meshProps.geometries.map((geometry, idx) => (
            <mesh
              key={geometry.uuid}
              geometry={geometry}
              material={meshProps.materials[idx]}
            />
          ))}
      </group>
    </>
  )
}
