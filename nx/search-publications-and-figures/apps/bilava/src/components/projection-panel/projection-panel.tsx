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
import {ScatterDot} from '../../types'
import {fetch_projections} from '../../api'
import {min} from 'd3-array'

// const data: ScatterDot[] = [
//   {x: 10, y: 10, lbl: 'exp.gel', prd: 'exp.gel'},
//   {x: 20, y: 20, lbl: 'exp.pla', prd: 'exp.pla'},
// ]

export interface ProjectionPanelProps {
  project: string
}

const xAccessor = (d: ScatterDot) => d.x
const yAccessor = (d: ScatterDot) => d.y

const translateData = (data: ScatterDot[]) => {
  /* Translate data to avoid negative positions, required by d3.density */
  const padding = 20
  const minX = Math.abs(min(data, xAccessor) || 0) + padding
  const minY = Math.abs(min(data, yAccessor) || 0) + padding
  console.log(minX, minY)
  return data.map(el => ({...el, x: el.x + minX, y: el.y + minY}))
}

export function ProjectionPanel(props: ProjectionPanelProps) {
  const [data, setData] = useState<ScatterDot[] | null>(null)
  const [classifier, setClassifier] = useState<string>('')
  const [projection, setProjection] = useState<string>('tsne')
  const [splitSet, setSplitSet] = useState<string>('TRAIN')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const classifiers = useClassifiers(props.project)

  const handleOnLoadData = async (searchBoxClassifier: string) => {
    const projections = await fetch_projections(
      searchBoxClassifier,
      projection,
      splitSet,
    )
    setClassifier(searchBoxClassifier)
    setData(translateData(projections))
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
      <Box w="full" h="full">
        {data ? (
          <ThreeScatterplot
            classifier={classifier}
            data={data}
            cameraLeft={0}
            cameraBottom={0}
            width={800}
            height={800}
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
  const partitions = ['TRAIN', 'VAL', 'TEST', 'UNL']

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
