import {run} from '../utils/apiClient'

export const search = async (
  terms,
  collection,
  startDate,
  endDate,
  maxDocs,
) => {
  const termsQuery = terms || '*'
  let queryString = `?highlight=true&q=${termsQuery}&max_docs=${maxDocs}`
  if (startDate) {
    queryString += `&from=${startDate}`
    if (endDate) {
      queryString += `&to=${endDate}`
    }
  }

  const url = `search/${queryString}`
  const payload = await run(url, 'get', {})
  return payload
}
