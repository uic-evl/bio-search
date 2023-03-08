import styles from './taxonomy-tree.module.css'

/* eslint-disable-next-line */
export interface TaxonomyTreeProps {}

export function TaxonomyTree(props: TaxonomyTreeProps) {
  return (
    <div className={styles['container']}>
      <h1>Welcome to TaxonomyTree!</h1>
    </div>
  )
}

export default TaxonomyTree
