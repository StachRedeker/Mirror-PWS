const electron = require("electron");
const { netLog } = require("electron/main");
const ipc = electron.ipcRenderer;
let { PythonShell } = require('python-shell')

const time = document.getElementsByClassName("time")[0].getElementsByClassName("value")[0];

ipc.on("setTime", (_, text) => {
    time.innerHTML = text;
});

const junkData = [[], []];
let last = 25;
for (let i = 0; i < 50; i++) {
    junkData[0][i] = i;
    const rand = Math.floor(Math.random() * 201);
    junkData[1][i] = (rand + last) / 2;
    last = rand;
}

const ctx = document.getElementById("chart").getContext("2d");
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: junkData[0],
        datasets: [{
            label: 'Alphabet',
            borderColor: 'rgb(0, 200, 100)',
            data: junkData[1]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        elements: {
            line: {
                tension: 0.1
            }
        }
    }
});

const tempTickers = ["TSLA", "UBER", "FB", "GOOG", "SU"];
$(() => {
    tempTickers.forEach(ticker => {
        addTicker(ticker);
    });

    $("#addTicker").on("click", function() {
        addTicker($("#ticker-input").val());
        $("#ticker-input").val("");
    });
});

function addTicker(ticker) {
    const options = {
        args: [ticker]
    }
    PythonShell.run('../ticker-info.py', options,  function(err, results)  {
        if (err) throw err;

        const data = {
            title: results[0],
            ticker: ticker.toUpperCase(),
            change: results[1]
        };
        tickers.set(ticker, data);
        sortTickers();
    });
    
}

function removeTicker(ticker) {
    tickers.delete(ticker);
    sortTickers();
}

const tickers = new Map();
const pinnedTickers = ["TSLA"];
const selectedTicker = "";
$(".tickers").on("click", ".pin button", function() {
    const btn = $(this);
    if(btn.hasClass("active")) {
        btn.removeClass("active");
        pinnedTickers.splice(pinnedTickers.indexOf(btn.attr("id")), 1);
    } else {
        pinnedTickers.push(btn.attr("id"))
        btn.addClass("active");
    }
    sortTickers();
});

function sortTickers() {
    tickers.forEach((data, _) => {
        if(data.ticker.length > maxLength)
            maxLength = data.ticker.length;
    });

    const container = $(".side-bar .tickers");
    let content = "";

    pinnedTickers.forEach(ticker => {
        const data = tickers.get(ticker);
        if(data != undefined)
            content += `<div ${selectedTicker === ticker ? "class='active'" : ""}><span class="title">${data.title}</span><span class="pin"><button class="active" id="${data.ticker}"></button></span><span class="info">${data.change} | ${equalSpacing(data.ticker)}</span></div>`;
    });
    tickers.forEach((data, ticker) => {
        if(!pinnedTickers.includes(ticker)) {
            content += `<div ${selectedTicker === ticker ? "class='active'" : ""}><span class="title">${data.title}</span><span class="pin"><button id="${data.ticker}"></button></span><span class="info">${data.change} | ${equalSpacing(data.ticker)}</span></div>`;
        }
    });

    container.html(content);
}

let maxLength = 0;
function equalSpacing(input) {
    return "&nbsp;".repeat(maxLength - input.length) + input;
}
