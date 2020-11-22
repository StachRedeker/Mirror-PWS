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
            change: results[1].toString().charAt(0) == "-" ? results[1] : "+" + results[1]
        };
        tickers.set(ticker, data);
        sortTickers();
    });
}

function removeTicker(ticker) {
    tickers.delete(ticker);
    sortTickers();
}

let selectedTicker = "";
$(".tickers").on("click", "div", function() {
    const tickerDiv = $(this);
    if(tickerDiv.hasClass("active")) {
        tickerDiv.removeClass("active");
        selectedTicker = "";
    } else {
        tickerDiv.addClass("active");
        if(selectedTicker != "")
            $("#" + selectedTicker).removeClass("active");

        selectedTicker = tickerDiv.attr("id");
    }
    updateInfo();
});

const tickers = new Map();
const pinnedTickers = ["TSLA"];
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
            content += `<div id="${ticker}" ${selectedTicker === ticker ? "class='active'" : ""}><span class="title">${data.title}</span><span class="pin"><button class="active" id="${data.ticker}"></button></span><span class="info">${data.change} | ${equalSpacing(data.ticker)}</span></div>`;
    });
    tickers.forEach((data, ticker) => {
        if(!pinnedTickers.includes(ticker)) {
            content += `<div id="${ticker}" ${selectedTicker === ticker ? "class='active'" : ""}><span class="title">${data.title}</span><span class="pin"><button id="${data.ticker}"></button></span><span class="info">${data.change} | ${equalSpacing(data.ticker)}</span></div>`;
        }
    });

    container.html(content);
}

let maxLength = 0;
function equalSpacing(input) {
    return "&nbsp;".repeat(maxLength - input.length) + input;
}

function updateInfo() {
    if(selectedTicker == "") {
        $(".main .info").html(`<div class="worth value">$0,00</div>
        <div class="converted">converted: <span class="value">€0,00</span></div>
        <div class="break"></div>
        <div class="status">Market Status: <span class="value">Unknown</span></div>
        
        <div class="local-time">
            <div class="header">Local Time:</div>
            <div class="data">
                <span class="date">?? ??? ????</span>
                <span class="time">??:?? (GMT-?)</span>
            </div>
        </div>`);
    } else {
        const ticker = selectedTicker;
        PythonShell.run('../detailed-ticker-info.py', {args: [ticker]},  function(err, results)  {
            if (err) throw err;
    
            console.log(results);

            const data = {
                title: results[0],
                ticker: ticker.toUpperCase(),
                value: results[1],
                symbol: results[2],
                converted: results[3],
                localDate: results[4],
                localTime: results[5],
                graphDate: results[6].split("|"),
                graphValue: results[7].split("|")
            };

            $(".main .info").html(`<div class="worth value">${data.symbol}${data.value}</div>
                <div class="converted">converted: <span class="value">€${data.converted}</span></div>
                <div class="break"></div>
                <div class="status">Market Status: <span class="value">Unknown</span></div>
                
                <div class="local-time">
                    <div class="header">Local Time:</div>
                    <div class="data">
                        <span class="date">${data.localDate}</span>
                        <span class="time">${data.localTime}</span>
                    </div>
                </div>`);

            chart.data = {
                labels: data.graphDate,
                datasets: [{
                    label: data.title,
                    borderColor: 'rgb(0, 200, 100)',
                    data: data.graphValue
                }]
            };
            chart.update();
        });
    }
}

updateInfo();
