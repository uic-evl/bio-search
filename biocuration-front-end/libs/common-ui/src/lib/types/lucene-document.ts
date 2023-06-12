export interface LuceneCaption {
  figure_id: number
  text: string
}

export interface LuceneDocument {
  id: number
  title: string
  publish_date: string
  abstract: string
  journal: string
  authors: string
  url: string
  num_figures: number
  modalities_count: {[id: string]: number}
  full_text: string | null
  captions: LuceneCaption[]
  otherid: string
}
