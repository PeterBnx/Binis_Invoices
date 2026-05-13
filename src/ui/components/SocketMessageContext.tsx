import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

interface MessageContextType {
  message: string | null;
}

const SocketMessageContext = createContext<MessageContextType | undefined>(undefined);

export function SocketMessageProvider({ children }: { children: ReactNode }) {
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    const handler = (msg: string) => setMessage(msg);
    window.api.receive('message_from_client', handler);
  }, []);

  return (
    <SocketMessageContext.Provider value={{ message }}>
      {children}
    </SocketMessageContext.Provider>
  );
}

export function useMessage() {
  const context = useContext(SocketMessageContext);
  if (!context) {
    throw new Error('useMessage must be used within a MessageProvider');
  }
  return context;
}
