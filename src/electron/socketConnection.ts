// This File handles socket connection with python script
import { WebSocket, WebSocketServer } from 'ws';
import { getMainWindow } from './util.js';
import { spawn } from 'child_process';
import { getScriptsPath } from './pathResolver.js';
import path from 'path';

interface Connection {
  server: WebSocketServer | null;
  clients: Set<WebSocket>;
}

const connection: Connection = {
  server: null,
  clients: new Set(),
};

export function startServer(): boolean {
  try {
    if (connection.server) {
      console.log("Server already running");
      return true;
    }

    connection.server = new WebSocketServer({ port: 5555 });
    console.log("[socketConnection.ts] WebSocket server started on port 5555");

    connection.server.on("connection", (ws) => {
      connection.clients.add(ws);

      ws.on("message", (msg: Buffer) => {
        try {
          const decodedMsg = msg.toString('utf-8'); 
          const messageData = JSON.parse(decodedMsg);
          console.log("[socketConnection.ts] Received structured data:", messageData);

          getMainWindow()?.webContents.send("socket_message", messageData);
        } catch (e) {
          console.log(e);
          const rawMessage = msg.toString();
          getMainWindow()?.webContents.send("socket_message", rawMessage);
        }
      });
    });

    return true;
  } catch (e) {
    console.error("[socketConnection.ts] Failed to start WebSocket server:", e);
    return false;
  }
}

export function stopServer(): boolean {
  try {
    if (connection.server) {
      connection.server.close(() => {
        console.log("[socketConnection.ts] WebSocket server closed");
      });
      connection.server = null;
      connection.clients.clear();
    }
    return true;
  } catch (e) {
    console.error("[socketConnection.ts] Failed to stop WebSocket server:", e);
    return false;
  }
}


export function runPythonScript(scriptName: string, args: string[] = [], data = null) {
  const isProd = process.env.NODE_ENV === 'production';
  const exePath = isProd
    ? path.join(process.resourcesPath, 'bin', 'ipc.exe')
    : 'python';
  const spawnArgs = isProd 
    ? [...args] 
    : [path.join(getScriptsPath(), scriptName), ...args];

  const pythonProcess = spawn(exePath, spawnArgs, {
    env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
  });

  pythonProcess.stdout.setEncoding('utf8');
  
  if (data) {
    pythonProcess.stdin.write(JSON.stringify(data));
    pythonProcess.stdin.end();
  }
  
  console.log(`[PYTHON] Spawning executable: ${exePath} with args:`, spawnArgs);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`[PYTHON STDOUT]: ${data.toString('utf-8')}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`[PYTHON STDERR]: ${data.toString()}`);
  });

  pythonProcess.on('exit', (code) => {
    console.log(`[PYTHON] exited with code ${code}`);
  });
}