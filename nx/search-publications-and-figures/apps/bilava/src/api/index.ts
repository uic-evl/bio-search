import {run} from '@search-publications-and-figures/api'

const BILAVA_ENDPOINT = import.meta.env.VITE_API

export const fetch_db_labels = async (project: string): Promise<string[]> => {
  const url = `${BILAVA_ENDPOINT}/tree/${project}`
  const payload = await run(url, 'get', {
    data: undefined,
    token: undefined,
    params: undefined,
  })
  return payload as string[]
}

export const fetch_available_classifiers = async (
  project: string,
): Promise<string[]> => {
  const url = `${BILAVA_ENDPOINT}/classifiers/${project}`
  const payload = await run(url, 'get', {
    data: undefined,
    token: undefined,
    params: undefined,
  })
  return payload as string[]
}
