import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { motion } from 'framer-motion'
import Dashboard from './pages/Dashboard'
import Routers from './pages/Routers'
import Monitoring from './pages/Monitoring'
import Chat from './pages/Chat'
import Layout from './components/Layout'
import ChatWidget from './components/ChatWidget'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/routers" element={<Routers />} />
          <Route path="/monitoring" element={<Monitoring />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
        <ChatWidget />
      </Layout>
    </Router>
  )
}

export default App
