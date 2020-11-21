const { app, BrowserWindow, Menu } = require("electron");
const url = require("url");
const path = require("path");

let homeWindow;

const menuTemplate = [
    {
        label: "App",
        submenu: [
            { 
                label: "Quit", 
                accelerator: process.platform === "darwin" ? "Command+Q" : "Ctrl+Q",
                click(){ app.quit(); } 
            }
        ]
    },
    {
        label: "Debug",
        submenu: [
            {
                label: "Toggle Developer Tools",
                accelerator: process.platform === "darwin" ? "Command+I" : "Ctrl+I",
                click(item, window) {
                    window.toggleDevTools();
                }
            },
            {
                label: "Reload Program",
                accelerator: process.platform === "darwin" ? "Command+Shift+R" : "Ctrl+Shift+R",
                role: "reload"
            }
        ]
    }
];

function createWindow() {
    homeWindow = new BrowserWindow({
        width: 1280,
        height: 720,
        webPreferences: {
            nodeIntegration: true,
        }
    });
    homeWindow.loadURL(url.format({
        pathname: path.join(__dirname, "home.html"),
        protocol: "file:",
        slashes: true
    }));

    const mainMenu = Menu.buildFromTemplate(menuTemplate);
    Menu.setApplicationMenu(mainMenu);

    const python = require("child_process").spawn("python", ["../interface.py"]);
    python.stdout.on("data", function(data) {
        dataIn(data.toString());
    });
}

function dataIn(raw) {
    const data = raw.split(" _ ");
    switch (data[0]) {
        case "time":
            homeWindow.webContents.send("setTime", data[1]);
            break;
    }
}

app.on("ready", createWindow);

app.on("window-all-closed", () => {
    app.quit();
});