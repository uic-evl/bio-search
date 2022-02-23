import axios from 'axios'

const API_ENDPOINT = process.env.REACT_APP_API

async function client(endpoint, method, {data, params} = {}) {
  const headers = {}

  try {
    const response = await axios({
      method,
      url: `${API_ENDPOINT}/${endpoint}`,
      data,
      headers,
      params,
    })

    return {error: false, payload: response.data, message: null}
  } catch (error) {
    if (error.message === 'Network Error') {
      return {error: true, payload: null, message: error.message}
    }
    if (error.response.status === 400) {
      return {
        error: true,
        payload: null,
        message: 'Cannot reach server endpoint',
      }
    }
    if (error.response.status === 500) {
      return {
        error: true,
        payload: null,
        message: 'Server error, contact the system administrator',
      }
    }
  }
}

async function run(endpoint, method, {data, token, params} = {}) {
  // if used with react-query, populate the error fields
  // for other calls, handle with try - catch
  const {error, payload, message} = await client(endpoint, method, {
    data,
    params,
  })
  if (error) throw new Error(message)
  else return payload
}

export {client, run}
