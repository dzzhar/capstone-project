<<<<<<< HEAD
import os
from datetime import datetime
from os.path import dirname, join

from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from pymongo import MongoClient

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)


MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

=======
from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
>>>>>>> 24ff6c1 (edit_product)

app = Flask(__name__)

# Konfigurasi MongoDB
DB_PASSWORD = os.getenv("DB_PASSWORD", "<db_password>")
MONGO_URL = f"mongodb+srv://danny:25cungkring@cluster0.60qw6.mongodb.net/bynotti"
client = MongoClient(MONGO_URL)
db = client['bynotti']
products_collection = db['products']

# Konfigurasi untuk folder upload
UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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


<<<<<<< HEAD
# endpoint cart
=======
# Rute untuk halaman keranjang belanja
>>>>>>> 24ff6c1 (edit_product)
@app.route("/cart")
def cart():
    return render_template("home/pages/cart.html")


<<<<<<< HEAD
# endpoint login
=======
# Rute untuk halaman login
>>>>>>> 24ff6c1 (edit_product)
@app.route("/login")
def login():
    return render_template("home/pages/login.html")


<<<<<<< HEAD
# endpoint register
@app.route("/register")
def register():
    return render_template("home/pages/register.html")


# endpoint dashboard table users
@app.route("/admin/users")
=======
# Rute untuk tabel pengguna di dashboard
@app.route("/dashboard/users")
>>>>>>> 24ff6c1 (edit_product)
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


<<<<<<< HEAD
# endpoint dashboard table products
@app.route("/admin/products")
=======
# Rute untuk tabel produk di dashboard
@app.route("/dashboard/products")
>>>>>>> 24ff6c1 (edit_product)
def products_table():
    products = list(products_collection.find())
    for product in products:
        product['_id'] = str(product['_id'])
    return render_template("admin/pages/products.html", products=products)


<<<<<<< HEAD
# endpoint dashboard create products
@app.route("/admin/products/create")
=======
# Rute untuk halaman membuat pengguna
@app.route("/dashboard/users/create")
def create_user():
    return render_template("admin/pages/create_user.html")


# Rute untuk membuat produk baru
@app.route('/dashboard/products/create', methods=['GET', 'POST'])
>>>>>>> 24ff6c1 (edit_product)
def create_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        price = request.form['price']
        category = request.form['category']
        image = request.files['image']

        if not product_name or not price or not category:
            return "All fields are required!", 400

        # Simpan file gambar jika ada
        image_filename = None
        if image and image.filename != '':
            image_filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        # Simpan data ke MongoDB
        new_product = {
            'product_name': product_name,
            'price': int(price),
            'category': category,
            'image': image_filename
        }
        products_collection.insert_one(new_product)
        return redirect(url_for('products_table'))

    return render_template("admin/pages/create_product.html")


# Rute untuk mengedit produk
@app.route('/dashboard/products/edit/<string:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    # Ambil data produk dari database
    product = products_collection.find_one({'_id': ObjectId(product_id)})

    if not product:
        return "Product not found!", 404

    # Daftar kategori (Cookies dan Brownies)
    categories = ['Cookies', 'Brownies']

    if request.method == 'POST':
        # Ambil data dari form
        product_name = request.form['product_name']
        price = request.form['price']
        category = request.form['category']
        image = request.files['image']

        # Validasi input
        if not product_name or not price or not category:
            return "All fields are required!", 400

        # Data untuk update produk
        update_data = {
            'product_name': product_name,
            'price': int(price),
            'category': category
        }

        # Update gambar jika ada
        if image and image.filename != '':
            image_filename = image.filename
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
            update_data['image'] = image_filename

        # Update produk di database
        products_collection.update_one({'_id': ObjectId(product_id)}, {'$set': update_data})
        return redirect(url_for('products_table'))

    return render_template("admin/pages/edit_product.html", product=product, categories=categories)



# Rute untuk menghapus produk
@app.route('/dashboard/products/delete/<string:product_id>')
def delete_product(product_id):
    products_collection.delete_one({'_id': ObjectId(product_id)})
    return redirect(url_for('products_table'))


# Jalankan aplikasi
if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
