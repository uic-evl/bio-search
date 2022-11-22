/**
 * Control the state logic for the search interface.
 * TODO: change detailsTop/Bottom and selectedIds to one array
 */

const initState = {
  isLoading: false, // whether the search is running or not
  documents: null, // search results
  detailsTop: null, // document to show on top
  detailsBottom: null, // document to show on bottom
  selectedIds: [], // helper to get ids
}

const searchReducer = (state, action) => {
  const {detailsTop, detailsBottom} = state

  switch (action.type) {
    case 'START_SEARCH':
      return {
        ...initState,
        isLoading: true,
      }
    case 'END_SEARCH':
      return {
        ...state,
        isLoading: false,
        documents: action.payload,
      }
    case 'OPEN_DETAILS':
      return {
        ...state,
        detailsTop:
          action.payload.position === 'top'
            ? action.payload.details
            : detailsTop,
        detailsBottom:
          action.payload.position === 'bottom'
            ? action.payload.details
            : detailsBottom,
        selectedIds: [...state.selectedIds, action.payload.documentId],
      }
    case 'CLOSE_DETAILS':
      const {documentId} = action.payload
      return {
        ...state,
        detailsTop:
          detailsTop && detailsTop.cord_uid === documentId ? null : detailsTop,
        detailsBottom:
          detailsBottom && detailsBottom.cord_uid === documentId
            ? null
            : detailsBottom,
        selectedIds: state.selectedIds.filter(id => id !== documentId),
      }
    default:
      break
  }
}

export {searchReducer, initState}
