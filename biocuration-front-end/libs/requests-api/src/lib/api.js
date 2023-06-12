import axios from 'axios'

async function client(endpoint, method, {data, params, token} = {}) {
  const headers = {
    Authorization: token ? `Bearer ${token}` : undefined,
    'Content-Type': 'application/json',
  }

  try {
    const response = await axios({
      method,
      url: endpoint,
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
      const message =
        'data' in error.response && 'description' in error.response.data
          ? error.response.data.description
          : 'unknown message'

      return {
        error: true,
        payload: null,
        message,
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
    token,
  })
  if (error) throw new Error(message)
  else return payload
}

export {client, run}
