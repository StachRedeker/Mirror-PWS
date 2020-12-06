const { ipcRenderer } = require("electron");
const fs = require("fs");
let { PythonShell } = require('python-shell');

// TODO: integrate AI (high prio, hard)
// TODO: live update day-graph if market is open (low prio, med)
// TODO: add indicators to graph (low prio, hard)

//#region Money/Balance
const EUR = new Intl.NumberFormat("en-UK", {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2
})

let balance = 0;
function setBal(bal) {
    if(bal > 10000000000000000)
        bal = 10000000000000000;

    balance = bal;
    $(".balance .value").html(EUR.format(balance));
}

function addBal(amount) {
    if(amount > 10000000000000000)
        amount = 10000000000000000;

    balance += parseFloat(amount);
    $(".balance .value").html(EUR.format(balance));
}

function removeBal(amount) {
    if(amount > 10000000000000000)
        amount = 10000000000000000;

    balance -= parseFloat(amount);
    $(".balance .value").html(EUR.format(balance));
}

setBal(0);
//#endregion

//#region Update Time
setInterval(() => {
    const date = new Date();
    $(".time .value").html(date.getHours() + ":" + (date.getMinutes() < 10 ? "0" : "") + date.getMinutes() + ":" + (date.getSeconds() < 10 ? "0" : "") +  date.getSeconds());
}, 1000);
//#endregion

//#region Config
let configData = {};

//Startup Initialization/Data Getting etc.
$(() => {
    showLoading();
    PythonShell.run('../GUI Scripts/setup.py', {}, function(err, results) {
        if (err) throw err;

        let out = [];
        results.forEach(ln => {
            const word = ln.split(" ")[1];
            if(word === "Package" || word === "Installed")
                out.push(ln);
        });

        console.log(out.join("\n"));
        hideLoading();
    });

    try {
        if(fs.existsSync("./config.json")) {
            fs.readFile("./config.json", (err, data) => {
                if(err) throw err;

                configData = JSON.parse(data);

                loadConfigData();
            });
        }
    } catch (err) {
        fs.writeFile("./config.json", "{}", (err) => {
            if(err) throw err;
            console.log("New config file created.");
        });
    }
});

function loadConfigData() {
    getConfig("tickers", "array").forEach(ticker => {
        addTicker(ticker);
    });

    pinnedTickers.push(...getConfig("pinned", "array"));
}

function setConfig(key, data) {
    configData[key] = data;
    fs.writeFileSync("./config.json", JSON.stringify(configData));
}

function getConfig(key, type) {
    if(type === "array") {
        return configData[key] == null ? [] : configData[key];
    } else {
        return configData[key];
    }
}
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
function encrypt(raw) {
    return raw.replace("^", "U2038").replace(".", "U002E").replace("=", "U003D");
}

function decrypt(raw) {
    return raw.replace("U2038", "^").replace("U002E", ".").replace("U003D", "=");
}

function addTicker(ticker) {
    ticker = encrypt(ticker);

    const options = {
        args: [ticker]
    }
    showLoading();
    PythonShell.run('../GUI Scripts/ticker-info.py', options,  function(err, results)  {
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

            setConfig("tickers", Array.from(tickers.keys()));
        }
    });
}

function removeTicker(ticker) {
    tickers.delete(ticker);
    sortTickers();

    setConfig("tickers", Array.from(tickers.keys()));
}

function sortTickers() {
    tickers.forEach((data, _) => {
        if(decrypt(data.ticker).length > maxLength)
            maxLength = decrypt(data.ticker).length;
    });

    const container = $(".side-bar .tickers");
    let content = "";

    pinnedTickers.forEach(ticker => {
        const data = tickers.get(ticker);
        if(data != undefined)
            content += `<div id="${ticker}" ${selectedTicker === ticker ? "class='active'" : ""}><span class="title">${data.title}</span><span class="more"><button></button></span><span class="pin"><button class="active" id="${data.ticker}-pin"></button></span><span class="info">${data.change} | ${equalSpacing(decrypt(data.ticker))}</span></div>`;
    });
    tickers.forEach((data, ticker) => {
        if(!pinnedTickers.includes(ticker)) {
            content += `<div id="${ticker}" ${selectedTicker === ticker ? "class='active'" : ""}><span class="title">${data.title}</span><span class="more"><button></button></span><span class="pin"><button id="${data.ticker}-pin"></button></span><span class="info">${data.change} | ${equalSpacing(decrypt(data.ticker))}</span></div>`;
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
            return;
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
        pinnedTickers.push(btn.attr("id").split("-")[0])
        btn.addClass("active");
    }

    setConfig("pinned", pinnedTickers);

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

//#region Info/Graph Section
let timeOffset;
let detailedGraphFetch;
let rangeData = new Map();
let rangeLabel = "";
let currentRange = "day";
let liveWorthInterval;
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
        clearInterval(liveWorthInterval);
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
        clearInterval(liveWorthInterval);
        const ticker = selectedTicker;
        showLoading();
        PythonShell.run('../GUI Scripts/detailed-ticker-info.py', {args: [ticker]},  function(err, results)  {
            if (err) throw err;

            const data = {
                title: results[0],
                ticker: decrypt(ticker).toUpperCase(),
                value: results[1],
                symbol: String.fromCharCode.apply(String, results[2].split("|")),
                converted: results[3],
                localDate: results[4],
                offset: parseInt(results[5]),
                graphDate: results[6],
                graphValue: results[7],
                graphSplits: results[8],
                graphDividends: results[9]
            };

            const dayData = sortGraphData(data.graphDate, data.graphValue, data.graphSplits, data.graphDividends)
            rangeData.set("day", dayData);
            rangeLabel = data.title;

            clearInterval(timeOffset);

            let marketOpen = false;
            timeOffset = setInterval(() => {
                const date = new Date();
                const time = date.getHours() - 1 + data.offset + ":" + (date.getMinutes() < 10 ? "0" : "") + date.getMinutes();

                if(isNaN(data.offset))
                    $(".local-time .data .time").html(`--:-- (EST-~)`);
                else
                    $(".local-time .data .time").html(`${time} (EST${data.offset >= 0 ? "+" + data.offset : data.offset})`);

                const lowRange = parseInt(data.graphDate.split("|")[0].split(":")[0] * 60 + data.graphDate.split("|")[0].split(":")[1]);
                const highRange = parseInt(data.graphDate.split("|").pop().split(":")[0] * 60 + data.graphDate.split("|").pop().split(":")[1]);
                const current = parseInt(time.split(":")[0] * 60 + time.split(":")[1]);
                marketOpen = (isNaN(data.offset) || (current >= lowRange && current <= highRange));
                $(".status").html(`Market Status: <span class="value ${marketOpen ? "open" : "closed"}">${marketOpen ? "Open&nbsp;&nbsp;" : "Closed"}`);
            }, 1000);

            $(".main .info").html(`<div class="worth value">${data.symbol}${data.value}</div>
                <div class="converted">${data.symbol !== "€" ? `converted: <span class="${data.value}">€${data.converted}</span>` : ""}</div>
                <div class="break"></div>
                <div class="status">Market Status: <span class="value closed">Closed</span></div>

                <div class="local-time">
                    <div class="header">Local Time:</div>
                    <div class="data">
                        <span class="date">${data.localDate}</span>
                        <span class="time">??:?? (EST-?)</span>
                    </div>
                </div>`);
            
            updateLiveWorth(data.ticker, data.symbol);

            chart.data = {
                labels: dayData[0],
                datasets: [{
                    label: rangeLabel,
                    borderColor: 'rgb(0, 200, 100)',
                    data: dayData[1],
                    backgroundColor: 'rgba(0, 100, 0, 0.1)'
                }, {
                    label: "Dividends",
                    borderColor: 'rgb(200, 200, 0)',
                    data: dayData[2],
                    backgroundColor: 'rgba(200, 200, 0, 0.2)'
                }, {
                    label: "No Data",
                    borderColor: 'rgb(200, 0, 0)',
                    data: dayData[3],
                    backgroundColor: 'rgba(200, 0, 0, 0.2)'
                }]
            };
            chart.update();

            loadFullGraphData(ticker);

            hideLoading();
        });
    }
}

function updateLiveWorth(ticker, symbol) {
    return;
    
    //FIXME: This errors out after a while, maybe due to too many requests? Not critical so I could just leave it disabled.

    if(liveWorthInterval != null)
        clearInterval(liveWorthInterval);
    
    liveWorthInterval = setInterval(() => {
        PythonShell.run('../GUI Scripts/get-ticker-worth.py', {args: [ticker]},  function(err, results)  {
            if(err) throw err;

            const worth = results[0];
            const converted = results[1];

            $(".info .worth .value").html(symbol + worth);
            $(".info .converted .value").html("€" + converted);
        });
    }, 1000);
}

function loadFullGraphData(ticker) {
    detailedGraphFetch = PythonShell.run('../GUI Scripts/full-ticker-graph-info.py', {args: [ticker]},  function(err, results) {
        if (err) throw err;

        const ranges = ["week", "month", "6months", "year", "max"];

        if(results == null)
            return;

        for (let i = 0; i < results.length; i += 4) {
            const range = ranges[i / 4];

            rangeData.set(range,  sortGraphData(results[i], results[i + 1], results[i + 2], results[i + 3]));
        }
    });
}

function sortGraphData(rawDates, rawValues, rawSplits, rawDividends) {
    const dateArray = rawDates.split("|");
    const valueArray = rawValues.split("|");
    const splitArray = rawSplits.split("|");
    const dividendsInput = rawDividends.split("|");
    const dividendsArray = [];
    const closedArray = [];

    for (let i = 0; i < valueArray.length; i++) {
        const value = valueArray[i]
        if(isNaN(value)) {
            if(parseFloat(splitArray[i]) !== 0) {
                for (let j = i; j > 0; j--) {
                    if(!isNaN(valueArray[j])) {
                        valueArray[i] = valueArray[j];
                        break;
                    }
                }
            } else if(parseFloat(dividendsInput[i]) !== 0) {
                if(!isNaN(valueArray[i - 1])) {
                    dividendsArray[i - 1] = valueArray[i - 1];
                }

                for (let j = i; j > 0; j--) {
                    if(!isNaN(valueArray[j])) {
                        dividendsArray[i] = valueArray[j];
                        break;
                    }
                }
            } else {
                if(!isNaN(valueArray[i - 1])) {
                    closedArray[i - 1] = valueArray[i - 1];
                }

                for (let j = i; j > 0; j--) {
                    if(!isNaN(valueArray[j])) {
                        closedArray[i] = valueArray[j];
                        break;
                    }
                }
            }
        } else if(i > 1 && isNaN(valueArray[i - 1])) {
            if(closedArray[i - 1] != null) {
                closedArray[i] = valueArray[i];
            } else if(dividendsArray[i - 1] != null) {
                dividendsArray[i] = valueArray[i];
            }
        }
    }

    return [dateArray, valueArray, dividendsArray, closedArray];
}

updateInfo();

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
                label: "Dividends",
                borderColor: 'rgb(200, 200, 0)',
                data: data[2],
                backgroundColor: 'rgba(200, 200, 0, 0.2)'
            }, {
                label: "No Data",
                borderColor: 'rgb(200, 0, 0)',
                data: data[3],
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
//#endregion

//#region Manual Input
// ticker = [value, invested money]
const tickersBought = new Map();

function removeMoneyFormatting(raw, amountOfDecimals) {
    const split = raw.split(".");
    let decimal = "";
    if(split[0] == null || split[0] == "")
        split[0] = "0";
    
    if(split[1] != null) {
        let i = split[1].length;
        while(i--) {
            if(split[1].charAt(i) !== "0") {
                decimal += split[1].slice(0, i + 1);
                break;
            }
        }
    }
    return split[0].match(/[\d]/g).join("") + (decimal == "" ? "" : "." + decimal.slice(0, amountOfDecimals));
}

$("#manual-input").on("input", function () {
    const input = $(this);

    if(input.val() != 0)
        input.val(input.val().match(/[\d,.]/g).join(""));
});

$("#manual-input").on("mouseenter", function () {
    const input = $(this);

    input.val(removeMoneyFormatting(input.val(), 2));
});

$("#manual-input").on("mouseleave", function () {
    const input = $(this);
    if(!input.is(":focus"))
        input.val(EUR.format(input.val()).match(/[\d,.]/g).join(""));
});

$("#manual-input").on("blur", function() {
    const input = $(this);
    if(input.val() != 0)
        input.val(EUR.format(input.val()).match(/[\d,.]/g).join(""));
});    

let liveInterval = null;
function updateLiveTickerProfit() {
    if(liveInterval != null)
        clearInterval(liveInterval);

    if(tickersBought.size > 0) {
        liveInterval = setInterval(() => {
            PythonShell.run('../GUI Scripts/get-multiple-ticker-worth.py', {args: [...tickersBought.keys()]},  function(err, results) {
                if (err) throw err;

                results.forEach(result => {
                    const ticker = result.split("|")[0];
                    const worth = result.split("|")[1];
                    const original = tickersBought.get(ticker);
                    tickersBought.set(ticker, [original[0], worth, original[2]]);
                    const delta = original[0] * worth - original[2];

                    let color = "";
                    if(delta >= 0.005)
                        color = "positive";
                    else if(delta <= -0.005)
                        color = "negative";

                    setTotal(ticker, `<p>${ticker}: ${sigTo4(original[0])}x (${EUR.format(original[0] * worth)} | <span class="${color}">${delta > 0 ? "+" : ""}${EUR.format(delta)}</span>)</p>`)
                });

                updateProfit();
            });
        }, 10000);
    } else {
        updateProfit();
    }
}

function updateProfit() {
    let profit = 0;
    tickersBought.forEach((data, ticker) => {
        profit += data[0] * data[1] - data[2];
    });
    $(".log .delta .value").html((profit > 0 ? "+" : "") + EUR.format(profit));
    if(profit >= 0.005) {
        $(".log .delta .value").addClass("positive");
        $(".log .delta .value").removeClass("negative");
    } else if(profit <= -0.005) {
        $(".log .delta .value").addClass("negative");
        $(".log .delta .value").removeClass("positive");
    } else {
        $(".log .delta .value").removeClass("negative");
        $(".log .delta .value").removeClass("positive");
    }
}

let manualErrQueue = 0;
$("#manual-err").hide();
$("#manual-buy").on("click", function() {
    const value = parseFloat(removeMoneyFormatting($("#manual-input").val(), 5));
    if(value < 0.0001) {
        $("#manual-err").html("Value must be atleast 0.0001");
        if(manualErrQueue <= 0)
            $("#manual-err").fadeIn(200);

        manualErrQueue++;
        setTimeout(() => {
            manualErrQueue--;
            if(manualErrQueue <= 0)
                $("#manual-err").fadeOut(200, () => $("#manual-err").html(""));
        }, 2000);
    } else if(value > balance) {
        const delta = Math.round((value - balance) * 100) / 100;
        $("#manual-err").html(`You cannot afford this transaction (missing ${EUR.format(delta)})`);
        if(manualErrQueue <= 0)
            $("#manual-err").fadeIn(200);

        manualErrQueue++;
        setTimeout(() => {
            manualErrQueue--;
            if(manualErrQueue <= 0)
                $("#manual-err").fadeOut(200, () => $("#manual-err").html(""));
        }, 2000);
    } else if(selectedTicker == "") {
        $("#manual-err").html(`You do not have a ticker selected`);
        if(manualErrQueue <= 0)
            $("#manual-err").fadeIn(200);

        manualErrQueue++;
        setTimeout(() => {
            manualErrQueue--;
            if(manualErrQueue <= 0)
                $("#manual-err").fadeOut(200, () => $("#manual-err").html(""));
        }, 2000);
    } else {
        removeBal(value);

        PythonShell.run('../GUI Scripts/get-ticker-worth.py', {args: [selectedTicker]},  function(err, results)  {
            if (err) throw err;

            // results[0] is the worth of the specified ticker
            const amount = value / results[0];

            if(tickersBought.has(selectedTicker)) {
                const original = tickersBought.get(selectedTicker);
                const current = original[0] * results[0];
                const total = current + parseFloat(value);

                tickersBought.set(selectedTicker, [total / results[0], results[0], total]);

                const delta = original[0] * results[0] - original[2];

                let color = "";
                if(delta >= 0.005)
                    color = "positive";
                else if(delta <= -0.005)
                    color = "negative";

                setTotal(selectedTicker, `<p>${selectedTicker}: ${sigTo4(total / results[0])}x (${EUR.format(total)} | <span class="${color}">${delta > 0 ? "+" : ""}${EUR.format(delta)}</span>)</p>`);
            } else {
                tickersBought.set(selectedTicker, [amount, results[0], value]);
                setTotal(selectedTicker, `<p>${selectedTicker}: ${sigTo4(amount)}x (${EUR.format(value)} | €0.00)</p>`);
            }

            addLog(`<p>Bought ${sigTo4(amount)}x ${selectedTicker} (<span class="negative">-${EUR.format(value)}</span>)</p>`);
            
            updateLiveTickerProfit();
        });
    }
});

$("#manual-sell").on("click", function() {
    const value = removeMoneyFormatting($("#manual-input").val(), 5);
    if(value < 0.0001) {
        manualErrQueue++;

        $("#manual-err").html("Value must be atleast 0.0001");
        if(queue <= 1)
            $("#manual-err").fadeIn(200);

        setTimeout(() => {
            manualErrQueue--;
            if(queue <= 0)
                $("#manual-err").fadeOut(200, () => $("#manual-err").html(""));
        }, 2000);
    } else if(selectedTicker == "") {
        $("#manual-err").html(`You do not have a ticker selected`);
        if(manualErrQueue <= 0)
            $("#manual-err").fadeIn(200);

        manualErrQueue++;
        setTimeout(() => {
            manualErrQueue--;
            if(manualErrQueue <= 0)
                $("#manual-err").fadeOut(200, () => $("#manual-err").html(""));
        }, 2000);
    } else {
        PythonShell.run('../GUI Scripts/get-ticker-worth.py', {args: [selectedTicker]},  function(err, results)  {
            if (err) throw err;

            // results[0] is the worth of the specified ticker
            const original = tickersBought.get(selectedTicker);
            const totalMoney = parseFloat(parseFloat(original[0]) * parseFloat(results[0] == null ? original[1] : results[0]));
            const correctedValue = value > totalMoney ? totalMoney : value;
            const amount = correctedValue / results[0];

            addLog(`<p>Sold ${sigTo4(amount)}x ${selectedTicker} (<span class="positive">+${EUR.format(correctedValue)}</span>)</p>`);

            if(correctedValue === totalMoney) {
                tickersBought.delete(selectedTicker);
                setTotal(selectedTicker, null);
            } else {
                const delta = (original[0] - amount) * results[0] - (original[2] - correctedValue);

                let color = "";
                if(delta >= 0.005)
                    color = "positive";
                else if(delta <= -0.005)
                    color = "negative";

                tickersBought.set(selectedTicker, [original[0] - amount, results[0], original[2] - correctedValue]);
                setTotal(selectedTicker, `<p>${selectedTicker}: ${sigTo4(original[0] - amount)}x (${EUR.format(original[2] - correctedValue)} | <span class="${color}">${delta > 0 ? "+" : ""}${EUR.format(delta)}</span>)</p>`);
            }


            updateLiveTickerProfit();

            addBal(correctedValue);
        });
    }
});

function sigTo4(input) {
    if(input >= 100) {
        return Math.round(input * 10) / 10;
    } else if(input >= 10) {
        return Math.round(input * 100) / 100;
    } else if(input >= 1) {
        return Math.round(input * 1000) / 1000;
    } else {
        return Math.round(input * 10000) / 10000;
    }
}
//#endregion

//#region Automatic

//#endregion

//#region Log
let mode = "change";

const changeLog = [];
function addLog(text) {
    changeLog.push(text);
    if(mode === "change") {
        $("#log-text").prepend(text);
        updateChangeLog();
    }
}

const totalLog = new Map();
function setTotal(key, value) {
    if(value == null)
        totalLog.delete(key);
    else
        totalLog.set(key, value);

    if(mode === "total")
        updateTotalLog();
}

function updateChangeLog() {
    $("#log-text").html("");
    changeLog.forEach(key => {
        $("#log-text").prepend(key);
    });
}

function updateTotalLog() {
    $("#log-text").html("");
    totalLog.forEach((value, key) => {
        $("#log-text").prepend(value);
    });
}

$(".log .log-setting").on("click", function() {
    const btn = $(this);
    if(btn.hasClass("active"))
        return;
    
    $("#" + mode).removeClass("active");
    $(this).addClass("active");
    mode = btn.attr("id");

    if(mode === "change")
        updateChangeLog();
    else if(mode === "total")
        updateTotalLog();
});
//#endregion

//#region Top Bar
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

        elem.innerHTML = `<input class="dropdown-change-balance" id="change-bal" value="0.00"/><button class="img" id="confirm-change-bal"></button>`;

        $(".container").append(elem);
        activeDropdowns.set("change-bal", elem);

        $("#change-bal").focus();
    }
});

$(".container").on("click", "#confirm-change-bal", function() {
    setBal(Number($("#change-bal").val()));

    if(activeDropdowns.has("change-bal")) {
        activeDropdowns.get("change-bal").remove();
        activeDropdowns.delete("change-bal");
    }
});

$(".container").on("keypress", "#change-bal", function(e) {
    const keyCode = e.keyCode || e.which;
    if(keyCode == 13) {
        setBal(Number($("#change-bal").val()));

    if(activeDropdowns.has("change-bal")) {
        activeDropdowns.get("change-bal").remove();
        activeDropdowns.delete("change-bal");
    }
    }
});

$(".container").on("input", "#change-bal", function () {
    const input = $(this);

    if(input.val() != 0)
        input.val(input.val().match(/[\d,.]/g).join(""));
});

$(".container").on("mouseenter", "#change-bal", function () {
    const input = $(this);

    input.val(removeMoneyFormatting(input.val(), 2));
});

$(".container").on("mouseleave", "#change-bal", function () {
    const input = $(this);
    if(!input.is(":focus"))
        input.val(EUR.format(input.val()).match(/[\d,.]/g).join(""));
});

$(".container").on("blur", "#change-bal", function() {
    const input = $(this);
    if(input.val() != 0)
        input.val(EUR.format(input.val()).match(/[\d,.]/g).join(""));
});  
//#endregion

$("#quit").on("click", function() {
    ipcRenderer.send("request-quit");
});

//#region Load Popup
let queue = 0;
let anim; let animStage = 0;
function showLoading() {
    queue++;

    if(queue <= 1) {
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
}

function hideLoading() {
    queue--;

    if(queue <= 0) {
        $("#load-popup").removeClass("active");
        clearInterval(anim);
    }
}
//#endregion
