// main.js

// Modules to control application life and create native browser window
const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const WebSocket = require('ws');

// Initiliser Websocket
let wss;
let ws;

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false
    }
  })

  // and load the index.html of the app.
  mainWindow.loadFile('index.html')

  // Open the DevTools.
  // mainWindow.webContents.openDevTools()
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  createWindow();

  // Connexion websocket
  wss = new WebSocket.Server({ port: 8080 });

  // Gestion Websocket 
  wss.on('connection', (websocket) => {
    console.log('Client connected');
    ws = websocket;
    ws.on('message', (message) => {
      console.log(`Received message: ${message}`);
    });
    ws.send('Welcome to the WebSocket server!');
    
  });


  // Pour écouter les messages de l'interface utilisateur et y répondre
  ipcMain.on('toMain', (event, data) => {
    console.log(data);
    if (data.topic == 'test') {
      ws.send('start');
    }

  })


  app.on('activate', () => {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    wss.close()
    app.quit()
  } 
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.