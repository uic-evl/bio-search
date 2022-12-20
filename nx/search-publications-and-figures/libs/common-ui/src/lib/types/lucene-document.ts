export interface LuceneDocument {
  id: number
  title: string
  publish_date: string
  abstract: string
  url: string
  num_figures: number
  modalities_count: {[id: string]: number}
  full_text: string | null
}
