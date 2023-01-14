import {Tooltip, Badge} from '@chakra-ui/react'

/* eslint-disable-next-line */
export interface ModalityCountBadgesProps {
  countMapper: {[id: string]: number}
  colorMapper: {[id: string]: string}
  namesMapper: {[id: string]: string}
}

export function ModalityCountBadges({
  countMapper,
  colorMapper,
  namesMapper,
}: ModalityCountBadgesProps) {
  return (
    <>
      {Object.keys(countMapper).map(key => {
        if (['gra', 'exp', 'mol', 'mic', 'rad'].includes(key)) return null

        return (
          <Tooltip
            label={`# ${namesMapper[key]} subfigures: ${countMapper[key]}`}
            key={`tooltip-${key}`}
          >
            <Badge key={key} mr={1} background={colorMapper[key]} color="black">
              {key}:{countMapper[key]}
            </Badge>
          </Tooltip>
        )
      })}
    </>
  )
}

export default ModalityCountBadges
