fetch("/menu")
  .then(response => response.json())
  .then(data => {
    const menuContainer = document.getElementById("menu");
    menuContainer.innerHTML = "";

    data.forEach(item => {
      const card = `
        <div class="card m-2 p-3" style="width: 200px;">
          <h5>${item.item_name}</h5>
          <p>₹${item.price}</p>
          <button class="btn btn-primary"
            onclick="placeOrder(${item.item_id})">
            Order
          </button>
        </div>
      `;
      menuContainer.innerHTML += card;
    });
  });

function placeOrder(itemId) {
  fetch("/order", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ item_id: itemId })
  })
  .then(res => res.json())
  .then(data => {
    const msgDiv = document.getElementById("order-message");

    if (data.success) {
      msgDiv.innerHTML = `
        <div class="alert alert-success">
          ${data.message} 😊 <br>
          <strong>Order ID:</strong> ${data.order_id}
        </div>
      `;
    } else {
      msgDiv.innerHTML = `
        <div class="alert alert-danger">
          Order failed ❌
        </div>
      `;
    }
  });
}


function loadOrders() {
  fetch("/my-orders")
    .then(res => res.json())
    .then(data => {
      const container = document.getElementById("orders-container");

      if (data.length === 0) {
        container.innerHTML = `
          <div class="alert alert-info">
            No orders found.
          </div>
        `;
        return;
      }

      let html = `
        <h4 class="mt-3">My Orders</h4>
        <table class="table table-bordered mt-2">
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Item</th>
              <th>Quantity</th>
              <th>Status</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
      `;

      data.forEach(order => {
        html += `
          <tr>
            <td>${order.order_id}</td>
            <td>${order.item_name}</td>
            <td>${order.quantity}</td>
            <td>${order.status}</td>
            <td>${order.order_time}</td>
          </tr>
        `;
      });

      html += "</tbody></table>";
      container.innerHTML = html;
    });
}
