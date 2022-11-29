import {run} from '@search-publications-and-figures/api'
import {Document} from 'libs/common-ui/src/lib/types/document'
import {LuceneDocument} from 'libs/common-ui/src/lib/types/lucene-document'

const SEARCH_API_ENDPOINT = process.env.NX_SEARCH_API
const APP_API_ENDPOINT = process.env.NX_SEARCH_API
const LOCAL_STORAGE_KEY = process.env.NX_LOCAL_STORAGE_KEY

interface User {
  username: string
  token: string
}

export const search = async (
  keywords: string,
  collection: string,
  startDate: string | null,
  endDate: string | null,
  maxDocs: number,
  modalities: string[],
): Promise<LuceneDocument[]> => {
  const termsQuery = keywords || '*'
  let queryString = `?highlight=true&q=${termsQuery}&max_docs=${maxDocs}`
  if (startDate) {
    queryString += `&from=${startDate}`
    if (endDate) {
      queryString += `&to=${endDate}`
    }
  }
  if (modalities.length > 0) {
    const joinedMods = modalities.join(';')
    queryString += `&modalities=${joinedMods}`
  }
  queryString += `&ds=${collection}`

  const url = `${SEARCH_API_ENDPOINT}/search/${queryString}`
  const payload = await run(url, 'get', {
    data: undefined,
    token: undefined,
    params: undefined,
  })
  return payload
}

export const getPageFigureDetails = async (
  documentId: string,
): Promise<Document> => {
  const url = `${SEARCH_API_ENDPOINT}/document2/${documentId}`
  const payload = await run(url, 'get', {
    data: undefined,
    token: undefined,
    params: undefined,
  })
  return payload
}

export const login = async (username: string, password: string) => {
  const url = `${APP_API_ENDPOINT}/users/login`
  try {
    const payload = await run(url, 'post', {
      data: {username, password},
      token: undefined,
      params: undefined,
    })
    localStorage.setItem(LOCAL_STORAGE_KEY, payload.token)

    if (payload.username) {
      return {
        user: {username: payload.username},
        message: `welcome ${payload.username}`,
      }
    } else {
      let message = payload.message
      if (payload.message === 'Missing credentials') {
        message = 'Please enter a username and password'
      }
      return {user: null, message}
    }
  } catch (error) {
    return {user: null, message: error}
  }
}

export const logout = async () => {
  localStorage.removeItem(LOCAL_STORAGE_KEY)
}

export const getToken = () => {
  return localStorage.getItem(LOCAL_STORAGE_KEY)
}

export const me = async (authToken: string): Promise<Promise<User | null>> => {
  const url = `${APP_API_ENDPOINT}/users/me`
  try {
    const data = await run(url, 'get', {
      token: authToken,
      data: undefined,
      params: undefined,
    })

    const {username, token} = data
    return {username, token}
  } catch (error) {
    return null
  }
}
