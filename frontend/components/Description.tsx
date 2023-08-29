import { FC } from 'react'

type DescriptionProps = {
  value: string
}

const Description: FC<DescriptionProps> = ({ value }) => {
  return (
    <span dangerouslySetInnerHTML={{ __html: value }}></span>
  )
}

export default Description
