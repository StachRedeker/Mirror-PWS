const electron = require("electron");
const ipc = electron.ipcRenderer;

const span = document.getElementById("msg");

ipc.on("setText", (_, text) => {
    console.log(text)
    span.innerHTML = text;
});
