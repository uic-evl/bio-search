/**
 * Return an array with elements NOT in the filter object
 * From https://gist.github.com/jherax/f11d669ba286f21b7a2dcff69621eb72
 * but negated. Filters [] are not ignored.
 * @param {*} arr Array of ScatterDot[]
 * @param {*} filters Record<string, string[]> where the keys are attributes of ScatterDot
 * @returns
 */

export const multiFilter = (arr, filters) => {
  const filterKeys = Object.keys(filters)
  return arr.filter(eachObj => {
    return filterKeys.every(eachKey => {
      if (!filters[eachKey].length) {
        return true // passing an empty filter means that filter is ignored.
      }
      return !filters[eachKey].includes(eachObj[eachKey])
    })
  })
}
