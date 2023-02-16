import {useState, useRef, useLayoutEffect, useEffect, MouseEvent} from 'react'
import {Box, Flex} from '@chakra-ui/react'

interface BoundingBox {
  x: number
  y: number
  width: number
  height: number
}

/* eslint-disable-next-line */
export interface AnnotationsProps {
  padding: number
  imageSrc: string
}

export function Annotations({imageSrc, padding}: AnnotationsProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const imageCanvasRef = useRef<HTMLCanvasElement>(null)
  const annotCanvasRef = useRef<HTMLCanvasElement>(null)
  const [canvasHeight, setCanvasHeight] = useState(0)
  const [canvasWidth, setCanvasWidth] = useState(0)
  const [interactableArea, setInteractableArea] = useState<number[] | null>(
    null,
  )
  const [startPoint, setStartPoint] = useState<number[] | null>(null)
  const [boundingBoxes, setBoundingBoxes] = useState<BoundingBox[]>([])

  useLayoutEffect(() => {
    // Adjust the canvas size to the size give to the div parent size
    if (containerRef.current) {
      const containerDiv = containerRef.current.parentElement
      if (containerDiv) {
        setCanvasHeight(containerDiv.offsetHeight - padding)
        setCanvasWidth(containerDiv.offsetWidth - padding)
      }
    }
  }, [padding])

  useEffect(() => {
    const paintBackground = (ctx: CanvasRenderingContext2D) => {
      ctx.save()
      ctx.fillStyle = 'black'
      ctx.fillRect(0, 0, canvasWidth, canvasHeight)
      ctx.restore()
    }

    const loadImage = (
      canvas: HTMLCanvasElement,
      ctx: CanvasRenderingContext2D,
    ) => {
      const image = new Image()
      image.src = imageSrc
      image.onload = () => {
        const scale = Math.min(
          canvas.width / image.width,
          canvas.height / image.height,
        )
        const x = canvas.width / 2 - (image.width / 2) * scale
        const y = canvas.height / 2 - (image.height / 2) * scale
        ctx.drawImage(image, x, y, image.width * scale, image.height * scale)
        setInteractableArea([x, y, image.width * scale, image.height * scale])
      }
    }

    if (
      canvasWidth > 0 &&
      canvasHeight > 0 &&
      null !== imageCanvasRef.current
    ) {
      console.log('loading image')
      const canvas = imageCanvasRef.current
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      paintBackground(ctx)
      loadImage(canvas, ctx)
    }
  }, [canvasWidth, canvasHeight, imageSrc])

  const getAnnotationContext = () => {
    const canvas = annotCanvasRef.current
    if (!canvas) return null
    return canvas.getContext('2d')
  }

  const canInteract = (x: number, y: number) => {
    if (!interactableArea) return false
    const x1 = interactableArea[0] + interactableArea[2]
    const y1 = interactableArea[1] + interactableArea[3]
    return (
      x >= interactableArea[0] && x <= x1 && y >= interactableArea[1] && y <= y1
    )
  }

  const drawBoundingBoxes = (boxes: BoundingBox[]) => {
    const ctx = getAnnotationContext()
    if (!ctx || !interactableArea) return
    ctx.clearRect(
      interactableArea[0],
      interactableArea[1],
      interactableArea[2],
      interactableArea[3],
    )
    for (const bbox of boxes) {
      ctx.save()
      ctx.strokeStyle = 'red'
      ctx.strokeRect(bbox.x, bbox.y, bbox.width, bbox.height)
      ctx.restore()
    }
  }

  const getCanvasCoordinates = (e: MouseEvent) => {
    if (!interactableArea || imageCanvasRef.current === null) return null
    const rect = imageCanvasRef.current.getBoundingClientRect()
    const {x, y} = e.nativeEvent
    return {x: x - rect.left, y: y - rect.top}
  }

  const handleMouseDown = (e: MouseEvent) => {
    const coords = getCanvasCoordinates(e)
    if (!coords) return
    const {x, y} = coords
    if (canInteract(x, y)) {
      setStartPoint([x, y])
    }
  }

  const handleMouseUp = (e: MouseEvent) => {
    const coords = getCanvasCoordinates(e)
    if (!coords || !startPoint) return
    const {x, y} = coords
    if (canInteract(x, y)) {
      const x0 = Math.min(startPoint[0], x)
      const y0 = Math.min(startPoint[1], y)
      const x1 = Math.max(startPoint[0], x)
      const y1 = Math.max(startPoint[1], y)

      const ctx = getAnnotationContext()
      if (!ctx) return

      const boxes = [
        ...boundingBoxes,
        {x: x0, y: y0, width: x1 - x0, height: y1 - y0},
      ]
      drawBoundingBoxes(boxes)
      setBoundingBoxes(boxes)
    }
  }

  return (
    <Flex
      w="full"
      h="full"
      position="relative"
      ref={containerRef}
      justifyContent="center"
      alignItems="center"
    >
      {canvasWidth > 0 && canvasHeight > 0 ? (
        <>
          <canvas
            id="img_canvas"
            width={canvasWidth}
            height={canvasHeight}
            style={{position: 'absolute', top: padding / 2, left: padding / 2}}
            ref={imageCanvasRef}
          />
          <canvas
            id="img_annotations"
            style={{position: 'absolute', top: padding / 2, left: padding / 2}}
            width={canvasWidth}
            height={canvasHeight}
            ref={annotCanvasRef}
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
          />
        </>
      ) : null}
    </Flex>
  )
}

export default Annotations
