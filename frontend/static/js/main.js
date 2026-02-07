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
          <button class="btn btn-primary">Order</button>
        </div>
      `;
      menuContainer.innerHTML += card;
    });
  })
  .catch(error => console.error("Error loading menu:", error));
