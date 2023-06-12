import {
  useState,
  useRef,
  useLayoutEffect,
  useEffect,
  MouseEvent,
  ReactNode,
} from 'react'
import {Box, Flex, Icon, IconButton} from '@chakra-ui/react'
import {AddIcon, EditIcon, DeleteIcon} from '@chakra-ui/icons'

type LabelingAction = 'insert' | 'update' | 'delete' | 'none'

interface BoundingBox {
  x: number
  y: number
  width: number
  height: number
  figure_id?: number
  label?: string
  action: LabelingAction
}

interface Handle {
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
  const [mode, setMode] = useState<string | null>(null)
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null)
  // handles
  const [leftHandle, setLeftHandle] = useState<Handle | null>(null)
  const [rightHandle, setRightHandle] = useState<Handle | null>(null)
  const [topHandle, setTopHandle] = useState<Handle | null>(null)
  const [bottomHandle, setBottomHandle] = useState<Handle | null>(null)

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

  useEffect(() => {
    drawBoundingBoxes(boundingBoxes)
  }, [mode])

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

  const drawHandle = (ctx: CanvasRenderingContext2D, handle: Handle) => {
    ctx.save()
    ctx.fillStyle = 'red'
    ctx.fillRect(handle.x, handle.y, handle.width, handle.height)
    ctx.restore()
  }

  const drawHandles = () => {
    const ctx = getAnnotationContext()
    if (!ctx || !interactableArea) return
    if (mode !== 'edit' && mode !== 'resizing') return
    if (leftHandle) drawHandle(ctx, leftHandle)
    if (rightHandle) drawHandle(ctx, rightHandle)
    if (topHandle) drawHandle(ctx, topHandle)
    if (bottomHandle) drawHandle(ctx, bottomHandle)
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
    for (const [idx, bbox] of boxes.entries()) {
      if (bbox.action === 'none') continue

      ctx.save()
      ctx.strokeStyle = 'red'
      if (idx === selectedIdx) {
        ctx.setLineDash([4])
        ctx.fillStyle = 'yellow'
        ctx.globalAlpha = 0.2
        ctx.fillRect(bbox.x, bbox.y, bbox.width, bbox.height)
      }
      ctx.globalAlpha = 1
      ctx.strokeRect(bbox.x, bbox.y, bbox.width, bbox.height)
      ctx.restore()
    }
    drawHandles()
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
    if (!canInteract(x, y)) return
    if (mode === 'add') {
      setStartPoint([x, y])
    } else if (mode === 'edit') {
      if (leftHandle && isPointerOnHandle(x, y, leftHandle)) {
        console.log('clicking left')
        setMode('resize')
        return
      }

      for (const [idx, bbox] of boundingBoxes.entries()) {
        if (isPointerInside(x, y, bbox)) {
          setSelectedIdx(idx)
          setLeftHandle({
            x: bbox.x - 5,
            y: bbox.y + bbox.height / 2,
            width: 10,
            height: 10,
          })
          setRightHandle({
            x: bbox.x + bbox.width - 5,
            y: bbox.y + bbox.height / 2,
            width: 10,
            height: 10,
          })
          setTopHandle({
            x: bbox.x + bbox.width / 2 - 5,
            y: bbox.y - 5,
            width: 10,
            height: 10,
          })
          setBottomHandle({
            x: bbox.x + bbox.width / 2 - 5,
            y: bbox.y + bbox.height - 5,
            width: 10,
            height: 10,
          })
          break
        }
      }
    }
  }

  const handleMouseUp = (e: MouseEvent) => {
    console.log('mouse up', mode)
    if (mode === 'resize') {
      setMode('edit')
      return
    }

    const coords = getCanvasCoordinates(e)
    if (!coords || !startPoint) return
    const {x, y} = coords

    if (canInteract(x, y)) {
      const x0 = Math.min(startPoint[0], x)
      const y0 = Math.min(startPoint[1], y)
      const x1 = Math.max(startPoint[0], x)
      const y1 = Math.max(startPoint[1], y)

      const action: LabelingAction = 'insert'
      const boxes = [
        ...boundingBoxes,
        {
          x: x0,
          y: y0,
          width: x1 - x0,
          height: y1 - y0,
          action,
        },
      ]
      drawBoundingBoxes(boxes)
      setBoundingBoxes(boxes)
      setStartPoint(null)
    }
  }

  const isPointerInside = (x: number, y: number, bbox: BoundingBox) => {
    return (
      bbox.action !== 'none' &&
      x >= bbox.x &&
      x <= bbox.x + bbox.width &&
      y >= bbox.y &&
      y <= bbox.y + bbox.height
    )
  }

  const isPointerOnHandle = (x: number, y: number, handle: Handle) => {
    return (
      handle &&
      x >= handle.x &&
      x <= handle.x + handle.width &&
      y >= handle.y &&
      y <= handle.y + handle.height
    )
  }

  const handleMouseMove = (e: MouseEvent) => {
    const coords = getCanvasCoordinates(e)
    if (!coords) return
    const {x, y} = coords
    if (!canInteract(x, y)) return

    if (mode === 'add' && startPoint) {
      // dragging to create new box
      drawBoundingBoxes(boundingBoxes)
      const x0 = Math.min(startPoint[0], x)
      const y0 = Math.min(startPoint[1], y)
      const x1 = Math.max(startPoint[0], x)
      const y1 = Math.max(startPoint[1], y)
      const ctx = getAnnotationContext()
      if (!ctx) return
      ctx.save()
      ctx.strokeStyle = 'grey'
      ctx.strokeRect(x0, y0, x1 - x0, y1 - y0)
      ctx.restore()
    } else if (mode === 'edit') {
      drawBoundingBoxes(boundingBoxes)
      for (const bbox of boundingBoxes) {
        if (isPointerInside(x, y, bbox)) {
          const ctx = getAnnotationContext()
          if (!ctx) return
          ctx.save()
          ctx.fillStyle = 'yellow'
          ctx.globalAlpha = 0.2
          ctx.fillRect(bbox.x, bbox.y, bbox.width, bbox.height)
          ctx.restore()
        }
      }

      if (!annotCanvasRef.current) return
      if (
        (leftHandle && isPointerOnHandle(x, y, leftHandle)) ||
        (rightHandle && isPointerOnHandle(x, y, rightHandle))
      ) {
        annotCanvasRef.current.style.cursor = 'w-resize'
      } else if (
        (topHandle && isPointerOnHandle(x, y, topHandle)) ||
        (bottomHandle && isPointerOnHandle(x, y, bottomHandle))
      ) {
        annotCanvasRef.current.style.cursor = 'n-resize'
      } else {
        annotCanvasRef.current.style.cursor = 'default'
      }
    } else if (mode === 'resize' && selectedIdx !== null) {
      const newX = x
      // drawing left handle
      const updates = [...boundingBoxes]
      const oldX = updates[selectedIdx].x
      updates[selectedIdx].x = newX
      const diff = Math.abs(newX - oldX)
      if (newX < oldX)
        updates[selectedIdx].width = updates[selectedIdx].width + diff
      else updates[selectedIdx].width = updates[selectedIdx].width - diff
      drawBoundingBoxes(updates)
      if (leftHandle) setLeftHandle({...leftHandle, x: newX - 5})
      setBoundingBoxes(updates)
    }
  }

  return (
    <Flex direction="column" w="full" h="full">
      <ButtonsBar>
        <IconButton
          aria-label="edit annotation"
          icon={<EditIcon />}
          size="xs"
          backgroundColor={mode !== 'edit' ? 'gray.100' : 'gray.500'}
          onClick={() => setMode('edit')}
        />
        <IconButton
          aria-label="add annotation"
          icon={<AddIcon />}
          size="xs"
          backgroundColor={mode !== 'add' ? 'gray.100' : 'gray.500'}
          onClick={() => {
            setMode('add')
            setSelectedIdx(null)
            setLeftHandle(null)
            setRightHandle(null)
            setTopHandle(null)
            setBottomHandle(null)
          }}
        />
        <IconButton
          aria-label="delete annotation"
          icon={<DeleteIcon />}
          size="xs"
          ml={1}
          backgroundColor={'gray.100'}
          disabled={selectedIdx === null}
          onClick={() => {
            const updates = [...boundingBoxes]
            for (const [idx, bbox] of updates.entries()) {
              if (idx === selectedIdx) {
                bbox.action = 'none'
              }
            }
            drawBoundingBoxes(updates)
            setBoundingBoxes(updates)
            setLeftHandle(null)
            setRightHandle(null)
            setTopHandle(null)
            setBottomHandle(null)
          }}
        />
      </ButtonsBar>
      <Flex
        w="full"
        minH="calc(100% - 30px);"
        h="calc(100% - 30px);"
        position="relative"
        ref={containerRef}
        justifyContent="center"
        alignItems="center"
        backgroundColor={'gray.100'}
      >
        {canvasWidth > 0 && canvasHeight > 0 ? (
          <>
            <canvas
              id="img_canvas"
              width={canvasWidth}
              height={canvasHeight}
              style={{
                position: 'absolute',
                top: padding / 2,
                left: padding / 2,
              }}
              ref={imageCanvasRef}
            />
            <canvas
              id="img_annotations"
              style={{
                position: 'absolute',
                top: padding / 2,
                left: padding / 2,
              }}
              width={canvasWidth}
              height={canvasHeight}
              ref={annotCanvasRef}
              onMouseDown={handleMouseDown}
              onMouseUp={handleMouseUp}
              onMouseMove={handleMouseMove}
            />
          </>
        ) : null}
      </Flex>
    </Flex>
  )
}

interface ButtonsBarProps {
  children: ReactNode
}

const ButtonsBar = (props: ButtonsBarProps) => (
  <Flex
    w="full"
    h="30px"
    backgroundColor={'gray.100'}
    justifyContent="right"
    alignItems="center"
  >
    {props.children}
  </Flex>
)

export default Annotations
