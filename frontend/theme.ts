import { createTheme } from '@mui/material'

const theme = createTheme({
  components: {
    MuiButton: {
      defaultProps: {
        variant: "contained"
      }
    },
    MuiButtonGroup: {
      defaultProps: {
        size: "small"
      }
    },
    MuiContainer: {
      defaultProps: {
        maxWidth: false
      }
    },
    MuiLink: {
      defaultProps: {
        underline: "hover"
      }
    },
    MuiList: {
      defaultProps: {
        dense: true
      }
    },
    MuiTextField: {
      defaultProps: {
        variant: "outlined",
        size: "small",
        margin: "none",
        fullWidth: true
      }
    },
    MuiToolbar: {
      defaultProps: {
        variant: "dense"
      }
    },
    MuiStack: {
      defaultProps: {
        spacing: 2
      }
    },
    MuiTable: {
      defaultProps: {
      }
    }
  }
})

export default theme
