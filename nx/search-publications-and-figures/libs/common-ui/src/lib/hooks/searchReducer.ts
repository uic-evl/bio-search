import {LuceneDocument} from '../types/lucene-document'

type Action =
  | {type: 'START_SEARCH'}
  | {type: 'END_SEARCH'; payload: LuceneDocument[]}

type State = {
  isLoading: boolean
  documents: LuceneDocument[] | null
  error: string | null
}

export const initSearchState = {
  isLoading: false,
  documents: null,
  error: null,
}

export const searchReducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'START_SEARCH':
      return {
        ...initSearchState,
        isLoading: true,
      }
    case 'END_SEARCH':
      return {
        ...state,
        isLoading: false,
        documents: action.payload,
      }
    default:
      throw Error('invalid action in search reducer')
  }
}
