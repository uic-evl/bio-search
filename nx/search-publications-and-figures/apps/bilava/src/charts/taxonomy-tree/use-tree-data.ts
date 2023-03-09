import {useState, useEffect} from 'react'
import {TreeData} from '../../types'
import {fetch_db_labels} from '../../api'
import {colorsMapper} from '../../utils/mapper'

export const useTreeData = (taxonomy: string) => {
  const [treeData, setTreeData] = useState<TreeData | null>(null)

  useEffect(() => {
    const loadTreeData = async () => {
      try {
        const payload = await fetch_db_labels(taxonomy)
        setTreeData({taxonomy: Object.keys(colorsMapper), data: payload})
      } catch (e) {
        console.log(e)
      }
    }
    loadTreeData()
  }, [taxonomy])

  return treeData
}
