import React, { useState, useEffect } from 'react'
import axios from 'axios'

import {
  Button, 
  List,
  ListItemText
} from '@mui/material'

import ProjectEntryForm from './ProjectEntryForm'

const ProjectForm = () => {
  const [value, setValue] = useState(false)
  const [projects, setProjects] = useState([])

  const clickHandler = () => {
    setValue(true)
  }

  const closeHandler = () =>{
    setValue(false)
  }

  const _search = async () => {
    const result = await axios.get('/data/prjinfo/')
    console.log(result)
    setProjects(result.data)
  }

  useEffect(() => {
    _search()
  }, [value])

  return (
    <>
      <List>
        {
          projects.map((item, idx) => (
            <ListItemText key={idx} primary={item} />
          )) 
        }
      </List>
      <Button variant="contained" onClick={clickHandler}>New</Button>
      <ProjectEntryForm open={value} closeHandler={closeHandler} />
    </>
  )
}

export default ProjectForm