import {PathOrFileDescriptor} from 'fs'

export {}

declare global {
  namespace NodeJS {
    interface ProcessEnv {
      PK: PathOrFileDescriptor
      CRT: PathOrFileDescriptor
      PORT: number
      HTTPS: string
      SECRET: string
      MAYO: string
      CURRYSAUCE: string
      NODE_ENV: string
      EXPPATH?: string
    }
  }
}
