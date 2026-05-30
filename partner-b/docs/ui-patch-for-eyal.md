# UI Patch — Partner B sections missing from the web client
# Eyal: paste the HTML block into index.html before the closing </body> tag,
# and paste the JS block into app.js at the end of the file.

---

## HTML — paste before </body> in index.html

```html
  <section class="card">
    <h2>Delete order</h2>
    <input id="del-id" type="text" placeholder="orderId" />
    <button onclick="deleteOrder()">Delete</button>
  </section>

  <section class="card">
    <h2>Subscribe to notifications</h2>
    <input id="sub-email" type="email" placeholder="your@email.com" />
    <button onclick="subscribe()">Subscribe</button>
  </section>

  <section class="card">
    <h2>Unsubscribe from notifications</h2>
    <input id="unsub-email" type="email" placeholder="your@email.com" />
    <button onclick="unsubscribe()">Unsubscribe</button>
  </section>

  <section class="card">
    <h2>Download deleted orders PDF</h2>
    <button onclick="getPdfSummary()">Generate PDF report</button>
    <div id="pdf-link"></div>
  </section>

  <section class="card">
    <h2>System metrics (last 24h) — CloudWatch</h2>
    <button onclick="getMetrics()">Get metrics</button>
    <div id="metrics-display"></div>
  </section>
```

---

## JS — paste at the end of app.js

```javascript
async function deleteOrder() {
  const id = document.getElementById("del-id").value.trim();
  await call("DELETE", "/orders/" + id);
  getAllOrders();
}

async function subscribe() {
  const email = document.getElementById("sub-email").value.trim();
  await call("POST", "/subscriptions", { email });
}

async function unsubscribe() {
  const email = document.getElementById("unsub-email").value.trim();
  await call("DELETE", "/subscriptions", { email });
}

async function getPdfSummary() {
  const r = await call("GET", "/reports/deleted-orders");
  if (r && r.data && r.data.url) {
    document.getElementById("pdf-link").innerHTML =
      `<a href="${r.data.url}" target="_blank">Click here to download the PDF</a>`;
  }
}

async function getMetrics() {
  const r = await call("GET", "/metrics");
  if (r && r.data && r.data.metrics) {
    const m = r.data.metrics;
    document.getElementById("metrics-display").innerHTML = `
      <table>
        <tr><th>Action</th><th>Count (last 24h)</th></tr>
        <tr><td>Orders Created</td><td>${m.ordersCreated}</td></tr>
        <tr><td>Orders Deleted</td><td>${m.ordersDeleted}</td></tr>
        <tr><td>Orders Listed</td><td>${m.ordersListed}</td></tr>
        <tr><td>Orders Updated</td><td>${m.ordersUpdated}</td></tr>
      </table>`;
  }
}
```
