import {run} from '@search-publications-and-figures/api'
import {
  Document,
  LuceneDocument,
} from '@search-publications-and-figures/common-ui'

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
  let queryString = `?highlight=true&ft=true&q=${termsQuery}&max_docs=${maxDocs}`
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
  preferredOrder: string[],
): Promise<Document> => {
  const url = `${SEARCH_API_ENDPOINT}/document2/${documentId}`
  const payload: Document = await run(url, 'get', {
    data: undefined,
    token: undefined,
    params: undefined,
  })
  // TODO: the sorting can be done on the web server, meanwhile here
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
  }

  return payload
}
