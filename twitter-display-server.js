// HSM display server - displays logs collected by the Host Spot Monitor
// Setup all required packages
'use strict';
var express = require("express");
var bodyParser = require("body-parser");
var fs = require("fs");
var jsdom = require("jsdom");
var readLine = require("readline");
var WebSocketServer = require("ws").Server;
var WebSocket = require("ws")
var https = require("https");
var spawn = require("child_process").spawn;
var execSync = require("child_process").execSync;
// Read main html page - this will be parsed later
let mainPageContents = fs.readFileSync("./index.html");
// Read timeline html page - this will be parsed later
let timelinePageContents = fs.readFileSync("./timeline.html");
// Read log entry page - this will be reissued later
// create an express server to make a static file server
var app = express();
var relay = [];
var getPage = function (location, row, cell1, cell2, statusID, last, response, dom) {
    let client = new WebSocket("ws://localhost:3002");
    let totalMessage = "";
    client.on("open", function(error) {
        if (error) {
            console.log("error on connection open", error);
        } else {
            // send request to get embedded status messages
            client.send(new Uint8Array(("getEmbeddedStatus " + statusID).split("").map(function (char) {return char.charCodeAt(0);})));
        }
    });
    client.on("message", function(message) {
        //console.log("received:", message);
        totalMessage += message;
    });
    client.on("close", function(message) {
        console.log("connection closed", message);
        try {
            let embeddedStatus = JSON.parse(totalMessage);
            if (typeof embeddedStatus.html !== 'undefined') {
                //console.log("Embedded Status:", embeddedStatus, embeddedStatus.html);
                let embed = new jsdom.JSDOM(embeddedStatus.html);
                //console.log(embed.window.document.body.innerHTML);
                cell2.appendChild(embed.window.document.body);
            }
        } catch (err) {
            console.log("Embedded Status translation from JSON failed, doing nothing to cell 2, error:", err);
        }
        row.appendChild(cell1);
        row.appendChild(cell2);
        location.appendChild(row);
        if (last) {
            response.send(dom.serialize());
        }
    });
    
};

// if the express server is contacted, look at the request and build a response or
// forward the request to the standard server behavior.
app.get("/", function(request, response, next) {
    let client = new WebSocket("ws://localhost:3002");
    let totalMessage = "";
    client.on("open", function(error) {
        if (error) {
            console.log("error on connection open", error);
        } else {
            // send request to get screen names that are followed
            client.send(new Uint8Array(("".split("").map(function (char) {return char.charCodeAt(0);}))));
        }
    });
    client.on("message", function(message) {
        //console.log("received:", message);
        totalMessage += message;
    });
    client.on("close", function(message) {
        console.log("connection closed", message);
        let followingObject = ["Error - none found"];
        try {
            followingObject = JSON.parse(totalMessage);
        } catch (err) {
            console.log("Error trying to translate 'following' from JSON:", err);
        }
        //console.log(followingObject);
        let dom = new jsdom.JSDOM(mainPageContents);
        let document = dom.window.document;
        let insertionPoint = document.querySelector("#list");
        for (let screenName of followingObject) {
            let element = document.createElement("a");
            let ref = "screenName_" + screenName;
            element.setAttribute("href", ref);
            element.innerHTML = screenName;
            let listElement = document.createElement("li");
            listElement.appendChild(element);
            insertionPoint.appendChild(listElement);
        }
        response.send(dom.serialize());
    });
  });
app.get("/screenName_*", function(request, response, next) {
    console.log("process a timeline route");
    let screenName = request.url.replace("/screenName_","");
    let client = new WebSocket("ws://localhost:3002")
    let totalMessage = "";
    client.on("open", function(error) {
        if (error) {
            console.log("error on connection open", error);
        } else {
            // send request to get timeline of screen name
            client.send(new Uint8Array((screenName.split("").map(function (char) {return char.charCodeAt(0);}))));
        }
    });
    client.on("message", function(message) {
        totalMessage += message;
    });
    client.on("close", function(message) {
        console.log("connection closed", message);
        let timelineObject = [];
        try {
            timelineObject = JSON.parse(totalMessage);
        } catch (err) {
            console.log("Error trying to translate timeline from JSON:", err);
        }
        let dom = new jsdom.JSDOM(timelinePageContents);
        let document = dom.window.document;
        let insertionPoint = document.querySelector("#screenName");
        insertionPoint.innerHTML = screenName;
        insertionPoint = document.querySelector("#timeline");
        let size = timelineObject.length;
        let elementsProcessed = 0;
        let processedAtLeastOneTweet = false;
        for (let onePost of timelineObject.reverse()) {
            let date = new Date(onePost[0]);
            let diff = new Date() - date;
            console.log("time diff", diff);
            elementsProcessed++;
            if (diff > 24*2*3600*1000) {
                continue;
            }
            processedAtLeastOneTweet = true;
            let tableRow = document.createElement("tr");
            let tableCell1 = document.createElement("td");
            let tableCell2 = document.createElement("td");
            let tweet = onePost[1];
            if (tweet.slice(0, 2).search("RT") >= 0) {
                tweet = onePost[1].split(':')[0] + " <br>" + onePost[2];
            }
            let pat = /https:\S+/g;
            let matches = tweet.match(pat);
            tableCell1.innerHTML = onePost[0].split("+")[0];
            if (matches) {
                let didThisTarget = []
                for (let target of matches) {
                    if ( ! didThisTarget.includes(target)) {
                        tweet = tweet.replace(target, "<a href=" + target + ">🔗</a>");
                        didThisTarget.push(target);
                    }
                }
            }
            tableCell2.innerHTML = tweet;
            let statusID = onePost[onePost.length - 1];
            getPage(insertionPoint, tableRow, tableCell1, tableCell2, statusID, elementsProcessed==size, response, dom);
        }
        if (! processedAtLeastOneTweet) {
            response.send(dom.serialize());
        }
    });
  });
app.get("*", function(request, response, next) {
    console.log("fell into default get");
    console.log(request.url);
    console.log(request.method);
    next();
  });
app.use(bodyParser.urlencoded({extended: true}));
app.use(express.static("./"));
var ws = new WebSocketServer({server: app.listen(process.env.PORT || 2999)});

ws.on("connection", function(connection) {
    relay.push(connection); // store for communication
    console.log("web socket connection made at server from HTML client page");
    connection.send("connected");
    connection.on("message", function (message) {
        if (message === "exit") {
          relay.splice(relay.indexOf(connection), 1);
          connection.close();
        }
      });
    connection.on("close", function(message) {
        relay.splice(relay.indexOf(connection), 1);
        connection.close();
        console.log("closing a connection");
      });
  });

console.log("Twitter display server is listening");
