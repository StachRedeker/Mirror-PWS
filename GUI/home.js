const { app, ipcRenderer } = require("electron");
const electron = require("electron");
const ipc = electron.ipcRenderer;
const fs = require("fs");
let { PythonShell } = require('python-shell')

//TODO: Add pinned to config

//#region Money/Balance
const EUR = new Intl.NumberFormat("en-UK", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2
})

let balance = 0;
function setBal(bal) {
    balance = bal;
    $(".balance .value").html(EUR.format(bal));
}

setBal(0);
//#endregion

//#region Update Time
setInterval(() => {
    const date = new Date();
    $(".time .value").html(date.getHours() + ":" + (date.getMinutes() < 10 ? "0" : "") + date.getMinutes() + ":" + (date.getSeconds() < 10 ? "0" : "") +  date.getSeconds());
}, 1000);
//#endregion

//#region Initialize Chart
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
//#endregion

//#region Tickers General
//Load tickers from config
$(() => {
    try {
        if(fs.existsSync("./config.json")) {
            fs.readFile("./config.json", (err, data) => {
                if(err) throw err;
                const config = JSON.parse(data);
                config["tickers"].forEach(ticker => {
                    addTicker(ticker);
                });
            });
        }
    } catch (err) {
        fs.writeFile("./config.json", "{}", (err) => {
            if(err) throw err;
            console.log("New config file created.");
        });
    }
});

function addTicker(ticker) {
    const options = {
        args: [ticker]
    }
    showLoading();
    PythonShell.run('../ticker-info.py', options,  function(err, results)  {
        if (err) {
            console.log(err);
            sortTickers();
            hideLoading();
        } else {
            const data = {
                title: results[0],
                ticker: ticker.toUpperCase(),
                change: results[1].toString().charAt(0) == "-" ? results[1] : "+" + results[1]
            };
            tickers.set(ticker, data);
            sortTickers();
    
            hideLoading();

            const config = { tickers: Array.from(tickers.keys()) };
            fs.writeFileSync("./config.json", JSON.stringify(config));
        }
    });
}

function removeTicker(ticker) {
    tickers.delete(ticker);
    sortTickers();

    const config = { tickers: Array.from(tickers.keys()) };
    fs.writeFileSync("./config.json", JSON.stringify(config));
}

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
            content += `<img id="${ticker}" ${selectedTicker === ticker ? "class='active'" : ""}><span class="title">${data.title}</span><span class="more"><button></button></span><span class="pin"><button class="active" id="${data.ticker}"></button></span><span class="info">${data.change} | ${equalSpacing(data.ticker)}</span></img>`;
    });
    tickers.forEach((data, ticker) => {
        if(!pinnedTickers.includes(ticker)) {
            content += `<div id="${ticker}" ${selectedTicker === ticker ? "class='active'" : ""}><span class="title">${data.title}</span><span class="more"><button></button></span><span class="pin"><button id="${data.ticker}"></button></span><span class="info">${data.change} | ${equalSpacing(data.ticker)}</span></div>`;
        }
    });

    container.html(content);
}

let maxLength = 0;
function equalSpacing(input) {
    return "&nbsp;".repeat(maxLength - input.length) + input;
}

$("#addTicker").on("click", () => {
    const input = $("#ticker-input");
    addTicker(input.val());
    input.val("");
});

$("#ticker-input").on("keypress", function(e) {
    const keyCode = e.keyCode || e.which;
    if(keyCode == 13) {
        addTicker($(this).val());
        $(this).val("");
    }
});
//#endregion

//#region Tickers Interaction
let overlapQueue = 0;
let selectedTicker = "";
$(".tickers").on("click", "div", function() {
    setTimeout(() => {
        if(overlapQueue > 0)
            return;

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
    }, 100);
});

const tickers = new Map();
const pinnedTickers = [];
$(".tickers").on("click", ".pin button", function() {
    overlapQueue++;
    setTimeout(() => {
        overlapQueue--;
    }, 200);

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

const activeDropdowns = new Map();
$(".tickers").on("click", ".more button", function() {
    overlapQueue++;
    setTimeout(() => {
        overlapQueue--;
    }, 200);

    const ticker = $(this).parent().parent().attr("id");
    if(activeDropdowns.has(ticker)) {
        activeDropdowns.get(ticker).remove();
        activeDropdowns.delete(ticker);
    } else {
        const btn = $(this);
    
        let elem = document.createElement("div");
        elem.setAttribute("style", `
            position: absolute; 
            top: ${btn.position().top + btn.height()}px;
            left: ${btn.position().left}px;
            height: "max-content";
            width: "max-content";`);
        elem.setAttribute("class", "dropdown more");
        
        elem.innerHTML = `<div class="img"></div><button class="dropdown-more-button" id="${ticker}">Delete</button>`;
    
        $(".container").append(elem);
        activeDropdowns.set(ticker, elem);
    }
});

$(".container").on("click", ".dropdown-more-button", function() {
    removeTicker($(this).attr("id"));
    $(this).parent().remove();
});
//#endregion

//#region Info Section
let timeOffset;
let detailedGraphFetch;
let rangeData = new Map();
let rangeLabel = "";
let currentRange = "day";
function updateInfo() {
    rangeData.clear();
    rangeLabel = "";
    if(detailedGraphFetch != null) {
        detailedGraphFetch.childProcess.kill("SIGINT");
        detailedGraphFetch = null;
    }

    if(currentRange != "day") {
        $("#" + currentRange).removeClass("active");
        $("#day").addClass("active");
        currentRange = "day";
    }

    if(selectedTicker == "") {
        clearInterval(timeOffset);
        $(".main .info").html(`<div class="worth value">$0.00</div>
        <div class="converted">converted: <span class="value">€0.00</span></div>
        <div class="break"></div>
        <div class="status">Market Status: <span class="value">Unknown</span></div>
        
        <div class="local-time">
            <div class="header">Local Time:</div>
            <div class="data">
                <span class="date">?? ??? ????</span>
                <span class="time">??:?? (EST-?)</span>
            </div>
        </div>`);
    } else {
        const ticker = selectedTicker;
        showLoading();
        PythonShell.run('../detailed-ticker-info.py', {args: [ticker]},  function(err, results)  {
            if (err) throw err;
    
            const data = {
                title: results[0],
                ticker: ticker.toUpperCase(),
                value: results[1],
                symbol: results[2],
                converted: results[3],
                localDate: results[4],
                offset: parseInt(results[5]),
                graphDate: results[6].split("|"),
                graphValue: results[7].split("|")
            };

            rangeData.set("day", [data.graphDate, data.graphValue]);
            rangeLabel = data.title;

            clearInterval(timeOffset);

            timeOffset = setInterval(() => {
                const date = new Date();
                $(".local-time .data .time").html(`${date.getHours() - 1 + data.offset}:${(date.getMinutes() < 10 ? "0" : "") + date.getMinutes()} (EST${data.offset >= 0 ? "+" + data.offset : data.offset})`);
            }, 1000);


            $(".main .info").html(`<div class="worth value">${data.symbol}${data.value}</div>
                <div class="converted">converted: <span class="value">€${data.converted}</span></div>
                <div class="break"></div>
                <div class="status">Market Status: <span class="value ${(data.graphValue == null || isNaN(data.graphValue[data.graphValue.length - 1])) ? "closed" : "open"}">${(data.graphValue == null || isNaN(data.graphValue[data.graphValue.length - 1])) ? "Closed" : "Open&nbsp;&nbsp;"}</span></div>
                
                <div class="local-time">
                    <div class="header">Local Time:</div>
                    <div class="data">
                        <span class="date">${data.localDate}</span>
                        <span class="time">??:?? (EST-?)</span>
                    </div>
                </div>`);

            chart.data = {
                labels: data.graphDate,
                datasets: [{
                    label: data.title,
                    borderColor: 'rgb(0, 200, 100)',
                    data: data.graphValue,
                    backgroundColor: 'rgba(0, 100, 0, 0.1)'
                }]
            };
            chart.update();

            loadFullGraphData(ticker);

            hideLoading();
        });
    }
}

function loadFullGraphData(ticker) {
    detailedGraphFetch = PythonShell.run('../full-ticker-graph-info.py', {args: [ticker]},  function(err, results) {
        const ranges = ["week", "month", "6months", "year", "max"];
        
        if(results == null)
            return;
        
        for (let i = 0; i < results.length; i += 2) {
            const range = ranges[i / 2];
            const dateArray = results[i].split("|");
            const valueArray = results[i + 1].split("|");
            const closedArray = [];
        
            for (let i = 0; i < valueArray.length; i++) {
                const value = valueArray[i]
                if(isNaN(value)) {
                    if(!isNaN(valueArray[i - 1])) {
                        closedArray.pop();
                        closedArray.push(valueArray[i - 1]);
                    }

                    for (let j = i; j > 0; j--) {
                        if(!isNaN(valueArray[j])) {
                            closedArray.push(valueArray[j]);
                            break;
                        }
                    }

                    if(!isNaN(valueArray[i + 1])) {
                        closedArray.push(valueArray[i + 1]);
                    }
                } else {
                    closedArray.push(null);
                }
            }

            rangeData.set(range, [dateArray, valueArray, closedArray]);
        }
    });
}

updateInfo();
//#endregion

$(".select-range").on("click", "button", function() {
    const btn = $(this);
    if(!btn.hasClass("active")) {
        $("#" + currentRange).removeClass("active");
        currentRange = btn.attr("id");
        btn.addClass("active");
        changeRange(currentRange);
    }
});

function changeRange(range) {
    if(selectedTicker == "")
        return;

    if(rangeData.has(range)) {
        const data = rangeData.get(range);

        chart.data = {
            labels: data[0],
            datasets: [{
                label: rangeLabel,
                borderColor: 'rgb(0, 200, 100)',
                data: data[1],
                backgroundColor: 'rgba(0, 100, 0, 0.1)'
            }, {
                label: "Closed",
                borderColor: 'rgb(200, 0, 0)',
                data: data[2],
                backgroundColor: 'rgba(200, 0, 0, 0.2)'
            }]
        };
        chart.update();
    } else {
        showLoading();
        const load = setInterval(() => {
            if(rangeData.has(range)) {
                hideLoading();
                clearInterval(load);
                changeRange(range);
            }
        }, 500);
    }
}

$("#manual-input").on("input", function () {
    const input = $(this);
    input.val(input.val().match(/[\d,.]/g).join(""));
});

$("#manual-input").on("mouseenter", function () {
    const input = $(this);
    const split = input.val().split(".");
    let decimal = "";
    if(split[0] != null && split[1] != null) {
        let i = split[1].length;
        while(i--) {
            const char = split[1].charAt(i);
            if(char !== "0")
                decimal += split[1].slice(0, i + 1);
        }
    }
    input.val(split[0].match(/[\d]/g).join("") + (decimal == "" ? "" : "." + decimal.slice(0, 2)));
});

$("#manual-input").on("mouseleave", function () {
    const input = $(this);
    input.val(EUR.format(input.val()).match(/[\d,.]/g).join(""));
});

$(".top-bar .change-balance").on("click", "button", function() {
    if(activeDropdowns.has("change-bal")) {
        activeDropdowns.get("change-bal").remove();
        activeDropdowns.delete("change-bal");
    } else {
        const btn = $(this);
    
        let elem = document.createElement("div");
        elem.setAttribute("style", `
            position: absolute; 
            top: ${btn.position().top + btn.height()}px;
            left: ${btn.position().left}px;
            height: "max-content";
            width: "max-content";`);
        elem.setAttribute("class", "dropdown change-bal");
        
        elem.innerHTML = `<input class="dropdown-change-balance" id="change-bal"/><button class="img" id="confirm-change-bal"></button>`;
    
        $(".container").append(elem);
        activeDropdowns.set("change-bal", elem);
    }
});

$(".container").on("click", "#confirm-change-bal", function() {
    setBal(Number($("#change-bal").val()));

    if(activeDropdowns.has("change-bal")) {
        activeDropdowns.get("change-bal").remove();
        activeDropdowns.delete("change-bal");
    }
});

$("#quit").on("click", function() {
    ipcRenderer.send("request-quit");
});

//#region Load Popup
let queue = 0;
let anim; let animStage = 0;
function showLoading() {
    queue++;

    $("#load-popup").addClass("active");

    clearInterval(anim);
    anim = setInterval(function() {
        switch (animStage) {
            case 1:
                $("#loading-text").html("&nbsp;".repeat(3) + "Loading" + "&nbsp;".repeat(3));
                break;
            case 2:
                $("#loading-text").html("&nbsp;".repeat(3) + "Loading." + "&nbsp;".repeat(2));
                break;
            case 3:
                $("#loading-text").html("&nbsp;".repeat(3) + "Loading.." + "&nbsp;");
                break;
            default:
                $("#loading-text").html("&nbsp;".repeat(3) + "Loading...");
                break;
        }

        if(animStage < 3)
            animStage++;
        else
            animStage = 0;
    }, 500);
}

function hideLoading() {
    queue--;

    if(queue == 0) {
        $("#load-popup").removeClass("active");
        clearInterval(anim);
    }
}
//#endregion
