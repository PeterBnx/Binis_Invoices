import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './styles/index.css';
import '../assets/fonts/Manrope-Variable.ttf';
import {SocketMessageProvider} from './components/SocketMessageContext.tsx'




createRoot(document.getElementById('root')!).render(
    <SocketMessageProvider>
        <App />
    </SocketMessageProvider>
)
