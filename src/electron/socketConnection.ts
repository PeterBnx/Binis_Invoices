// This File handles socket connection with python script
import { WebSocket, WebSocketServer } from 'ws';
import { getMainWindow } from './util.js';
import { spawn } from 'child_process';
import { getScriptsPath } from './pathResolver.js';
import path from 'path';
import { app } from 'electron';

interface Connection {
  server: WebSocketServer | null;
  clients: Set<WebSocket>;
}

const connection: Connection = {
  server: null,
  clients: new Set(),
};

const envVars = {
  ...process.env,
  PLAYWRIGHT_BROWSERS_PATH: app.isPackaged 
    ? path.join(process.resourcesPath, 'ms-playwright')
    : path.join(app.getAppPath(), 'ms-playwright')
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
  const isPackaged = app.isPackaged;

  const exePath = isPackaged
    ? path.join(process.resourcesPath, 'bin', 'ipc.exe')
    : 'python';

  const spawnArgs = isPackaged 
    ? [...args] 
    : [path.join(getScriptsPath(), scriptName), ...args];

  console.log(`[PYTHON] Spawning target: ${exePath} with args:`, spawnArgs);

  const pythonProcess = spawn(exePath, spawnArgs, {
    env: { ...envVars, PYTHONIOENCODING: 'utf-8' }
  });

  pythonProcess.stdout.setEncoding('utf8');
  
  if (data) {
    pythonProcess.stdin.write(JSON.stringify(data));
    pythonProcess.stdin.end();
  }

  pythonProcess.stdout.on('data', (data) => {
    console.log(`[PYTHON STDOUT]: ${data.toString()}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`[PYTHON STDERR]: ${data.toString()}`);
  });

  pythonProcess.on('exit', (code) => {
    console.log(`[PYTHON] exited with code ${code}`);
  });
}