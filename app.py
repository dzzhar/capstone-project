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


app = Flask(__name__)


# endpoint home
@app.route("/")
def home():
    return render_template("home/pages/home.html")


# endpoint contact
@app.route("/contact")
def contact():
    return render_template("home/pages/contact.html")


# endpoint products
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
    return render_template("admin/pages/products.html")


# endpoint dashboard create products
@app.route("/admin/products/create")
def create_product():
    return render_template("admin/pages/create_product.html")


# run app
if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
