import React, { useState } from 'react'
import axios from 'axios'
import {
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField
} from '@mui/material'

const ProjectEntryForm = ({ open, closeHandler }) => {
  const [value, setValue] = useState('')

  const changeHandler = (e) => {
    setValue(e.target.value)
  }

  const clickHandler = async () =>{
    console.log(value)
    await axios.put(`/data/prjinfo/${value}`, {test:'abc'})
    closeHandler()
  }

  return (
    <>
      <Dialog open={open}>
        <DialogTitle>Subscribe</DialogTitle>
        <DialogContent>
          <TextField
            label="project name"
            value={value}
            onChange={changeHandler}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={closeHandler}>Cancel</Button>
          <Button onClick={clickHandler}>Subscribe</Button>
        </DialogActions>
      </Dialog>
    </>

  )
}
export default ProjectEntryForm