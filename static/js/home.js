$(document).ready(function () {
  $("#togglePassword").on("click", function () {
    const passwordInput = $("#password");
    const passwordIcon = $("#passwordToggleIcon");

    if (passwordInput.attr("type") === "password") {
      passwordInput.attr("type", "text"); // Show password
      passwordIcon.removeClass("fa-eye").addClass("fa-eye-slash"); // Change icon to eye-slash
    } else {
      passwordInput.attr("type", "password"); // Hide password
      passwordIcon.removeClass("fa-eye-slash").addClass("fa-eye"); // Change icon to eye
    }
  });

  $("#toggleConfirmPassword").on("click", function () {
    const confirmPasswordInput = $("#confirm_password");
    const confirmPasswordIcon = $("#confirmPasswordToggleIcon");

    if (confirmPasswordInput.attr("type") === "password") {
      confirmPasswordInput.attr("type", "text"); // Show confirm password
      confirmPasswordIcon.removeClass("fa-eye").addClass("fa-eye-slash"); // Change icon to eye-slash
    } else {
      confirmPasswordInput.attr("type", "password"); // Hide confirm password
      confirmPasswordIcon.removeClass("fa-eye-slash").addClass("fa-eye"); // Change icon to eye
    }
  });
});

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

    // Update harga per item
    item.querySelector(".harga-item").textContent = formatCurrency(itemTotal);
    subtotal += itemTotal;
  });

  // Update subtotal (Grand Total)
  document.getElementById("total").textContent = formatCurrency(subtotal);
}

// Tambahkan event listener untuk tombol plus, minus, dan hapus item
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

// Hitung ulang total saat halaman dimuat
document.addEventListener("DOMContentLoaded", updateTotals);

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
