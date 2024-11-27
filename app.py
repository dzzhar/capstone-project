import os
from werkzeug.utils import secure_filename
from datetime import datetime
from os.path import dirname, join

from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, url_for
from pymongo import MongoClient

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)


MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__)

# Konfigurasi untuk folder upload
UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}

# Memeriksa apakah file yang diupload memiliki ekstensi yang valid
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]


# Rute untuk halaman utama
@app.route("/")
def home():
    return render_template("home/pages/home.html")


# Rute untuk halaman kontak
@app.route("/contact")
def contact():
    return render_template("home/pages/contact.html")


# Rute untuk halaman produk
@app.route("/products")
def products():
    return render_template("home/pages/products.html")


# endpoint cart
@app.route("/cart")
def cart():
    return render_template("home/pages/cart.html")


# endpoint login
@app.route("/login")
def login():
    return render_template("home/pages/login.html")


# endpoint register
@app.route("/register")
def register():
    return render_template("home/pages/register.html")


# endpoint dashboard table users
@app.route("/admin/users")
def users_table():
    # mengambil semua data users
    users_list = list(db.users.find({}))

    # mengirim tabel pengguna
    return render_template("admin/pages/users.html", users=users_list)


# endpoint dashboard create users
@app.route("/admin/user/create", methods=["GET", "POST"])
def create_user():
    # permintaan menggunakan method POST
    if request.method == "POST":
        # mengambil beberapa data dari form
        username_receive = request.form["username_give"]
        password_receive = request.form["password_give"]
        role_receive = request.form["role_give"]

        # membuat doc untuk penyimpanan database
        doc = {
            "username": username_receive,
            "password": password_receive,
            "role": role_receive,
        }
        db.users.insert_one(doc)

        return jsonify({"result": "success", "msg": "Data User Successfully Added!"})

    # merender ke halaman create user
    return render_template("admin/pages/create_user.html")


# endpoint dashboard edit users
@app.route("/admin/user/edit/<id>", methods=["GET", "POST"])
def edit_user(id):
    # permintaan menggunakan method GET
    if request.method == "GET":
        # mengambil data user berdasarkan id
        user_id = db.users.find_one({"_id": ObjectId(id)})

        # render ke halaman edit user dengan id user
        return render_template("admin/pages/edit_user.html", user=user_id)

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
def delete_user():
    # mengambil id user yang akan dihapus
    id_receive = request.form["id_give"]

    # menghapus user dari database
    db.users.delete_one({"_id": ObjectId(id_receive)})

    return jsonify({"result": "success", "msg": "Data User Successfully Deleted!"})


# endpoint dashboard table products
@app.route("/admin/products")
def products_table():
    products = list(db.products.find())
    for product in products:
        product["_id"] = str(product["_id"])
    return render_template("admin/pages/products.html", products=products)


# endpoint dashboard create products
@app.route("/admin/products/create", methods=["GET", "POST"])
def create_product():
    if request.method == "POST":
        # Mengambil data dari form
        product_name = request.form["product_name"]
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
            "price": int(price),
            "category": category,
            "image": image_filename,
        }
        db.products.insert_one(new_product)

        return jsonify({"result": "success", "msg": "Product successfully created!"})

    # Menampilkan halaman form
    return render_template("admin/pages/create_product.html")



# Rute untuk mengedit produk
@app.route("/admin/product/edit/<string:product_id>", methods=["GET", "POST"])
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
        return render_template("admin/pages/edit_product.html", product=product, categories=categories)

    # Jika permintaan menggunakan method POST (untuk update produk)
    if request.method == "POST":
        # Ambil data dari form
        product_name = request.form["product_name"]
        price = request.form["price"]
        category = request.form["category"]
        image = request.files["image"]

        # Validasi input (pastikan semua kolom diisi)
        if not product_name or not price or not category:
            return "All fields are required!", 400

        # Menyiapkan data untuk update produk
        update_data = {
            "product_name": product_name,
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


# Jalankan aplikasi
if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
