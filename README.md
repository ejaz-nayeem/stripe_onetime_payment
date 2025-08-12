# Stripe Payment Backend 

This is the Django backend that handles payment processing via Stripe. It provides a simple API for a frontend client to initiate payments and uses secure webhooks to confirm them.

---
#This is a one-time payment system.
#did not use authentication.
#i used webhook.
#i also used ngrok to run the program from another pc.
## Local Setup Instructions

Follow these steps to run the backend server on your local machine for development and testing.

1.  **Clone the repository:**
    `git clone <your-repo-url>`

2.  **Create and activate a virtual environment:**
    `python -m venv venv`
    `source venv/bin/activate`  # On Windows: `venv\Scripts\activate`

3.  **Install dependencies:**
    `pip install -r requirements.txt`

4.  **Set up your environment variables:**
    - Copy the example environment file: `cp .env.example .env`
    - Open the `.env` file and fill in the required values. You will need your own free Stripe test account to get API keys.
    - Leave `STRIPE_WEBHOOK_SECRET` blank for now.

5.  **Run database migrations:**
    `python manage.py migrate`

6.  **Start the Django server (Terminal 1):**
    `python manage.py runserver`

7.  **Start the Stripe Webhook Forwarder (Terminal 2):**
    - Open a **second terminal**.
    - Run the Stripe CLI to forward events to your local server:
      `stripe listen --forward-to http://127.0.0.1:8000/stripe-webhook/`
    - The CLI will print a **temporary** webhook signing secret (`whsec_...`).

8.  **Update the Webhook Secret:**
    - **Copy** the new `whsec_...` secret from the Stripe CLI.
    - **Paste** it into your `.env` file.
    - **Restart your Django server** in Terminal 1 (`Ctrl+C`, then `python manage.py runserver`) to load the new secret.

The backend is now running and ready to accept API calls.

---

## API Documentation

This section describes the API endpoint that the frontend will use.

### Create Checkout Session

This endpoint starts the payment process. It creates an order on the backend and returns a unique, secure URL from Stripe. The frontend's only job is to redirect the user to this URL.

*   **Endpoint:** `/api/checkout/`
*   **Method:** `POST`
*   **Authentication:** None required.
*   **Request Body:** None required.

#### Success Response

*   **Code:** `200 OK`
*   **Content:** A JSON object containing the Stripe URL.

**Example:**
```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_test_a1B2c3..."
}
