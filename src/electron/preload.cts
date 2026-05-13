import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('api', {
  send: (channel: string, data: any) => {
    ipcRenderer.send(channel, data);
  },
  receive: (channel: string, func: (...args: any[]) => void) => {
    const subscription = (_event: Electron.IpcRendererEvent, ...args: any[]) => func(...args);
    ipcRenderer.on(channel, subscription);
    
    // Optional: return unsubscribe function
    return () => ipcRenderer.removeListener(channel, subscription);
  },
  invoke: (channel: string, data?: any) => {
    return ipcRenderer.invoke(channel, data);
    }
});
