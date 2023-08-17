import { css } from '@emotion/react'

const GlobalCss = css`
.MuiTableHead-root {
  background-color: #86ccce;
  .MuiTableCell-root {
    font-weight: bold;
  }
}

.MuiTableBody-root > .MuiTableRow-root:nth-of-type(odd) {
  background-color: #f5f5f5;
}

.MuiTableBody-root > .MuiTableRow-root.clickable {
  cursor: pointer;
}

.MuiTableBody-root > .MuiTableRow-root:hover {
  background-color: #eee;
}
`

export default GlobalCss
