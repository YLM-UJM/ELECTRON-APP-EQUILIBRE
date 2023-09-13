// preload.js

const { contextBridge, ipcRenderer } = require('electron');
// const fs = require('fs');

contextBridge.exposeInMainWorld(
  "api", {
    send: (channel, data) => {
      // whitelist channels
      let validChannels = ["toMain"];
      if (validChannels.includes(channel)) {
        ipcRenderer.send(channel, data);
      }
    },
    receive: (channel, func) => {
      let validChannels = ["fromMain"];
      if (validChannels.includes(channel)) {
        // Deliberately strip event as it includes `sender` 
        ipcRenderer.on(channel, (event, ...args) => func(...args));
      }
    },
    loadScript: (src) => {
      return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
      });
    },
    removeAllListeners: (channel) => {
      let validChannels = ["fromMain"];
      if (validChannels.includes(channel)) {
        ipcRenderer.removeAllListeners(channel);
      }
    },
    //chart: Chart.chart
  //   lireJSON: (chemin) => {
  //     return new Promise((resolve, reject) => {
  //         fs.readFile(chemin, 'utf8', (err, data) => {
  //             if (err) {
  //                 reject(err);
  //             } else {
  //                 resolve(JSON.parse(data));
  //             }
  //         });
  //     });
  // },
  }
);
// All the Node.js APIs are available in the preload process.
// It has the same sandbox as a Chrome extension.
window.addEventListener('DOMContentLoaded', () => {
    const replaceText = (selector, text) => {
      const element = document.getElementById(selector)
      if (element) element.innerText = text
    }
  
    for (const dependency of ['chrome', 'node', 'electron']) {
      replaceText(`${dependency}-version`, process.versions[dependency])
    }
  })