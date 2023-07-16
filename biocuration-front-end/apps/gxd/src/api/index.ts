import {run} from '@biocuration-front-end/requests-api'
import {Document} from '@biocuration-front-end/common-ui'
import {LuceneDocument} from '@biocuration-front-end/common-ui'

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
  return payload as LuceneDocument[]
}

export const getPageFigureDetails = async (
  documentId: string,
  preferredOrder: string[],
): Promise<Document> => {
  const url = `${SEARCH_API_ENDPOINT}/document/${documentId}`
  const payload: Document = await run(url, 'get', {
    data: undefined,
    token: undefined,
    params: undefined,
  })

  // match the GDX structure to TS types

  if (preferredOrder.length > 0) {
    payload.pages.forEach(page => {
      let score = 0
      page.figures.forEach(figure => {
        let figurePriority = 0
        figure.subfigures.forEach(subfigure => {
          preferredOrder.forEach(prioritized_type => {
            if (
              prioritized_type === subfigure.type ||
              subfigure.type.includes(prioritized_type)
            ) {
              score += 1
              figurePriority += 1
            }
          })
          // if (preferredOrder.includes(subfigure.type)) {
          //   score += 1
          //   figurePriority += 1
          // }
        })
        figure.priority = figurePriority
      })
      page.priority = score
    })

    payload.pages.forEach(page => {
      page.figures = page.figures.sort((fig1, fig2) => {
        const b = fig2.priority ? fig2.priority : 0
        const a = fig1.priority ? fig1.priority : 0
        return b - a
      })
    })

    payload.pages = payload.pages.sort((page1, page2) => {
      const b = page2.priority ? page2.priority : 0
      const a = page1.priority ? page1.priority : 0
      return b - a
    })
  } else {
    // sort by page number
    payload.pages = payload.pages.sort((page1, page2) => {
      const b = page2.page
      const a = page1.page
      return a - b
    })
  }

  return payload
}

export const login = async (username: string, password: string) => {
  const url = `${APP_API_ENDPOINT}/users/login`
  console.log(url)
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

export const logExperimenterResult = async (
  authToken: string,
  uid: string,
  condition: string,
  docId: string,
  decision: boolean,
  completionTime: number,
) => {
  const url = `${APP_API_ENDPOINT}/experimenter/individual`
  try {
    await run(url, 'post', {
      token: authToken,
      data: {uid, condition, docId, decision, completionTime},
      params: undefined,
    })

    return true
  } catch (error) {
    return false
  }
}
