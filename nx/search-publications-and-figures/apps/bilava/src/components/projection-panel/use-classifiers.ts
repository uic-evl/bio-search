import {useState, useEffect} from 'react'
import {fetch_available_classifiers} from '../../api'

export const useClassifiers = (project: string) => {
  const [classifiers, setClassifiers] = useState<string[]>([])

  useEffect(() => {
    const loadTreeData = async () => {
      try {
        const payload = await fetch_available_classifiers(project)
        setClassifiers(payload)
      } catch (e) {
        console.log(e)
      }
    }
    loadTreeData()
  }, [project])

  return classifiers
}
