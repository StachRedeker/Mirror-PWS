const { app, BrowserWindow, Menu, ipcMain } = require("electron");
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
}

app.on("ready", createWindow);

app.on("window-all-closed", () => {
    app.quit();
});

ipcMain.on("request-quit", () => {
    app.quit();
});