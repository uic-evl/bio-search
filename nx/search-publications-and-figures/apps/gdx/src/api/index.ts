import {run} from '@search-publications-and-figures/api'
import {
  Document,
  Page,
  Figure,
  Subfigure,
} from '@search-publications-and-figures/common-ui'
import {LuceneDocument} from '@search-publications-and-figures/common-ui'
import {
  reverseNamesMapper,
  namesMapper,
  codeMapper,
  colorsMapper,
} from '../utils/mapper'

const SEARCH_API_ENDPOINT = process.env.NX_SEARCH_API
const APP_API_ENDPOINT = process.env.NX_APP_API
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
  let queryString = `?highlight=true&ft=false&q=${termsQuery}&max_docs=${maxDocs}`
  if (startDate) {
    queryString += `&from=${startDate}`
    if (endDate) {
      queryString += `&to=${endDate}`
    }
  }

  if (modalities.length > 0) {
    const mappedModalities = modalities.map(el => namesMapper[el])
    const joinedMods = mappedModalities.join(';')
    queryString += `&modalities=${joinedMods}`
  }
  queryString += `&ds=${collection}`

  const url = `${SEARCH_API_ENDPOINT}/search/${queryString}`
  const payload: LuceneDocument[] = await run(url, 'get', {
    data: undefined,
    token: undefined,
    params: undefined,
  })

  payload.forEach(el => {
    const newMapping: Record<string, number> = {}
    Object.keys(el.modalities_count).forEach(key => {
      newMapping[reverseNamesMapper[key]] = el.modalities_count[key]
    })
    el.modalities_count = newMapping as unknown as {[id: string]: number}
  })

  return payload
}

export const getPageFigureDetails = async (
  documentId: string,
): Promise<Document> => {
  const url = `${SEARCH_API_ENDPOINT}/document/${documentId}`
  const document: Document = await run(url, 'get', {
    data: undefined,
    token: undefined,
    params: undefined,
  })

  // match the GDX structure to TS types

  const {cord_uid, bboxes} = document
  if (bboxes) {
    document.pages.forEach((page: Page) => {
      const pageNumber = page.page
      page.figures.forEach((figure: Figure, idx: number) => {
        figure.url = `${cord_uid}/${pageNumber}_${idx + 1}.jpg`
        const newSubfigures = figure.subfigures.map((sf: Subfigure) => {
          const {name} = sf
          return {
            bbox: name ? bboxes[`${pageNumber}_${idx + 1}`][name] : null,
            type: codeMapper[sf.type],
            color: colorsMapper[codeMapper[sf.type]],
          }
        })
        figure.subfigures = newSubfigures
      })
    })
  }

  return document
}

export const login = async (username: string, password: string) => {
  const url = `${APP_API_ENDPOINT}/users/login`
  try {
    const payload = await run(url, 'post', {
      data: {username, password},
      token: undefined,
      params: undefined,
    })
    console.log(payload)
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
