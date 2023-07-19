import { useMemo, useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import {
  useGridApiRef
} from '@mui/x-data-grid'

const rows = []

const useTemplateDataEditor = () => {
  const { data } = useOutletContext()
  const apiRef = useGridApiRef()

  useEffect(() => {
    console.log(data)
  }, [])

  const columns = useMemo(() => {
    return data.gridColumns.map(({type, items, ...props}) => (
      {
        ...props,
        type,
        valueOptions: items
      }
    ))
  }, [data])

  // const rows = [
  //   {id: 1, col1: 'Test1', col2: 'TestA' },
  //   {id: 2, col1: 'Test2', col2: 'TestB' },
  //   {id: 3, col1: 'Test3', col2: 'TestC' },
  // ]

  // const columns = [
  //   { field: 'col1', headerName: 'Column1', width: 150, editable: true },
  //   { field: 'col2', headerName: 'Column2', width: 100 }
  // ]

  const append = () => {
    console.log(apiRef.current.getSortedRows())
    // setRows([ ...rows, {
    //   id: count,
    //   position_id: '',
    //   position_name: count,
    // }])
    setCount(count + 1)
  }

  const lotofappend = () => {
    const data = []
    for (let i = 1; i < 3; i++) {
      apiRef.current.updateRows([{
        id: 'abic-a222-aa-x-x-s-s--wa' + i,
        position_id: 'a' + i
      }])
    }
  }

  return {
    apiRef,
    columns,
    rows,
    append,
    lotofappend
  }
}

export default useTemplateDataEditor
