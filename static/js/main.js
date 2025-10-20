// INITIALIZATION 

// Read all server-side data from the special div in base.html
const AppData = document.getElementById('app-data').dataset;

// Read csrf token
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

// Main entry point: Wait for the page to be fully loaded before running scripts.
document.addEventListener('DOMContentLoaded', function () {
    initializeToasts();
    handleCartUrlTrigger();
    attachGlobalEventHandlers();
});

/**
 * Attaches event handlers to elements that are always present on the page.
 */
function attachGlobalEventHandlers() {
    attachAjaxFormHandlers(document);
    attachCheckoutHandler();
}

/**
 * Initializes any Bootstrap toasts that were rendered on the page by the server.
 */
function initializeToasts() {
    const toastElList = document.querySelectorAll('.toast');
    [...toastElList].map(toastEl => new bootstrap.Toast(toastEl).show());
}


// CORE LOGIC & EVENT HANDLERS 

/**
 * Checks if the URL has the 'open_cart' parameter and shows the offcanvas if it does.
 * It also cleans the URL to prevent the cart from opening on every refresh.
 */
function handleCartUrlTrigger() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('open_cart') === 'true') {
        const cartOffcanvasElement = document.getElementById('cartOffcanvas');
        if (cartOffcanvasElement) {
            const cartOffcanvas = new bootstrap.Offcanvas(cartOffcanvasElement);
            cartOffcanvas.show();

            const cleanUrl = window.location.protocol + "//" + window.location.host + window.location.pathname;
            window.history.replaceState({ path: cleanUrl }, '', cleanUrl);
        }
    }
}

/**
 * Attaches the AJAX submit handler to all forms with the class '.ajax-form'.
 * @param {HTMLElement} parentElement 
 */
function attachAjaxFormHandlers(parentElement) {
    const forms = parentElement.querySelectorAll('.ajax-form');
    forms.forEach(form => {
        form.removeEventListener('submit', handleAjaxSubmit);
        form.addEventListener('submit', handleAjaxSubmit);
    });
}

/**
 * Handles the submission of any form with the '.ajax-form' class.
 * It prevents the default page reload and sends the data via Fetch.
 * @param {Event} e 
 */
function handleAjaxSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const isRemoveAction = form.getAttribute('action').includes('remove_from_cart');

    fetch(form.getAttribute('action'), {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            updateCartBadge(data.cart_item_count);
            showToast(data.message, 'success');

            updateCartOffcanvas().then(() => {
                if (isRemoveAction) {
                    const offcanvasEl = document.getElementById('cartOffcanvas');
                    const offcanvas = bootstrap.Offcanvas.getOrCreateInstance(offcanvasEl);
                    offcanvas.show();
                }
            });
        } else {
            showToast('Error: ' + (data.message || 'Unknown error'), 'danger');
        }
    })
    .catch(error => {
        console.error('AJAX form submission error:', error);
        showToast('An unexpected error occurred.', 'danger');
    });
}

/**
 * Attaches the click event handler for the Stripe checkout button.
 */
function attachCheckoutHandler() {
    const stripe = Stripe(AppData.stripeKey);
    const checkoutButton = document.getElementById('checkout-button');

    if (checkoutButton) {
        checkoutButton.removeEventListener('click', checkoutClickHandler); 
        checkoutButton.addEventListener('click', checkoutClickHandler);
    }

    function checkoutClickHandler() {
        const button = this;
        const spinner = button.querySelector('.spinner-border');
        const buttonText = button.querySelector('.button-text');

        setButtonLoadingState(button, spinner, buttonText, true);

        fetch(AppData.checkoutUrl, {
            method: 'POST',
            credentials: 'include',
            headers: { 
                'X-CSRFToken': csrfToken
        }
        })
        .then(response => response.json())
        .then(session => {
            if (session.id) {
                return stripe.redirectToCheckout({ sessionId: session.id });
            } else {
                console.error('Failed to create checkout session:', session.error);
                showToast(session.error || 'Could not proceed to checkout.', 'danger');
                setButtonLoadingState(button, spinner, buttonText, false);
            }
        })
        .catch(error => {
            console.error('Stripe checkout error:', error);
            showToast('An error occurred during checkout.', 'danger');
            setButtonLoadingState(button, spinner, buttonText, false);
        });
    }
}


// UI UPDATE HELPERS 

/**
 * Fetches the latest cart HTML from the server and injects it into the offcanvas body.
 * @returns {Promise} 
 */
function updateCartOffcanvas() {
    return fetch(AppData.cartHtmlUrl, { cache: 'no-cache' })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch cart HTML');
            }
            return response.text();
        })
        .then(html => {
            const offcanvasBody = document.querySelector('#cartOffcanvas .offcanvas-body');
            if (offcanvasBody) {
                offcanvasBody.innerHTML = html;

                attachAjaxFormHandlers(offcanvasBody);
                attachCheckoutHandler();
            }
        })
        .catch(error => {
            console.error('Error updating cart view:', error);
        });
}

/**
 * Updates the cart item count in the header badge.
 * @param {number} count 
 */
function updateCartBadge(count) {
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline' : 'none';
    }
}

/**
 * Dynamically creates and displays a Bootstrap toast message.
 * @param {string} message 
 * @param {string} category 
 */
function showToast(message, category = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) return;

    const toastEl = document.createElement('div');
    toastEl.className = `toast align-items-center text-white bg-${category} border-0`;
    toastEl.role = 'alert';
    toastEl.ariaLive = 'assertive';
    toastEl.ariaAtomic = 'true';

    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    toastContainer.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
    toast.show();

    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

/**
 * Toggles the visual state of a button between loading and default.
 * @param {HTMLButtonElement} button 
 * @param {HTMLElement} spinner
 * @param {HTMLElement} buttonText 
 * @param {boolean} isLoading 
 */
function setButtonLoadingState(button, spinner, buttonText, isLoading) {
    button.disabled = isLoading;
    if (isLoading) {
        spinner.classList.remove('d-none');
        if(buttonText) buttonText.textContent = 'Processing...';
    } else {
        spinner.classList.add('d-none');
        if(buttonText) buttonText.textContent = 'Proceed to Checkout'; 
    }
}