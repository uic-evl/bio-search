import {useRef, useEffect, useState, useLayoutEffect} from 'react'
import {Box} from '@chakra-ui/react'

const ImageBoundingBoxViewer = ({img_src, bboxes}) => {
  const containerRef = useRef(null)
  const canvasRef = useRef(null)

  const [height, setHeight] = useState(0)
  const [width, setWidth] = useState(0)

  useLayoutEffect(() => {
    // get size based on parent's size
    const containerDiv = containerRef.current.parentElement
    setHeight(containerDiv.offsetHeight)
    setWidth(containerDiv.offsetWidth)
  }, [bboxes, img_src])

  useEffect(() => {
    if (height > 0 && width > 0) {
      const canvas = canvasRef.current
      const ctx = canvas.getContext('2d')
      const image = new Image()
      image.src = img_src
      image.onload = () => {
        const scale = Math.min(
          canvas.width / image.width,
          canvas.height / image.height,
        )
        const x = canvas.width / 2 - (image.width / 2) * scale
        const y = canvas.height / 2 - (image.height / 2) * scale

        ctx.save()
        ctx.fillStyle = 'black'
        ctx.fillRect(0, 0, canvas.width, canvas.height)
        ctx.drawImage(image, x, y, image.width * scale, image.height * scale)
        ctx.restore()

        // draw bounding boxes
        bboxes.forEach(el => {
          if (el.bbox) {
            ctx.save()
            ctx.strokeStyle = el.color
            ctx.lineWidth = 5
            ctx.strokeRect(
              el.bbox[0] * scale + x,
              el.bbox[1] * scale + y,
              el.bbox[2] * scale,
              el.bbox[3] * scale,
            )
            ctx.restore()
          }
        })
      }
    }
  }, [bboxes, height, img_src, width])

  return (
    <Box ref={containerRef}>
      {width > 0 && (
        <canvas id="img_canvas" width={width} height={height} ref={canvasRef} />
      )}
    </Box>
  )
}

export default ImageBoundingBoxViewer
