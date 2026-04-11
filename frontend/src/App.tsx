import { CssBaseline, ThemeProvider, createTheme } from '@mui/material'
import BoardView from './components/BoardView'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#0052cc' },
    background: { default: '#0079bf' },
  },
})

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline/>
      <BoardView/>
    </ThemeProvider>
  )
}