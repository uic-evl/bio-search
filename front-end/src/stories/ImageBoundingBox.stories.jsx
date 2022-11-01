import React from 'react'
import {Box} from '@chakra-ui/react'

import ImageBoundingBoxViewer from '../components/image/image_bbox_viewer'

export default {
  title: 'Image Bounding Box',
  component: ImageBoundingBoxViewer,
}

const params = {
  img_src: 'http://localhost:8080/4_1.jpg',
  // img_w: 466,
  // img_h: 600,
  bboxes: [
    {bbox: [347.5, 260.5, 117.0, 119.0], type: 1, color: 'red'},
    {bbox: [168.5, 1.0, 296.0, 243.5], type: 1, color: 'red'},
  ],
}

const params2 = {
  img_src: 'http://localhost:8080/7_1.jpg',
  // img_w: 466,
  // img_h: 600,
  bboxes: [
    {
      name: '001',
      bbox: [11, 11, 376, 113],
      type: 1,
      color: '#1f78b4',
    },
    {
      name: '004',
      bbox: [267, 123, 146, 102],
      type: 1,
      color: '#1f78b4',
    },
    {
      name: '006',
      bbox: [415, 133, 112, 91],
      type: 1,
      color: '#1f78b4',
    },
    {
      name: '005',
      bbox: [390, 13, 83, 104],
      type: 1,
      color: '#1f78b4',
    },
    {
      name: '002',
      bbox: [11, 127, 253, 93],
      type: 6,
      color: '#fdbf6f',
    },
  ],
}

export const Image = () => (
  <Box w={600} h={600} bg="tomato">
    <ImageBoundingBoxViewer {...params2} />
  </Box>
)
