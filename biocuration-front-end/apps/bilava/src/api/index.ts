import {run} from '@biocuration-front-end/requests-api'
import {Dataset, ImageExtras, ResponseError, UpdateResult} from '../types'

const BILAVA_ENDPOINT = import.meta.env.VITE_API
const NO_TOKEN_NO_PARAMS = {token: undefined, params: undefined}

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

export const fetch_projections = async (
  classifier: string,
  projection: string,
  splitSet: string,
): Promise<Dataset> => {
  const url = `${BILAVA_ENDPOINT}/projections/${classifier}/${projection}/${splitSet}`
  const payload = await run(url, 'get', {
    data: undefined,
    token: undefined,
    params: undefined,
  })
  return payload
}

export const fetch_image_extras = async (
  imgId: number,
  classifier: string,
): Promise<ImageExtras> => {
  const url = `${BILAVA_ENDPOINT}/images/${imgId}/${classifier}/extras`
  const payload = await run(url, 'get', {
    data: undefined,
    token: undefined,
    params: undefined,
  })
  return payload
}

export const batch_update = async (
  imgIds: number[],
  newLabel: string,
): Promise<ResponseError | UpdateResult> => {
  const url = `${BILAVA_ENDPOINT}/images/batch_update`

  try {
    const data = {ids: imgIds, label: newLabel}
    const payload: UpdateResult = await run(url, 'post', {
      data,
      ...NO_TOKEN_NO_PARAMS,
    })
    return payload
  } catch (e) {
    return {
      error: true,
      description: (e as Error).message,
    }
  }
}
