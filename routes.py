from flask import render_template, redirect, url_for, request, jsonify, flash, session, abort, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, current_user, logout_user
import stripe, os

from app import app, db, csrf
from models import User, Product, CartItem, Order, OrderItem
from forms import LoginForm, RegistrationForm


@app.context_processor
def inject_stripe_key():
    return dict(
        stripe_publishable_key=os.getenv('STRIPE_PUBLISHABLE_KEY')
    )


@app.context_processor
def inject_cart_data():
    cart_items_list = []
    cart_total = 0
    cart_item_count = 0
    # For logged-in user
    if current_user.is_authenticated:
        db_items = CartItem.query.filter_by(user_id=current_user.id).all()
        for item in db_items:
            cart_items_list.append({
                'product_id': item.product.id, 
                'name': item.product.name,
                'price': float(item.product.price_with_tax),
                'quantity': item.quantity,
                'image_url': item.product.image_url
            })
            cart_total += item.product.price_with_tax * item.quantity
            cart_item_count += item.quantity
    # For quest user
    else:
        guest_cart = session.get('cart', {})
        cart_items_list = list(guest_cart.values())
        for item_data in cart_items_list:
            cart_total += item_data['price'] * item_data['quantity']
            cart_item_count += item_data['quantity']

    return dict(
        cart_items=cart_items_list, 
        cart_total=cart_total, 
        cart_item_count=cart_item_count
    )


@app.route("/")
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)


@app.route("/product/<product_name>")
def view_product(product_name):
    product = Product.query.filter_by(name=product_name).first()
    return render_template('product.html', product=product)


@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm() 
    
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("That email is already taken. Please choose a different one.", "warning")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(
            form.password.data, 
            method='pbkdf2:sha256:600000', 
            salt_length=8
        )
        
        new_user = User(
            email=form.email.data, 
            password=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        
        flash("Account created successfully!", "success")
        return redirect(url_for('index'))
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    
    form = LoginForm() 
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password. Please try again.", "danger")
            return redirect(url_for('login'))

        login_user(user, remember=True)
        return redirect(url_for("index"))
    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/manage_cart", methods=["POST"])
def manage_cart():
    product_id = int(request.form.get('product_id'))  
    quantity = int(request.form.get('quantity', 1))
    action = request.form.get('action', 'add') 

    if quantity < 1:
        return remove_from_cart()

    product = Product.query.get(product_id)
    if not product:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Product not found!'}), 400
        else:
            flash("Product not found!", "danger")
            return redirect(request.referrer)

    # For logged-in users
    if current_user.is_authenticated:
        item = CartItem.query.filter_by(user_id=current_user.id, product_id=product.id).first()

        # If item exists, decide whether to add or set
        if item:
            if action == 'set_quantity':
                item.quantity = quantity
            else:  # Default 'add' action
                item.quantity += quantity
        else:
            # Item doesn't exist, create it
            item = CartItem(user_id=current_user.id, product_id=product.id, quantity=quantity)
            db.session.add(item)
        
        db.session.commit()
        # Compute new count
        db_items = CartItem.query.filter_by(user_id=current_user.id).all()
        new_count = sum(item.quantity for item in db_items)
    # For guest users
    else:
        if 'cart' not in session:
            session['cart'] = {}
        
        cart = session['cart']
        product_id_str = str(product_id)

        if product_id_str in cart:
            if action == 'set_quantity':
                cart[product_id_str]['quantity'] = quantity
            else:  
                cart[product_id_str]['quantity'] += quantity
        else:
            cart[product_id_str] = {
                'product_id': product.id,
                'name': product.name,
                'price': float(product.price_with_tax),
                'quantity': quantity,
                'image_url': product.image_url
            }

        session.modified = True

        guest_cart = session.get('cart', {})
        new_count = sum(item['quantity'] for item in guest_cart.values())

    message = "Cart updated."
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': message, 'cart_item_count': new_count})
    else:
        flash(message, "success")
        return redirect(request.referrer or url_for('index'))


@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    product_id = int(request.form.get('product_id'))
    message = "Item removed from cart."
    new_count = 0

    if current_user.is_authenticated:
        item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if item:
            db.session.delete(item)
            db.session.commit()

            db_items = CartItem.query.filter_by(user_id=current_user.id).all()
            new_count = sum(item.quantity for item in db_items)
    else:
        cart = session.get('cart', {})
        product_id_str = str(product_id)
        if product_id_str in cart:
            del cart[product_id_str]
            session.modified = True

            new_count = sum(item['quantity'] for item in cart.values())

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'message': message, 'cart_item_count': new_count})
    else:
        flash(message, "success")
        referrer = request.referrer or url_for('index')
        redirect_url = f"{referrer.split('?')[0]}?open_cart=true"
        return redirect(redirect_url)
    

@app.route('/get_cart_html')
def get_cart_html():
    response = make_response(render_template('cart_items.html'))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    line_items = []
    
    tax_rate_id = os.getenv('STRIPE_TAX_RATE_ID')
    if not tax_rate_id:
        return jsonify(error="Stripe Tax Rate ID is not configured."), 500

    # For logged-in user
    if current_user.is_authenticated:
        cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
        for cart_item in cart_items:
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {'name': cart_item.product.name},
                    'unit_amount': int(cart_item.product.price_with_tax * 100),
                },
                'quantity': cart_item.quantity,
                'tax_rates': [tax_rate_id]
            })
    # For guests
    else:
        guest_cart = session.get('cart', {})
        for product_id, item_data in guest_cart.items():
            line_items.append({
                'price_data': {
                    'currency': 'eur',
                    'product_data': {'name': item_data['name']},
                    'unit_amount': int(item_data['price'] * 100),
                },
                'quantity': item_data['quantity'],
                'tax_rates': [tax_rate_id]
            })

    try:
        domain_url = os.getenv('DOMAIN', 'http://127.0.0.1:5000')
        client_ref_id = str(current_user.id) if current_user.is_authenticated else None
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card', 'mobilepay'],
            line_items=line_items,
            mode='payment',
            success_url=domain_url + '/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + '/cancel',
            customer_email='test@domain.test',
            client_reference_id=client_ref_id
        )
        return jsonify(id=checkout_session.id)
    except Exception as e:
        return jsonify(error=str(e)), 403
    

@app.route('/stripe-webhook', methods=['POST'])
@csrf.exempt
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    event = None

    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=sig_header, secret=webhook_secret)
    except ValueError as e:
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        return 'Invalid signature', 400
    
    if event['type'] == 'checkout.session.completed':
        try:
            session = event['data']['object']
            user_id_str = session.get('client_reference_id')
            user_id = int(user_id_str) if user_id_str else None
            line_items = stripe.checkout.Session.list_line_items(session.id, limit=50)

            new_order = Order(
                user_id=user_id,
                guest_email=session.customer_details.email,
                total_price=session.amount_total / 100.0,
                stripe_payment_id=session.payment_intent
            )
            db.session.add(new_order)
            db.session.commit()

            for item in line_items.data:
                product = Product.query.filter_by(name=item.description).first()
                new_order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=product.id if product else None,
                    quantity=item.quantity,
                    price_at_purchase=item.price.unit_amount / 100.0 if item.price else 0
                )
                db.session.add(new_order_item)

            db.session.commit()

            # Clear shopping cart
            if user_id:
                deleted_count = CartItem.query.filter_by(user_id=user_id).delete()
                db.session.commit()
        except Exception as e:
            db.session.rollback()  # Prevent partial saves
            return jsonify({'status': 'error', 'message': str(e)}), 500  

    return jsonify({'status': 'success'}), 200


@app.route('/success')
def success():
    # Check if a cart exists in the session and remove it
    if 'cart' in session:
        session.pop('cart', None)
    
    return render_template('success.html')


@app.route("/cancel")
def cancel():
    return render_template('cancel.html')


@app.route('/orders')
@login_required
def order_history():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.order_date.desc()).all()
    return render_template('order_history.html', orders=user_orders)


@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first()
    if order is None:
        abort(404)
    return render_template('order_detail.html', order=order)
