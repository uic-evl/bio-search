export {}

declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NX_SEARCH_API: string
      NX_PDFS_ENDPOINT: string
      NX_FIGURES_ENDPOINT: string
      NX_COLLECTION: string
    }
  }
}
