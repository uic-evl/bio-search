export {}

declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NX_SEARCH_API: string
      NX_PDFS_ENDPOINT: string
      NX_FIGURES_ENDPOINT: string
      NX_COLLECTION: string
      NX_BASE_PATH: string
      NX_LOCAL_STORAGE_KEY: string
    }
  }
}
