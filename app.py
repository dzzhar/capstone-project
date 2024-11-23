from flask import Flask, render_template

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


# endpoint products
@app.route("/cart")
def cart():
    return render_template("home/pages/cart.html")


# endpoint products
@app.route("/login")
def login():
    return render_template("home/pages/login.html")


# endpoint dashboard table users
@app.route("/dashboard/users")
def users_table():
    return render_template("admin/pages/users.html")


# endpoint dashboard table products
@app.route("/dashboard/products")
def products_table():
    return render_template("admin/pages/products.html")


# endpoint dashboard create users
@app.route("/dashboard/users/create")
def create_user():
    return render_template("admin/pages/create_user.html")


# endpoint dashboard create products
@app.route("/dashboard/products/create")
def create_product():
    return render_template("admin/pages/create_product.html")


# run app
if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
