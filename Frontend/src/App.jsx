import { useState } from 'react'
import JDCVMatcher from './pages/home'
import './index.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <JDCVMatcher/>
  )
}

export default App
