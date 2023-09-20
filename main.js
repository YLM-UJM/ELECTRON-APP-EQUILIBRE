// main.js

// Modules to control application life and create native browser window
const { app, BrowserWindow, ipcMain } = require('electron')
const path = require('path')
const WebSocket = require('ws');
const mysql = require('mysql');
const MySQLEvents = require('@rodrigogs/mysql-events');
require('dotenv').config();

// Initiliser Websocket
let wss;
let ws;
let mainWindow;


const createWindow = () => {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 1024,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true, // Assurez-vous que contextIsolation est activé
      enableRemoteModule: true,
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
  db = connectDb();
  initMySQLListener(db);

  

  // Connexion websocket
  wss = new WebSocket.Server({ port: 8080 });

  // Gestion Websocket 
  wss.on('connection', (websocket) => {
    console.log('Client connected');

    ws = websocket;
    ws.on('message', (message) => {
      const jsonObject = JSON.parse(message);
      const formattedJson = JSON.stringify(jsonObject, null, 2); // Indente avec 2 espaces
      console.log(formattedJson);
      if (jsonObject.topic == 'fromPython') {
        mainWindow.webContents.send('fromMain', jsonObject); 
        if (jsonObject.status == 'onPlateform') {
          payload = {
            'topic': 'toPython',
            'status': 'start',
            'essai': 0
        }
        ws.send(JSON.stringify(payload));
        }

      }
    });
    
    payload = {
      'topic': 'toPython',
      'status': 'Welcome to the WebSocket server!'
    }
    
    //ws.send(JSON.stringify(payload));

  
  });

 


  // Pour écouter les messages de l'interface utilisateur et y répondre
  ipcMain.on('toMain', (event, data) => {
    //console.log(data);

    // Receive refresh from index.js
    // if (data.topic == 'refresh') {
    //   mainWindow.webContents.send('fromMain',payloadHome)
    // }

    if (data.topic == 'get-users') {
      console.log('get User')
      getUsers(db,event);
      getConfig(db);
    }
    else if (data.topic == 'user-selected') {
      //console.log('idUser : ',data.message)
    }

    if (data.topic == 'toPython') {
        ws.send(JSON.stringify(data));
        console.log(data)
    }

    if (data.topic == 'get-config') {

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

function connectDb() {
  // Se connecter à la base de données 
  const db = mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_NAME,
    port: process.env.DB_PORT
});

db.connect(function(err) {
  if (err) {
      console.error('Erreur de connexion : ' + err.stack);
      return;
  }
  console.log('Connecté avec l\'ID ' + db.threadId);
});
return db;
}

function getUsers(db) {
  db.query('SELECT id, prenom FROM user ORDER BY id DESC', (error, results, fields) => {
    if (error) {
      return console.error(error.message);
    }
    console.log('retunr user')
    mainWindow.webContents.send('fromMain', { type: 'get-users-reply', data: results });
  });
}

function initMySQLListener(db) {
  const program = async () => {
    const instance = new MySQLEvents(db, {
      serverId:2,
      startAtEnd: true, // Commencez à écouter les événements à partir de la position actuelle du binlog
      excludedSchemas: {
        mysql: true,
      },
    });

    await instance.start();

    instance.addTrigger({
      name: 'User Change Listener',
      expression: 'selfit_station.user.*', // Écoutez tous les événements sur la table 'user' dans votre base de données
      statement: MySQLEvents.STATEMENTS.ALL, // Écoutez toutes les opérations DML (INSERT, UPDATE, DELETE)
      onEvent: (event) => { // Doit traiter l'événement
        console.log(event); // Affichez l'événement pour le débogage

        getUsers(db); // Mettez à jour la liste des utilisateurs
      },
    });

    instance.addTrigger({
      name: 'User Change Listener',
      expression: 'selfit_station.config.*', // Écoutez tous les événements sur la table 'user' dans votre base de données
      statement: MySQLEvents.STATEMENTS.ALL, // Écoutez toutes les opérations DML (INSERT, UPDATE, DELETE)
      onEvent: (event) => { // Doit traiter l'événement
        console.log(event); // Affichez l'événement pour le débogage
        getConfig(db);
      },
    });

    instance.on(MySQLEvents.EVENTS.CONNECTION_ERROR, console.error);
    instance.on(MySQLEvents.EVENTS.ZONGJI_ERROR, console.error);
  };

  program()
    .then()
    .catch(console.error);
}

function getConfig(db) {
  db.query('SELECT durationRestStability FROM config LIMIT 1', (error, results, fields) => {
    if (error) {
      return console.error(error.message);
    }
    mainWindow.webContents.send('fromMain', { topic: 'config', data: results });
  });
}