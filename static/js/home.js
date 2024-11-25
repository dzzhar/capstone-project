function formatCurrency(amount) {
  return "Rp. " + amount.toLocaleString("id-ID");
}

function updateTotals() {
  const cartItems = document.querySelectorAll(".cart-item");
  let subtotal = 0;

  cartItems.forEach((item) => {
    const price = parseFloat(item.dataset.harga) || 0;
    const quantity =
      parseInt(item.querySelector(".jumlah-item").textContent) || 0;
    const itemTotal = price * quantity;

    item.querySelector(".harga-item").textContent = formatCurrency(itemTotal);
    subtotal += itemTotal;
  });

  document.getElementById("total").textContent = formatCurrency(subtotal);
}

document.querySelectorAll(".cart-item").forEach((item) => {
  const minusBtn = item.querySelector(".minus-btn");
  const plusBtn = item.querySelector(".plus-btn");
  const jumlahItem = item.querySelector(".jumlah-item");

  minusBtn.addEventListener("click", () => {
    let quantity = parseInt(jumlahItem.textContent) || 0;
    if (quantity > 1) {
      jumlahItem.textContent = quantity - 1;
      updateTotals();
    }
  });

  plusBtn.addEventListener("click", () => {
    let quantity = parseInt(jumlahItem.textContent) || 0;
    jumlahItem.textContent = quantity + 1;
    updateTotals();
  });
});

document.querySelectorAll(".hapus-item").forEach((button) => {
  button.addEventListener("click", function () {
    const item = this.closest(".cart-item");
    item.remove();
    updateTotals();
  });
});

document
  .getElementById("whatsappOrder")
  .addEventListener("click", function (e) {
    e.preventDefault();

    const cartItems = document.querySelectorAll(".cart-item");
    let message = "Halo, saya ingin memesan:\n";
    let subtotal = 0;

    cartItems.forEach((item) => {
      const name = item.querySelector("h5").textContent.trim();
      const price = parseFloat(item.dataset.harga);
      const quantity =
        parseInt(item.querySelector(".jumlah-item").textContent) || 0;
      const itemTotal = price * quantity;

      message += `- ${name} (x${quantity}): ${formatCurrency(itemTotal)}\n`;
      subtotal += itemTotal;
    });

    const total = subtotal;

    message += `\nTotal: ${formatCurrency(total)}\n\nMohon konfirmasi.`;

    const phoneNumber = "628997626200";
    const whatsappUrl = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(
      message
    )}`;
    window.open(whatsappUrl, "_blank");
  });
