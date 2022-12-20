import {LuceneDocument} from '../types/lucene-document'

type Action =
  | {type: 'START_SEARCH'; payload: string[]}
  | {type: 'END_SEARCH'; payload: LuceneDocument[]}

type State = {
  isLoading: boolean
  documents: LuceneDocument[] | null
  filterModalities: string[]
  error: string | null
}

export const initSearchState = {
  isLoading: false,
  documents: null,
  filterModalities: [],
  error: null,
}

export const searchReducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'START_SEARCH':
      return {
        ...initSearchState,
        filterModalities: action.payload,
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
