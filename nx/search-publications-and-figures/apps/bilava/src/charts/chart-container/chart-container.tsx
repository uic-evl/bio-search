import styles from './chart-container.module.css'

/* eslint-disable-next-line */
export interface ChartContainerProps {}

export function ChartContainer(props: ChartContainerProps) {
  return (
    <div className={styles['container']}>
      <h1>Welcome to ChartContainer!</h1>
    </div>
  )
}

export default ChartContainer
