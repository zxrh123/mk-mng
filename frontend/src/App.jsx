import { Routes, Route } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Devices from './pages/Devices'
import ChatPage from './pages/ChatPage'
import Monitoring from './pages/Monitoring'
import Tasks from './pages/Tasks'

function App() {
  return (
    <AnimatePresence mode="wait">
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="devices" element={<Devices />} />
          <Route path="monitoring" element={<Monitoring />} />
          <Route path="tasks" element={<Tasks />} />
          <Route path="chat" element={<ChatPage />} />
        </Route>
      </Routes>
    </AnimatePresence>
  )
}

export default App
