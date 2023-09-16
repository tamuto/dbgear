import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"

const useFillData = (columns: GridColumn[], fillData: (column: string, value: string) => void) => {
  const [open, setOpen] = useState(false)
  const { control, handleSubmit, watch } = useForm({
    defaultValues: {
      column: '',
      value: '',
    }
  })
  const column = watch('column')
  const [valueType, setValueType] = useState('text')
  const [items, setItems] = useState<ListItem[]>([])

  useEffect(() => {
    if (column) {
      const columnInfo = columns.find(x => x.field === column)
      if (columnInfo) {
        if (columnInfo.items) {
          setValueType('select')
          setItems(columnInfo.items)
        } else {
          setValueType('text')
          setItems([])
        }
      }
    }
  }, [columns, column])

  const onSubmit = handleSubmit((data) => {
    fillData(data.column, data.value)
    setOpen(false)
  })

  return {
    setOpen,
    open,
    control,
    onSubmit,
    valueType,
    items
  }
}

export default useFillData
