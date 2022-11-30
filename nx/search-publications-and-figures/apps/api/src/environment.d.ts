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
      CURRYSOUP: string
      NODE_ENV: string
    }
  }
}
