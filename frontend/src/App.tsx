import { BrowserRouter } from 'react-router-dom'

import { DashboardRoutes } from './routes'

function App() {
  return (
    <BrowserRouter>
      <DashboardRoutes />
    </BrowserRouter>
  )
}

export default App
