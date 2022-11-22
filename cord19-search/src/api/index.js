import {run} from '../utils/apiClient'

const API_ENDPOINT = process.env.REACT_APP_API
const API_AUTH_ENDPOINT = process.env.REACT_APP_AUTH_API
const LOCAL_STORAGE_KEY = process.env.REACT_APP_AUTH_KEY

export const search = async (
  terms,
  collection,
  startDate,
  endDate,
  maxDocs,
  modalities,
) => {
  const termsQuery = terms || '*'
  let queryString = `?highlight=true&q=${termsQuery}&max_docs=${maxDocs}`
  if (startDate) {
    queryString += `&from=${startDate}`
    if (endDate) {
      queryString += `&to=${endDate}`
    }
  }
  if (modalities.length > 0) {
    const queryModalities = modalities.map(el => el.value)
    const joinedMods = queryModalities.join(';')
    queryString += `&modalities=${joinedMods}`
  }
  queryString += `&ds=${collection}`

  const url = `${API_ENDPOINT}/search/${queryString}`
  const payload = await run(url, 'get', {})
  return payload
}

export const getDetails = async documentId => {
  const url = `${API_ENDPOINT}/document2/${documentId}`
  const payload = await run(url, 'get', {})
  return payload
}

export const login = async (username, password) => {
  const url = `${API_AUTH_ENDPOINT}/users/login`
  try {
    const payload = await run(url, 'post', {data: {username, password}})
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

export const me = async token => {
  const url = `${API_AUTH_ENDPOINT}/users/me`
  try {
    const data = await run(url, 'get', {token})
    return {user: {username: data.username, token: data.token}}
  } catch (error) {
    return null
  }
}
