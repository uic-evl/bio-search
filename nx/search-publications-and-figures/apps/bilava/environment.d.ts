export {}

declare global {
  namespace NodeJS {
    interface ProcessEnv {
      NX_API: string
    }
  }
}
