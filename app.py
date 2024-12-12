import hashlib
import os
from datetime import datetime, timedelta
from functools import wraps
from os.path import dirname, join

import jwt
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from pymongo import MongoClient
from werkzeug.utils import secure_filename

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)


MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")
SECRET_KEY = os.environ.get("SECRET_KEY")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)


# Konfigurasi untuk folder upload
UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}


# Memeriksa apakah file yang diupload memiliki ekstensi yang valid
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]
    )


# format rupiah
def format_idr(value):
    # Ensure value is treated as a number (float or int)
    value = float(value)
    return f"Rp. {value:,.0f}"


app.jinja_env.filters["format_idr"] = format_idr


# Rute untuk halaman utama
@app.route("/")
def home():
    # menyimpan token ke dalam mytoken
    token_receive = request.cookies.get("mytoken")
    user_info = None
    is_logged_in = False

    reviews = db.reviews.find({}, {"_id": False})

    if token_receive:
        try:
            # menggunakan jwt.decode untuk decode token
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"username": payload["id"]})
            is_logged_in = True  # Tandai pengguna sebagai login
        except jwt.ExpiredSignatureError:
            pass
        except jwt.exceptions.DecodeError:
            # Abaikan token tidak valid, tetap anggap pengguna tidak login
            pass

    # Render halaman utama dengan informasi login (jika ada)
    return render_template(
        "home/pages/home.html",
        is_logged_in=is_logged_in,
        user_info=user_info,
        reviews=reviews,
    )


# endpoint register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username_receive = request.form["username_give"]
        password_receive = request.form["password_give"]

        # periksa keunikan username
        if db.users.find_one({"username": username_receive}):
            return jsonify({"result": "failure", "msg": "Username already exists."})

        # hashing password
        hash_password = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

        new_user = {
            "username": username_receive,
            "password": hash_password,
            "role": "user",
        }

        # simpan user baru ke collection
        db.users.insert_one(new_user)

        return jsonify(
            {"result": "success", "msg": "You have successfully registered!"}
        )

    return render_template("home/pages/register.html")


# endpoint login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_receive = request.form["username_give"]
        password_receive = request.form["password_give"]

        hash_password = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

        user = db.users.find_one(
            {"username": username_receive, "password": hash_password}
        )

        if user:
            # membuat payload untuk token JWT
            payload = {
                "id": user["username"],
                "role": user["role"],  # Tambahkan role di payload
                "exp": datetime.utcnow() + timedelta(seconds=3000),
            }

            # encode JWT dengan SECRET_KEY
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            return jsonify({"result": "success", "token": token, "role": user["role"]})

        # jika username tidak ditemukan
        else:
            return jsonify({"result": "failure", "msg": "Could not find the user."})

    return render_template("home/pages/login.html")


# endpoint logout
@app.route("/logout")
def logout():
    response = redirect(url_for("login"))

    # menghapus cookies
    response.set_cookie("mytoken", "", expires=0)
    return response


@app.route("/products")
def products():
    token_receive = request.cookies.get("mytoken")
    user_info = None
    is_logged_in = False

    # Ambil data produk dari MongoDB
    products = list(db.products.find({}))
    for product in products:
        product["_id"] = str(product["_id"])  # Ubah ObjectId ke string

    if token_receive:
        try:
            # Decode token untuk mendapatkan informasi pengguna
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"username": payload["id"]})
            is_logged_in = True  # Tandai pengguna sebagai login
        except jwt.ExpiredSignatureError:
            pass
        except jwt.exceptions.DecodeError:
            pass

    # Render halaman produk dengan data login dan produk
    return render_template(
        "home/pages/products.html",
        is_logged_in=is_logged_in,
        user_info=user_info,
        products=products,
        username=user_info["username"] if user_info else None,
    )


# Rute untuk halaman produk
@app.route("/product/<id>")
def detail_product(id):
    token_receive = request.cookies.get("mytoken")
    user_info = None
    is_logged_in = False

    # mencari produk berdasarkan id
    product = db.products.find_one({"_id": ObjectId(id)})

    if token_receive:
        try:
            # Decode token untuk mendapatkan informasi pengguna
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
            user_info = db.users.find_one({"username": payload["id"]})
            is_logged_in = True  # Tandai pengguna sebagai login
        except jwt.ExpiredSignatureError:
            pass
        except jwt.exceptions.DecodeError:
            pass

    # Render halaman detail
    return render_template(
        "home/pages/detail_product.html",
        is_logged_in=is_logged_in,
        user_info=user_info,
        product=product,
    )


# Rute untuk menambah produk ke cart
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    token_receive = request.cookies.get("mytoken")
    if not token_receive:
        return redirect(url_for("login"))  # Redirect jika token tidak ada

    try:
        # Decode JWT untuk mendapatkan informasi pengguna
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        return redirect(url_for("login"))  # Redirect jika token invalid

    # Ambil `product_id` dari form
    product_id = request.form.get("product_id")
    if not product_id:
        return jsonify({"result": "failure", "msg": "Product ID is required."}), 400

    # Cari produk berdasarkan ID
    product = db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        return jsonify({"result": "failure", "msg": "Product not found."}), 404

    # Periksa apakah pengguna sudah memiliki keranjang
    user_cart = db.carts.find_one({"username": username})
    if not user_cart:
        # Jika tidak ada keranjang, buat keranjang baru
        new_cart = {
            "username": username,
            "items": [{"product_id": product_id, "quantity": 1}],
        }
        db.carts.insert_one(new_cart)
    else:
        # Jika sudah ada keranjang, perbarui
        items = user_cart.get("items", [])
        for item in items:
            if item["product_id"] == product_id:
                item["quantity"] += 1
                break
        else:
            # Tambahkan produk baru ke keranjang
            items.append({"product_id": product_id, "quantity": 1})
        db.carts.update_one({"username": username}, {"$set": {"items": items}})

    # Redirect ke halaman keranjang setelah sukses
    return jsonify({"result": "success", "msg": "Product added to cart."})


# endpoint cart
@app.route("/cart/<username>")
def cart(username):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        if username != payload["id"]:
            return redirect(url_for("login"))

        user_info = db.users.find_one({"username": username})
        user_cart = db.carts.find_one({"username": username})
        cart_items = []
        total_price = 0

        if user_cart and user_cart.get("items"):
            for item in user_cart["items"]:
                product = db.products.find_one({"_id": ObjectId(item["product_id"])})
                if product:
                    item_price = int(product["price"]) * int(item["quantity"])
                    total_price += item_price
                    cart_items.append(
                        {
                            "product_name": product["product_name"],
                            "price": product["price"],
                            "image": product["image"],
                            "quantity": item["quantity"],
                        }
                    )

        is_logged_in = True

        return render_template(
            "home/pages/cart.html",
            user_info=user_info,
            is_logged_in=is_logged_in,
            cart_items=cart_items,
            total_price=total_price,
        )

    except (jwt.ExpiredSignatureError, jwt.DecodeError):
        return redirect(url_for("login"))


# endpoint place order
@app.route("/place_order", methods=["POST"])
def place_order():
    data = request.get_json()

    # Validasi data
    if not data.get("name") or not data.get("address") or not data.get("products"):
        return (
            jsonify(
                {"status": "error", "message": "Nama, alamat, dan item harus diisi"}
            ),
            400,
        )

    try:
        # Buat data pesanan
        order = {
            "customer_name": data["name"],
            "customer_address": data["address"],
            "products": data["products"],
            "total_price": sum(
                item["price"] * item["quantity"] for item in data["products"]
            ),
            "status": "pending",  # Status default
            "created_at": datetime.utcnow(),
        }

        # Simpan ke database
        db.orders.insert_one(order)

        return (
            jsonify({"status": "success", "message": "Order created successfully"}),
            201,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# endpoint get order by username
@app.route("/order/<username>")
def order(username):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])

        # Pastikan username di URL cocok dengan ID di token
        if username != payload["id"]:
            return redirect(url_for("login"))

        user_info = db.users.find_one({"username": username})
        orders = db.orders.find_one({"username": username})

        if not orders:
            print(f"No order found for {username}")  # Debugging log

        return render_template(
            "home/pages/orders.html",
            user_info=user_info,
            is_logged_in=True,
            orders=orders,
        )

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


""" ------ DASHBOARD ADMIN SECTION ------ """


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("mytoken")
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if data.get("role") != "admin":
                return redirect("/")
        except jwt.ExpiredSignatureError:
            return redirect("/login")
        except jwt.InvalidTokenError:
            return redirect("/login")

        # ambil username dari session
        request.username = data.get("id")
        return f(*args, **kwargs)

    return decorated_function


# endpoint dashboard
@app.route("/admin")
@admin_required
def dashboard():
    total_users = db.users.count_documents({})
    total_products = db.products.count_documents({})
    total_orders = db.orders.count_documents({})
    total_keuntungan = 0

    orders_done = db.orders.find({"status": "done"})
    for order in orders_done:
        total_keuntungan += float(order.get("total_price", 0))

    return render_template(
        "admin/pages/dashboard.html",
        username=request.username,
        total_keuntungan=total_keuntungan,
        total_users=total_users,
        total_orders=total_orders,
        total_products=total_products,
    )


# endpoint dashboard table users
@app.route("/admin/users")
@admin_required
def users_table():
    # mengambil semua data users
    users_list = list(db.users.find({}))

    # mengirim tabel pengguna
    return render_template(
        "admin/pages/users.html",
        users=users_list,
        username=request.username,
    )


# endpoint dashboard create users
@app.route("/admin/user/create", methods=["GET", "POST"])
@admin_required
def create_user():
    # permintaan menggunakan method POST
    if request.method == "POST":
        # mengambil beberapa data dari form
        username_receive = request.form["username_give"]
        password_receive = request.form["password_give"]
        role_receive = request.form["role_give"]

        hash_password = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()

        # periksa keunikan username
        if db.users.find_one({"username": username_receive}):
            return jsonify({"result": "failure", "msg": "Username already exists."})

        # membuat doc untuk penyimpanan database
        doc = {
            "username": username_receive,
            "password": hash_password,
            "role": role_receive,
        }
        db.users.insert_one(doc)

        return jsonify({"result": "success", "msg": "Data User Successfully Added!"})

    # merender ke halaman create user
    return render_template(
        "admin/pages/create_user.html",
        username=request.username,
    )


# endpoint dashboard edit users
@app.route("/admin/user/edit/<id>", methods=["GET", "POST"])
@admin_required
def edit_user(id):
    # permintaan menggunakan method GET
    if request.method == "GET":
        # mengambil data user berdasarkan id
        user_id = db.users.find_one({"_id": ObjectId(id)})

        # render ke halaman edit user dengan id user
        return render_template(
            "admin/pages/edit_user.html", user=user_id, username=request.username
        )

    # permintaan menggunakan method POST
    if request.method == "POST":
        # mengambil data dari form edit
        username_receive = request.form["username_give"]
        password_receive = request.form["password_give"]
        role_receive = request.form["role_give"]

        # memperbarui dokumen user di database
        db.users.update_one(
            {"_id": ObjectId(id)},
            {
                "$set": {
                    "username": username_receive,
                    "password": password_receive,
                    "role": role_receive,
                }
            },
        )

        return jsonify({"result": "success", "msg": "Data User Successfully Edited!"})


# endpoint dashboard delete user
@app.route("/admin/user/delete", methods=["POST"])
@admin_required
def delete_user():
    # mengambil id user yang akan dihapus
    id_receive = request.form["id_give"]

    # menghapus user dari database
    db.users.delete_one({"_id": ObjectId(id_receive)})

    return jsonify({"result": "success", "msg": "Data User Successfully Deleted!"})


# endpoint dashboard table products
@app.route("/admin/products")
@admin_required
def products_table():
    products = list(db.products.find())
    for product in products:
        product["_id"] = str(product["_id"])
    return render_template(
        "admin/pages/products.html",
        products=products,
        username=request.username,
    )


# endpoint dashboard create products
@app.route("/admin/products/create", methods=["GET", "POST"])
@admin_required
def create_product():
    if request.method == "POST":
        # Mengambil data dari form
        product_name = request.form["product_name"]
        description = request.form["description"]
        price = request.form["price"]
        category = request.form["category"]
        image = request.files["image"]

        # Cek apakah semua field diisi
        if not product_name or not price or not category:
            return jsonify({"result": "error", "msg": "All fields are required!"}), 400

        # Menyimpan gambar jika ada
        image_filename = None
        if image and image.filename != "":
            image_filename = image.filename
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))

        # Menyimpan produk ke database
        new_product = {
            "product_name": product_name,
            "description": description,
            "price": int(price),
            "category": category,
            "image": image_filename,
        }
        db.products.insert_one(new_product)

        return jsonify({"result": "success", "msg": "Product successfully created!"})

    # Menampilkan halaman form
    return render_template(
        "admin/pages/create_product.html",
        username=request.username,
    )


# Rute untuk mengedit produk
@app.route("/admin/product/edit/<string:product_id>", methods=["GET", "POST"])
@admin_required
def edit_product(product_id):
    # Ambil data produk dari database
    product = db.products.find_one({"_id": ObjectId(product_id)})

    if not product:
        return "Product not found!", 404

    # Daftar kategori (misalnya Cookies dan Brownies)
    categories = ["Cookies", "Brownies"]

    # Jika permintaan menggunakan method GET
    if request.method == "GET":
        # Render halaman edit produk dengan data produk yang ada
        return render_template(
            "admin/pages/edit_product.html",
            product=product,
            categories=categories,
            username=request.username,
        )

    # Jika permintaan menggunakan method POST (untuk update produk)
    if request.method == "POST":
        # Ambil data dari form
        product_name = request.form["product_name"]
        description = request.form["description"]
        price = request.form["price"]
        category = request.form["category"]
        image = request.files["image"]

        # Validasi input (pastikan semua kolom diisi)
        if not product_name or not price or not category:
            return "All fields are required!", 400

        # Menyiapkan data untuk update produk
        update_data = {
            "product_name": product_name,
            "description": description,
            "price": int(price),
            "category": category,
        }

        # Update gambar jika ada
        if image and image.filename != "":
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_filename))
            update_data["image"] = image_filename

        # Update produk di database
        db.products.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})

        # Kembali ke halaman daftar produk setelah berhasil diupdate
        return redirect(url_for("products_table"))


# Endpoint untuk menghapus produk
@app.route("/admin/product/delete", methods=["POST"])
@admin_required
def delete_product():
    product_id = request.form.get("id_give")  # Mendapatkan ID produk yang akan dihapus

    # Menghapus produk dari database berdasarkan ID
    result = db.products.delete_one({"_id": ObjectId(product_id)})

    if result.deleted_count == 1:
        # Mengirimkan respon jika produk berhasil dihapus
        return jsonify({"msg": "Data User Successfully Deleted!"}), 200
    else:
        # Mengirimkan respon jika produk tidak ditemukan
        return jsonify({"msg": "Produk tidak ditemukan!"}), 404


# endpoint orders table
@app.route("/admin/orders")
@admin_required
def orders_table():
    orders = list(db.orders.find())

    # Mengonversi ObjectId menjadi string dan menambahkan beberapa data tambahan
    for order in orders:
        order["_id"] = str(order["_id"])

        if "purchased_on" not in order:
            order["purchased_on"] = datetime.utcnow()

        total_price = 0
        for product in order.get("products", []):
            product_price = int(product.get("price", 0))
            product_quantity = int(product.get("quantity", 0))
            total_price += product_price * product_quantity
        order["total_price"] = total_price

        order["total_quantity"] = sum(
            int(product.get("quantity", 0)) for product in order.get("products", [])
        )

        order["customer_name"] = order.get("customer_name", "Unknown")

    return render_template(
        "admin/pages/orders.html",
        orders=orders,
        username=request.username,
    )


# Route untuk mengupdate status order
@app.route("/admin/order/update_status", methods=["POST"])
@admin_required
def update_order_status():
    order_id = request.form.get("order_id")
    status = request.form.get("status")

    # Update status order
    db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": status}})

    return jsonify({"msg": "Order status updated successfully!"})


@app.route("/admin/order/delete", methods=["POST"])
@admin_required
def delete_order():
    order_id = request.form.get("order_id")

    if not order_id:
        return jsonify({"status": "error", "message": "Order ID is required"}), 400

    try:
        # Menghapus order dari database
        db.orders.delete_one({"_id": ObjectId(order_id)})
        return (
            jsonify({"status": "success", "message": "Order deleted successfully!"}),
            200,
        )
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# Jalankan aplikasi
if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
