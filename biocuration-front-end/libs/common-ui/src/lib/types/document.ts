/** cord_uid and bboxes are now here because the GDX api returns them in a
 * different structure than the db. TODO: standardize
 */
export interface Document {
  id: number
  pages: Page[]
  pmcid: string
  cord_uid?: string
  otherid: string
  bboxes?: {[id: string]: {[id: string]: number[]}}
}

/** bbox is an array [xMin, yMin, width, height] where
 * xMin and yMin is the top left corner for coordinate systems where the top
 * left is (0,0), as in an html canvas. This could also be a type per se but
 * I'm not sure if it's convenient to add this complexity
 */
export interface Subfigure {
  name?: string
  bbox: number[] | null
  color: string
  type: string
}

export interface Figure {
  id: number
  caption: string
  subfigures: Subfigure[]
  url: string
  priority?: number
}

export interface Page {
  page: number
  page_url: string
  priority?: number
  figures: Figure[]
}
