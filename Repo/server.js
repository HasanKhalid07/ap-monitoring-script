const http = require("http");
const fs = require("fs");
const { exec } = require("child_process");

const PORT = 3000;

// ===== HTTP SERVER =====
http.createServer((req, res) => {

  // Serve dashboard
  if (req.url === "/") {
    fs.readFile("index.html", (err, data) => {
      res.writeHead(200, { "Content-Type": "text/html" });
      res.end(data);
    });
  }

  // Serve JSON data
  else if (req.url === "/data") {
    fs.readFile("ap_status.json", (err, data) => {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(data);
    });
  }

  // Run Python script manually
  else if (req.url === "/refresh") {
    exec("python collector.py");
    res.writeHead(200);
    res.end("Script started");
  }

  else {
    res.writeHead(404);
    res.end();
  }

}).listen(PORT, () => {
  console.log(`Dashboard running at http://localhost:${PORT}`);
});

// ===== AUTO RUN EVERY 1 MIN =====
setInterval(() => {
  exec("python collector.py");
  console.log("Collector script executed");
}, 60000);
