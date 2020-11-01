const { app, BrowserWindow } = require("electron");
const url = require("url");
const path = require("path");

let homeWindow;

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

    const python = require("child_process").spawn("python", ["../test.py"]);
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