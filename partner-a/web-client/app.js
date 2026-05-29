// The one place the client knows about the backend. No business logic here:
// the client only calls APIs and displays whatever the backend returns.
const API_BASE = "https://ia2iwtvws0.execute-api.us-east-1.amazonaws.com/prod";

const output = () => document.getElementById("output");

// Call the API and always show the raw backend response.
async function call(method, path, body) {
  try {
    const res = await fetch(API_BASE + path, {
      method,
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json();
    output().textContent = `HTTP ${res.status}\n` + JSON.stringify(data, null, 2);
    return { status: res.status, data };
  } catch (err) {
    output().textContent = "Request failed: " + err;
    return null;
  }
}

async function createOrder() {
  const price = parseFloat(document.getElementById("create-price").value);
  const description = document.getElementById("create-desc").value;
  await call("POST", "/orders", { price, description });
  getAllOrders();
}

async function getAllOrders() {
  const r = await call("GET", "/orders");
  if (!r || !Array.isArray(r.data)) return;
  const rows = r.data
    .map((o) => `<tr><td>${o.orderId}</td><td>${o.price}</td><td>${o.description}</td><td>${o.creationDate}</td></tr>`)
    .join("");
  document.getElementById("orders-table").innerHTML =
    `<table><tr><th>orderId</th><th>price</th><th>description</th><th>created</th></tr>${rows}</table>`;
}

async function getOrder() {
  const id = document.getElementById("get-id").value.trim();
  await call("GET", "/orders/" + id);
}

async function updateOrder() {
  const id = document.getElementById("upd-id").value.trim();
  const body = {};
  const price = document.getElementById("upd-price").value;
  const desc = document.getElementById("upd-desc").value;
  if (price !== "") body.price = parseFloat(price);
  if (desc !== "") body.description = desc;
  await call("PUT", "/orders/" + id, body);
}
