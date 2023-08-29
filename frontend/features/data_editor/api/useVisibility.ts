import { useState } from 'react'

const useVisibility = () => {
  const [allColumns, setAllColumns] = useState(false)

  const triggerColumns = () => {
    setAllColumns(!allColumns)
  }

  return {
    allColumns,
    triggerColumns
  }
}

export default useVisibility
