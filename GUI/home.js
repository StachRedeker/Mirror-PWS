const electron = require("electron");
const ipc = electron.ipcRenderer;

const time = document.getElementsByClassName("time")[0].getElementsByClassName("value")[0];

ipc.on("setTime", (_, text) => {
    time.innerHTML = text;
});