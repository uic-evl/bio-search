import {run} from '@search-publications-and-figures/api'
import {Document} from 'libs/common-ui/src/lib/types/document'
import {LuceneDocument} from 'libs/common-ui/src/lib/types/lucene-document'

const SEARCH_API_ENDPOINT = process.env.NX_SEARCH_API

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
