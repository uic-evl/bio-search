import {Dispatch, SetStateAction, useState} from 'react'
import {Box, Spacer, Spinner} from '@chakra-ui/react'
import {
  ActionButton,
  HeaderSelect,
  HeaderTitle,
  PanelHeader,
} from '../panel-header/panel-header'
import {useClassifiers} from './use-classifiers'

/* eslint-disable-next-line */
export interface ProjectionPanelProps {
  project: string
}

export function ProjectionPanel(props: ProjectionPanelProps) {
  const [classifier, setClassifier] = useState<string>('')
  const [projection, setProjection] = useState<string>('tsne')
  const [partition, setPartition] = useState<string>('TRAIN')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const classifiers = useClassifiers(props.project)

  const handleOnLoadData = async () => {}

  return (
    <Box w="full" h="full">
      <ProjectionPanelHeader
        classifiers={classifiers}
        selectedClassifier={classifier}
        setClassifier={setClassifier}
        selectedProjection={projection}
        setProjection={setProjection}
        selectedPartition={partition}
        setPartition={setPartition}
        isLoading={isLoading}
        onClick={handleOnLoadData}
      />
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
  onClick: () => Promise<void>
}

const ProjectionPanelHeader = (props: ProjectionPanelHeaderProps) => {
  const projections = ['pca', 'tsne', 'umap']
  const partitions = ['TRAIN', 'VAL', 'TEST', 'UNL']

  return (
    <PanelHeader>
      <HeaderTitle>Projections</HeaderTitle>
      {props.classifiers.length > 0 ? (
        <HeaderSelect
          placeholder="classifier"
          value={props.selectedClassifier}
          options={props.classifiers}
          onChangeFn={props.setClassifier}
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
            !props.selectedClassifier ||
            !props.selectedProjection ||
            !props.selectedPartition ||
            props.isLoading
          }
          onClick={props.onClick}
          isLoading={props.isLoading}
        >
          Load
        </ActionButton>
      </Box>
    </PanelHeader>
  )
}

export default ProjectionPanel
