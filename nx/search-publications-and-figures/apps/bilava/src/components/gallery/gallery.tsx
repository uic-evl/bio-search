import {Dispatch, SetStateAction, useEffect, useMemo, useState} from 'react'
import {Box, Grid, GridItem} from '@chakra-ui/react'
import {GalleryHeader} from './panel-header'
import {ScatterDot} from '../../types'
import {useChartDimensions} from '../../charts/use-chart-dimensions/use-chart-dimensions'
import HtmlImageThumbnail, {
  ScaledImage,
} from '../html-image-thumbnail/html-image-thumbnail'
import {LabelCircleIcon} from '../icons/icons'
import {colorsMapper} from '../../utils/mapper'

import styles from './gallery.module.css'

const mispredicted = (images: ScatterDot[]) =>
  images ? images.filter(d => d.lbl !== 'unl' && d.lbl !== d.prd) : []

const confident = (images: ScatterDot[]) => {
  const unlabeled = images.filter(d => d.lbl === 'unl')
  unlabeled.sort((a, b) => b.ms - a.ms)
  return unlabeled
}

const uncertain = (images: ScatterDot[]) => {
  const unlabeled = images.filter(d => d.lbl === 'unl')
  unlabeled.sort((a, b) => a.ms - b.ms)
  return unlabeled
}

/* eslint-disable-next-line */
export interface GalleryProps {
  data: ScatterDot[] | null
  size: number
  brushedData: ScatterDot[] | null
  setGalleryCandidates: Dispatch<SetStateAction<ScatterDot[]>>
  setPointInterest: Dispatch<SetStateAction<ScatterDot | null>>
}

export function Gallery(props: GalleryProps) {
  const [selectedIdx, setSelectedIdx] = useState<boolean[]>([])
  const [tabIndex, setTabIndex] = useState<number>(0)
  const [currPage, setCurrPage] = useState<number>(0)
  const [gridRef, dimensions] = useChartDimensions({
    marginLeft: 5,
    marginRight: 5,
    marginTop: 0,
    marginBottom: 0,
  })
  const gap = 5

  const handleSelectAll = () => {
    let indexes = [...selectedIdx]
    indexes = indexes.map(e => true)
    setSelectedIdx(indexes)
  }
  const handleDeselectAll = () => {
    let indexes = [...selectedIdx]
    indexes = indexes.map(e => false)
    setSelectedIdx(indexes)
  }

  const [numberPages, itemsPerPage] = useMemo<[number, number]>(() => {
    if (!props.data) return [0, 0]

    const squaredImgSize = props.size + gap
    const elemsWidth = Math.floor(dimensions.boundedWidth / squaredImgSize)
    const elemsHeight = Math.floor(dimensions.boundedHeight / squaredImgSize)
    const elemsPerPage = elemsWidth * elemsHeight
    const numberPages = Math.ceil(props.data.length / elemsPerPage)

    return [numberPages, elemsPerPage]
  }, [props.data, dimensions])

  const contextImages = useMemo<ScatterDot[]>(() => {
    if (!props.data) return []
    if (tabIndex === 0) return mispredicted(props.data)
    if (tabIndex === 1) return props.brushedData ? props.brushedData : []
    if (tabIndex === 2) return confident(props.data)
    return uncertain(props.data)
  }, [props.data, props.brushedData, tabIndex])

  useEffect(() => {
    setCurrPage(0)
    props.setGalleryCandidates([])
    setSelectedIdx(Array.from({length: contextImages.length}, () => false))
  }, [contextImages])

  const imagesOnPage = useMemo<ScatterDot[]>(() => {
    const numImages = contextImages.length
    if (numImages === 0) return []

    const start = itemsPerPage * currPage
    const end =
      start + itemsPerPage > numImages
        ? start + numImages - start
        : start + itemsPerPage
    return contextImages.slice(start, end)
  }, [currPage, contextImages])

  return (
    <Box w="full" h="full">
      <GalleryHeader
        numberImages={contextImages.length}
        currPage={currPage}
        setCurrPage={setCurrPage}
        setTabIndex={setTabIndex}
        onSelectAll={handleSelectAll}
        onDeselectAll={handleDeselectAll}
        numberPages={Math.ceil(contextImages.length / itemsPerPage)}
      />
      <Grid
        ref={gridRef}
        w="100%"
        h="90%"
        gridTemplateColumns={`repeat(auto-fill, minmax(${props.size}px, 1fr))`}
        gap={`${gap}px`}
        mt={dimensions.marginTop}
        pl={dimensions.marginRight}
        pr={dimensions.marginRight}
        pt={1}
        bg="blackAlpha.900"
      >
        {imagesOnPage &&
          imagesOnPage.map((d, idx) => (
            <GridItem key={d.dbId} w={`${props.size}px`} h={`${props.size}px`}>
              <Box
                w="full"
                h="full"
                position={'relative'}
                border={
                  selectedIdx[currPage * itemsPerPage + idx]
                    ? '1px solid red'
                    : ''
                }
              >
                <img
                  src={d.uri}
                  style={{
                    width: `${props.size - 4}px`,
                    height: `${props.size - 4}px`,
                    maxWidth: `${props.size - 4}px`,
                    maxHeight: `${props.size - 4}px`,
                  }}
                  className={styles['item-image']}
                  alt=""
                  onClick={() => {
                    const indexes = [...selectedIdx]
                    const wrapIdx = currPage * itemsPerPage + idx
                    indexes[wrapIdx] = !indexes[wrapIdx]
                    setSelectedIdx(indexes)
                    props.setGalleryCandidates(
                      contextImages.filter((el, idx) => indexes[idx]),
                    )
                  }}
                />
                <LabelCircleIcon
                  fill={colorsMapper[d.lbl]}
                  stroke={colorsMapper[d.prd]}
                  size={{width: 14, height: 14}}
                  onClick={() => {
                    props.setPointInterest(d)
                  }}
                />
              </Box>
            </GridItem>
          ))}
        {imagesOnPage && imagesOnPage.length === 0 && (
          <Box color="white">No data to display</Box>
        )}
      </Grid>
    </Box>
  )
}
