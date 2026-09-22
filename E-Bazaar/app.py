from flask import Flask, request, render_template, render_template_string, redirect, make_response, session
import base64
import json
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

HTML = 'index.html'
ADMIN_HTML = 'admin_index.html'
CHECKOUT_PAGE = 'checkout.html'
ADMIN_PAGE = 'admin.html'


items_id = {'1': "Basic Magic Wand", '2': "Mage Costume", '3': "Book of Spells", '4': "Iced Out Magic Wand", '5':"Elixir Vitae", '6':"Elixir of Invisibility"}


def encode_cookie(data):
    return base64.b64encode(json.dumps(data).encode()).decode()

def decode_cookie(cookie):
    try:
        return json.loads(base64.b64decode(cookie).decode())
    except:
        return None

def reset_cart(cart):
    for id in cart:
        cart[id] = 0
    session.modified = True

def calculate_cart(cart):
    cart_text = ""
    total_price = 0
    for id, amount in cart.items():
        item = items_id[id]     
        price = session["items_price"][id]
        if amount != 0:
            try:
                cart_text += f'x{amount} {item} = {price * amount}\n'
                total_price += price * amount
            except Exception:
                reset_cart(cart)
                return "Server ran into an error while editing your cart.", 0
    cart_text += f'Total: {total_price}$'
    return cart_text, total_price

@app.route("/", methods=["GET"])
def index():
    if "cart" not in session:
        session["cart"] = {'1':0,'2':0,'3':0, '4':0, '5':0, '6':0}
        session["balance"] = 100
        session["first_flag_found"] = False
        session["second_flag_found"] = False
        session["items_price"] = {'1': 10, '2': 25, '3':50, '4': 9999999, '5':None, '6':0}
        session.modified = True

    cart_text, total_price = calculate_cart(session["cart"])
    cookie = request.cookies.get("auth")
    data = decode_cookie(cookie)
    if not data:
        pass
    else:
        if data.get("user") == "admin" and data.get("loggedIn") is True:
            session["first_flag_found"] = True
            session["second_flag_found"] = True  
            session.modified = True
    if session["first_flag_found"] and session["second_flag_found"]:
        cookie = request.cookies.get("auth")
        data = decode_cookie(cookie)
        if not data:
            return render_template_string("Invalid cookies.")
        
        if data.get("user").lower() == "admin" and data.get("loggedIn") is True:
            return render_template(
                ADMIN_HTML,
                cart=cart_text,
                balance=session["balance"],
                items_id=items_id,
                items_price=session["items_price"]
            )
    return render_template(
        HTML,
        cart=cart_text,
        balance=session["balance"],
        items_id=items_id,
        items_price=session["items_price"]
    )
@app.after_request
def set_default_cookies(response):
    if "cart" not in session:
        session["cart"] = {'1':0,'2':0,'3':0, '4':0, '5':0, '6':0}
        session["balance"] = 100
        session["first_flag_found"] = False
        session["second_flag_found"] = False
        session["items_price"] = {'1': 10, '2': 25, '3':50, '4': 9999999, '5':None, '6':0}
        session.modified = True

    if session["first_flag_found"] and session["second_flag_found"]:
        if not request.cookies.get("auth"):
            auth_cookie = encode_cookie({
                "user": "None",
                "loggedIn": False
            })

            response.set_cookie(
                "auth",
                auth_cookie,
                path="/",
                httponly=False 
            )

    return response



@app.route("/items/edit_admin", methods=["POST"])
def edit_price():
    try:
        session["items_price"][str(request.form.get("id"))] = int(request.form.get("set_price"))
        session.modified = True
    except Exception as err:
        return render_template_string(f'{err}')
    return redirect("/")

@app.route("/admin", methods=["POST", "GET"])
def debug():
    if not session["first_flag_found"] or not session["second_flag_found"]:
        return render_template_string("Find the first 2 pieces of the flag in order for access.")
    usr = "admin"
    pss = "1234567"
    if request.method == "GET": return render_template(ADMIN_PAGE)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username.lower() == usr and password == pss:
            cookie = encode_cookie({
                "user":"admin",
                "loggedIn":True
            })
            resp = make_response(redirect("/"))
            resp.set_cookie("auth", cookie)
            return resp
        elif username.lower() == usr and password != pss: 
            return render_template(ADMIN_PAGE, message="Invalid password.")
        elif username.lower() != usr: return render_template(ADMIN_PAGE, message="Invalid username.")
        else: return render_template(ADMIN_PAGE, message="Invalid credentials.")

@app.route("/cart/update", methods=["POST"])
def update_cart():
    item_ids = request.form.getlist("item_id")
    item_amounts = request.form.getlist("item_amount")
    if request.form.get("reset_cart"):
        for id in session["cart"]:
            session["cart"][id] = 0
        session.modified = True
        return redirect('/')
    for item_id, amount in zip(item_ids, item_amounts):
        item_id = str(item_id)
        amount = int(amount)
        session["cart"][item_id] += amount
    session.modified = True
    return redirect("/")

@app.route("/checkout", methods=["POST"])
def checkout():

    cart_text, total_price = calculate_cart(session["cart"])
    cart_empty = request.form.get("636172745F656D707479")
    override = request.form.get("666f7263655f636865636b6f7574")

    base64_string = override
    base64_bytes = base64_string.encode("ascii")

    sample_string_bytes = base64.b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("ascii")

    if sample_string.strip().lower() != "true":
        for item in session["cart"]:
            if int(session["cart"][item]) < 0:
                return render_template(
                    CHECKOUT_PAGE,
                    message = ["", "Something Seems To Be Wrong."]
                    )
    if cart_empty == "Z29vZGx1Y2s=":
        for id in session["cart"]:
            if session["cart"][id] > 0:
                cart_empty = False
        if cart_empty == "Z29vZGx1Y2s=": cart_empty = True
    
    if cart_empty == True:
        return render_template(
        CHECKOUT_PAGE,
        message=["", "Cart Is Empty"]
    )
    if session["balance"] >= total_price:
        session["balance"] -= total_price
        message = ["", "Checkout Successful"]
        session.modified = True
        if session["cart"]["4"] >= 1:
            session["second_flag_found"] = True
            message = ["Achievement Unlocked: Flexing.", "2nd part of the flag: L0V3_"]
            session.modified = True
        if session["cart"]["5"] >= 1:
            message = ["Achievement Unlocked: Web wizard.", "3rd (final) part of the flag: hT7p_Ch4lS}"]
        if session["cart"]["6"] >= 1:
            session["first_flag_found"] = True
            message = ["Achievement Unlocked: You can't see me.", "1st part of the flag: FantasyCTF{1_"]
            session.modified = True
        for id in session["cart"]:
            session["cart"][id] = 0
            session.modified = True
    else:
        message = ["", "Insufficient balance."]
    return render_template(
        CHECKOUT_PAGE,
        message=message
    )


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 80)) 
    app.run(debug=False, host='0.0.0.0', port=port)
