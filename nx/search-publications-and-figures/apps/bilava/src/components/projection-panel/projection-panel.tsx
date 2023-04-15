import {Dispatch, SetStateAction, useState} from 'react'
import {Box, Spacer, Spinner} from '@chakra-ui/react'
import {
  ActionButton,
  HeaderSelect,
  HeaderTitle,
  PanelHeader,
} from '../panel-header/panel-header'
import {useClassifiers} from './use-classifiers'
import ThreeScatterplot from '../../charts/three-scatterplot/three-scatterplot'
import {Dataset, Filter, ScatterDot} from '../../types'
import {fetch_projections} from '../../api'
import {min} from 'd3-array'
import useDimensions from 'react-cool-dimensions'
import {ResizeObserver} from '@juggle/resize-observer'
import {Point} from '../../utils/convex-hull'

export interface ProjectionPanelProps {
  project: string
  data: ScatterDot[]
  setDataset: Dispatch<SetStateAction<Dataset>>
  setPointInterest: Dispatch<SetStateAction<ScatterDot | null>>
  neighborhoodHull: Point[]
  setBrushedData: Dispatch<SetStateAction<ScatterDot[]>>
  filters: Filter
}

const xAccessor = (d: ScatterDot) => d.x
const yAccessor = (d: ScatterDot) => d.y

const translateData = (data: ScatterDot[]) => {
  /* Translate data to avoid negative positions, required by d3.density */
  const padding = 20
  const minX = Math.abs(min(data, xAccessor) || 0) + padding
  const minY = Math.abs(min(data, yAccessor) || 0) + padding
  return data.map(el => ({...el, x: el.x + minX, y: el.y + minY}))
}

export function ProjectionPanel(props: ProjectionPanelProps) {
  const [classifier, setClassifier] = useState<string>('')
  const [projection, setProjection] = useState<string>('tsne')
  const [splitSet, setSplitSet] = useState<string>('TRAIN')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const classifiers = useClassifiers(props.project)
  const {observe, height} = useDimensions({
    useBorderBoxSize: true,
    polyfill: ResizeObserver,
    onResize: ({unobserve, height}) => {
      // without observing, the canvas is expanding its height out of control
      // and we only need the container height. TODO: fix for resizing
      if (height > 0) {
        unobserve()
      }
    },
  })

  const handleOnLoadData = async (searchBoxClassifier: string) => {
    setIsLoading(true)
    const dataset = await fetch_projections(
      searchBoxClassifier,
      projection,
      splitSet,
    )
    setIsLoading(false)
    setClassifier(searchBoxClassifier)
    props.setDataset({
      data: translateData(dataset.data),
      labels: dataset.labels,
      sources: dataset.sources,
      minPrediction: dataset.minPrediction,
    })
  }

  return (
    <Box w="full" h="full">
      <ProjectionPanelHeader
        classifiers={classifiers}
        selectedClassifier={classifier}
        setClassifier={setClassifier}
        selectedProjection={projection}
        setProjection={setProjection}
        selectedPartition={splitSet}
        setPartition={setSplitSet}
        isLoading={isLoading}
        onClick={handleOnLoadData}
      />
      <Box w="full" h="95%" ref={observe}>
        {props.data.length > 0 && height > 0 ? (
          <ThreeScatterplot
            classifier={classifier}
            data={props.data}
            cameraLeft={0}
            cameraBottom={0}
            height={height}
            setPointInterest={props.setPointInterest}
            neighborhoodHull={props.neighborhoodHull}
            setBrushedData={props.setBrushedData}
            filters={props.filters}
          />
        ) : null}
      </Box>
    </Box>
  )
}

interface ProjectionPanelHeaderProps {
  classifiers: string[]
  selectedClassifier: string
  setClassifier: Dispatch<SetStateAction<string>>
  selectedProjection: string
  setProjection: Dispatch<SetStateAction<string>>
  selectedPartition: string
  setPartition: Dispatch<SetStateAction<string>>
  isLoading: boolean
  onClick: (arg: string) => Promise<void>
}

const ProjectionPanelHeader = (props: ProjectionPanelHeaderProps) => {
  const [classifier, setClassifier] = useState<string>('')
  const projections = ['pca', 'tsne', 'umap']
  const partitions = ['TRAIN', 'TRAIN+UNL', 'VAL', 'TEST', 'UNL']

  const handleOnClick = () => props.onClick(classifier)

  return (
    <Box>
      <PanelHeader>
        <HeaderTitle>Projections</HeaderTitle>
        {props.classifiers.length > 0 ? (
          <HeaderSelect
            placeholder="classifier"
            value={classifier}
            options={props.classifiers}
            onChangeFn={setClassifier}
          />
        ) : (
          <Spinner />
        )}
        <HeaderSelect
          placeholder="projection"
          value={props.selectedProjection}
          options={projections}
          onChangeFn={props.setProjection}
        />
        <HeaderSelect
          placeholder="partition"
          value={props.selectedPartition}
          options={partitions}
          onChangeFn={props.setPartition}
        />
        <Spacer />
        <Box>
          <ActionButton
            disabled={
              !classifier ||
              !props.selectedProjection ||
              !props.selectedPartition ||
              props.isLoading
            }
            onClick={handleOnClick}
            isLoading={props.isLoading}
          >
            Load
          </ActionButton>
        </Box>
      </PanelHeader>
    </Box>
  )
}

export default ProjectionPanel
