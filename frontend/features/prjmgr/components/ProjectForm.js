import React, { useState } from 'react'

import { Button } from '@mui/material'

import ProjectEntryForm from './ProjectEntryForm'

const ProjectForm = () => {
  const [value, setValue] = useState(false)

  const clickHandler = () => {
    setValue(true)
  }

  const closeHandler = () =>{
    setValue(false)
  }

  return (
    <>
      <Button variant="contained" onClick={clickHandler}>New</Button>
      <ProjectEntryForm open={value} closeHandler={closeHandler} />
    </>
  )
}

export default ProjectForm