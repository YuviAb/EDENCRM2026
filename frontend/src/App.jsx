import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import MainLayout    from './layouts/MainLayout'
import LoginPage     from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import ClientsPage   from './pages/ClientsPage'
import CalendarPage  from './pages/CalendarPage'
import PaymentsPage      from './pages/PaymentsPage'
import IntakeFormsPage    from './pages/IntakeFormsPage'
import ClientProfilePage  from './pages/ClientProfilePage'
import { authApi }   from './api/auth'

function RequireAuth({ children }) {
  if (!authApi.isAuthenticated()) {
    return <Navigate to="/login" replace />
  }
  return children
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <RequireAuth>
              <MainLayout />
            </RequireAuth>
          }
        >
          <Route index             element={<DashboardPage />} />
          <Route path="clients"   element={<ClientsPage />}   />
          <Route path="calendar"  element={<CalendarPage />}  />
          <Route path="payments"  element={<PaymentsPage />}  />
          <Route path="intake"            element={<IntakeFormsPage />} />
          <Route path="clients/:clientId" element={<ClientProfilePage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
