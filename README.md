# Flask E-commerce Website

**Live Demo:** [https://ecommerce-zawu.onrender.com](https://ecommerce-zawu.onrender.com)

*Note: The live website may take a minute to deploy due to Render's free-tier cold start.*

A full-stack e-commerce web application built with Python and the Flask framework. This project demonstrates a complete, deployable online store with user authentication, a dynamic shopping cart, and a real payment integration using Stripe.


## Features

*   **Product Catalog:** Browse a list of all available products on the homepage.
*   **User Authentication:** Users can register for an account, log in, and log out.
*   **Shopping Cart:** Both guests and logged-in users have persistent shopping carts.
*   **Dynamic Cart Management:** Add items, update quantities, or remove items from the cart with AJAX for a seamless experience without page reloads.
*   **Stripe Payment Integration:** A complete checkout workflow using Stripe Checkout for secure payment processing.
*   **Order History:** Logged-in users can view a history of their past orders.
*   **Automated Database Setup:** The application is configured to automatically handle database migrations and seed initial data on deployment.
*   **Responsive Design:** The user interface is fully responsive and mobile-friendly, built using the Bootstrap 5 framework to ensure a seamless experience on desktops, tablets, and phones.

## Technology Stack

*   **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate
*   **Database:** PostgreSQL (Production), SQLite (Development)
*   **Payments:** Stripe API
*   **Frontend:** HTML, CSS, Bootstrap 5, JavaScript
*   **Deployment:** Gunicorn, Render

## Security Considerations

Security was a key consideration during development. The application includes the following measures:

*   **Password Hashing:** User passwords are hashed and salted using the Werkzeug security library.
*   **CSRF Protection:** All forms are protected against Cross-Site Request Forgery (CSRF) attacks using Flask-WTF.
*   **Secure Payment Processing:** All payment information is handled directly by Stripe's secure checkout, ensuring no sensitive credit card data ever touches the application server.

## Screenshots

**Homepage:**

<img width="1640" height="757" alt="image" src="https://github.com/user-attachments/assets/8dbc3f01-2857-453f-9610-77c396dcdecf" />
<br>
<br>

**Product page and shopping cart:**
  
<img width="1783" height="907" alt="image" src="https://github.com/user-attachments/assets/be450a21-6c81-4ed8-b82e-84db8d2d6c64" />
<br>
<br>

**Stripe Checkout:**

<img width="1232" height="739" alt="image" src="https://github.com/user-attachments/assets/c0044050-70f6-497c-beff-2fecfb4e40bb" />
