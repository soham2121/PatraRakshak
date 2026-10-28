import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource/mukta/400.css'
import '@fontsource/mukta/600.css'
import '@fontsource/mukta/800.css'
import './app.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
