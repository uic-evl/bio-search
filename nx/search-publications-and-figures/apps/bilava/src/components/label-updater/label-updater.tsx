import {Dispatch, SetStateAction, useEffect, useState} from 'react'
import {ScatterDot, UpdateResult} from '../../types'
import {
  AlertStatus,
  Box,
  Button,
  Flex,
  Radio,
  RadioGroup,
  Select,
  Stack,
  UseToastOptions,
  chakra,
  useToast,
} from '@chakra-ui/react'
import {SimpleBoxHeader, Subtitle} from '../panel-header/panel-header'
import {colorsMapper, findChildren, findSiblings} from '../../utils/mapper'
import {batch_update} from '../../api'

const errorMessage = (description: string) => ({
  title: 'Error',
  description,
  status: 'error' as AlertStatus,
  isClosable: true,
  duration: 3000,
})

const successMessage = (result: UpdateResult) => ({
  title: 'Success',
  description: `${result.total_updates} images updated`,
  type: 'success' as AlertStatus,
  isClosable: true,
  duration: 3000,
})

const EmptySelector = () => (
  <Box>
    <Box w="full">
      <SimpleBoxHeader title="update labels" />
      <Box pl={2} pr={2} fontStyle="italic">
        Please select images from the Gallery or Neighborhood views
      </Box>
    </Box>
  </Box>
)

/* eslint-disable-next-line */
export interface LabelUpdaterProps {
  neighbors: ScatterDot[]
  galleryItems: ScatterDot[]
}

export const LabelUpdater = ({neighbors, galleryItems}: LabelUpdaterProps) => {
  const [label, setLabel] = useState<string | undefined>(undefined)
  const [selectionGroup, setSelectionGroup] = useState<string | undefined>(
    undefined,
  )
  const [targetLabel, setTargetLabel] = useState<string | null>(null)
  const [action, setAction] = useState<string>('update')
  const toast = useToast()

  useEffect(() => {
    // Control what options are available to update based on selected elements
    let selection = undefined
    if (neighbors.length > 0 && galleryItems.length === 0) {
      selection = 'neighborhood'
    } else if (neighbors.length === 0 && galleryItems.length > 0) {
      selection = 'gallery'
    } else if (neighbors.length === 0 && galleryItems.length === 0) {
      selection = undefined
    }
    if (selection !== selectionGroup) {
      setSelectionGroup(selection)
    }
  }, [neighbors, galleryItems])

  useEffect(() => {
    if (neighbors.length === 0 && galleryItems.length === 0) {
      setSelectionGroup(undefined)
      return
    }

    const collection =
      selectionGroup === 'neighborhood' ? neighbors : galleryItems
    const label =
      collection[0].lbl === 'unl' ? collection[0].prd : collection[0].lbl

    setTargetLabel(label)
    setLabel(label)
  }, [selectionGroup])

  const labelOpts = siblings2options(label, colorsMapper)

  const handleOnSave = async () => {
    const collection =
      selectionGroup === 'neighborhood' ? neighbors : galleryItems
    const ids = collection.map(el => el.dbId)

    let newLabel = 'error' // label for delete cases
    if (action === 'update') {
      if (targetLabel === null) {
        toast(errorMessage('input a value to update'))
        return
      }
      newLabel = targetLabel
    }

    const response = await batch_update(ids, newLabel)
    if ('error' in response) {
      toast(errorMessage(response.description))
    } else {
      toast(successMessage(response))
    }
  }

  if (neighbors.length === 0 && galleryItems.length === 0) {
    return <EmptySelector />
  }

  return (
    <Box>
      <Box w="full">
        <SimpleBoxHeader title="update labels" />
      </Box>
      <Box pl={2} pr={2}>
        <Subtitle text={'selection'} />
        <RadioGroup
          onChange={setSelectionGroup}
          value={selectionGroup}
          mb={2}
          isDisabled={selectionGroup === undefined}
        >
          <Stack direction="row">
            <Radio
              size="sm"
              value="gallery"
              isDisabled={galleryItems.length === 0}
            >
              Gallery
            </Radio>
            <Radio
              size="sm"
              value="neighborhood"
              isDisabled={neighbors.length === 0}
            >
              Neighborhood
            </Radio>
          </Stack>
        </RadioGroup>

        <Box mt="4">
          <Flex direction="row" alignItems="center" textAlign="center">
            <Select
              size="xs"
              variant="filled"
              w="90px"
              bg={action === 'update' ? 'green.200' : 'tomato'}
              value={action}
              onChange={e => setAction(e.target.value)}
            >
              <option value="update">Update</option>
              <option value="delete">Delete</option>
            </Select>

            <Box>
              {selectionGroup && (
                <chakra.span ml={2}>
                  {selectionGroup === 'gallery'
                    ? galleryItems && galleryItems.length
                      ? galleryItems.length
                      : 0
                    : neighbors && neighbors.length
                    ? neighbors.length
                    : 0}{' '}
                  images
                </chakra.span>
              )}
            </Box>
          </Flex>
        </Box>

        {label && action == 'update' ? (
          <Box mt="4">
            <Subtitle text={'label'} />
            <HierarchicalSelect
              opts={labelOpts}
              label={label}
              mapping={colorsMapper}
              level={0}
              setTargetLabel={setTargetLabel}
            />
            <chakra.span>{targetLabel}</chakra.span>
          </Box>
        ) : null}

        <Button
          w="full"
          size="sm"
          mt={2}
          onClick={handleOnSave}
          isDisabled={neighbors.length === 0 && galleryItems.length === 0}
        >
          Save
        </Button>
      </Box>
    </Box>
  )
}

const getBranchKeys = (label: string) => {
  // Get all the labels in the branch down to the input label
  return label.split('.').map((el, i, arr) => arr.slice(0, i + 1).join('.'))
}

const siblings2options = (
  label: string | undefined,
  mapping: Record<string, string>,
) => {
  if (label === undefined) return []
  const branchLabels = getBranchKeys(label)

  const siblings = findSiblings(mapping, branchLabels[0])

  let labels = null
  console.log(branchLabels)
  if (branchLabels[0] !== 'unl') labels = [branchLabels[0], ...siblings]
  else labels = [...siblings]
  labels.sort()
  return labels2options(labels)
}

const getSelectLabel = (label: string, level: number) => {
  const arr = label.split('.').slice(0, level + 1)
  if (level > arr.length) return undefined
  else return arr.join('.')
}

const labels2options = (labels: string[]) =>
  labels.map(val => ({
    value: val,
    label: val.split('.').at(-1),
  }))

const children2opts = (mapping: Record<string, string>, label: string) => {
  const children = label ? findChildren(mapping, label) : null
  if (children) children.sort()
  return children ? labels2options(children) : null
}

const display = (lbl: string | undefined) => {
  if (!lbl) return 'undefined'
  const split = lbl.split('.')
  return split.length === 1 ? split : split.at(-1)
}

interface HierarchicalSelectProps {
  opts: {label: string | undefined; value: string}[]
  label: string // label to set at a level in the hierarchy
  mapping: Record<string, string>
  level: number
  setTargetLabel: Dispatch<SetStateAction<string | null>>
}

// Hierarchical component of nested Selects
const HierarchicalSelect = ({
  opts,
  label,
  mapping,
  level,
  setTargetLabel,
}: HierarchicalSelectProps) => {
  const [value, setValue] = useState(getSelectLabel(label, level))
  const [childrenOpts, setChildrenOpts] = useState<
    {label: string | undefined; value: string}[] | null
  >(null)

  useEffect(() => {
    if (!value) return

    const newValue = getSelectLabel(value, level)
    // make sure grandchildren disappear if grandparent changes
    if (newValue !== undefined) {
      const newChildrenOpts = children2opts(mapping, newValue)
      setChildrenOpts(newChildrenOpts)
    }
  }, [value])

  return (
    <>
      <Select
        size="sm"
        variant="flushed"
        value={value}
        onChange={val => {
          setValue(val.target.value)
          setTargetLabel(val.target.value)
        }}
        placeholder="select"
      >
        {opts.map(el => (
          <option key={`${label}-${el.value}`} value={el.value}>
            {`${el.label} (${display(el.value)})`}
          </option>
        ))}
      </Select>
      {value && childrenOpts && childrenOpts.length > 0 && (
        <HierarchicalSelect
          opts={childrenOpts}
          label={label && label.includes(value) ? label : value}
          mapping={mapping}
          level={level + 1}
          setTargetLabel={setTargetLabel}
        />
      )}
    </>
  )
}
