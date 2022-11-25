export interface Document {
  id: number
  pages: Page[]
}

/** bbox is an array [xMin, yMin, width, height] where
 * xMin and yMin is the top left corner for coordinate systems where the top
 * left is (0,0), as in an html canvas. This could also be a type per se but
 * I'm not sure if it's convenient to add this complexity
 */
export interface Subfigure {
  bbox: number[] | null
  color: string
  type: string
}

export interface Figure {
  caption: string
  subfigures: Subfigure[]
  url: string
}

export interface Page {
  pageNumber: number
  figures: Figure[]
}
