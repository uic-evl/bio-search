import {run} from '../utils/apiClient'

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
    console.log('joined', joinedMods)
    queryString += `&modalities=${joinedMods}`
  }

  const url = `search/${queryString}`
  const payload = await run(url, 'get', {})
  return payload
}

export const getDetails = async documentId => {
  const url = `document/${documentId}`
  const payload = await run(url, 'get', {})
  return payload
}
