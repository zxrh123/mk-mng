import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { Toaster } from 'react-hot-toast'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
    <Toaster 
      position="top-left"
      toastOptions={{
        duration: 4000,
        style: {
          background: '#1a1a2e',
          color: '#00d9ff',
          border: '1px solid #00d9ff',
          fontFamily: 'Cairo, sans-serif',
        },
      }}
    />
  </React.StrictMode>,
)
