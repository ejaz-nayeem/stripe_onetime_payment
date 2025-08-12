# payments/views.py
import stripe
from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Import our new model
from .models import Order

stripe.api_key = settings.STRIPE_SECRET_KEY

# payments/views.py

# payments/views.py
# ... keep all your other imports and views ...

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt # Stripe will not send a CSRF token
def stripe_webhook(request):
    """
    Stripe webhook view to handle checkout session completed event.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Retrieve the order_id from the session metadata
        order_id = session.metadata.get('order_id')
        
        # Find the order in our database
        try:
            order = Order.objects.get(id=order_id)
            
            # If the order is found, update its status
            if order.status == Order.Status.PENDING:
                order.status = Order.Status.COMPLETED
                order.save()
                print(f"Webhook success: Order {order_id} has been marked as COMPLETED.")

        except Order.DoesNotExist:
            print(f"Webhook error: Order with id={order_id} not found.")

    else:
        # Handle other event types
        print(f"Unhandled event type {event['type']}")

    return HttpResponse(status=200)

class StripeCheckoutView(APIView):
    def post(self, request):
        product_name = "Test Product (DRF)"
        price = 2000  # in cents, so $20.00

        try:
            # Step 1: Create the Order in PENDING state.
            # We only need its ID to pass to Stripe.
            order = Order.objects.create(
                product_name=product_name,
                price=price / 100
            )
        except Exception as e:
            return Response({'error': 'Could not create order.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Step 2: Create the Stripe Session.
        try:
            success_url = request.build_absolute_uri(f'/success/?order_id={order.id}')
            cancel_url = request.build_absolute_uri('/cancel/')

            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': product_name},
                        'unit_amount': price,
                    },
                    'quantity': 1,
                }],
                metadata={
                    # This is the crucial link back to our system
                    'order_id': order.id
                },
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
            )

            # WE DO NOT NEED TO SAVE THE ORDER HERE.
            # The only source of truth for completion will be the success redirect.
            
            return Response({'checkout_url': checkout_session.url})
        
        except Exception as e:
            # If creating the Stripe session fails, we don't need to do anything
            # with the order, it will just remain 'Pending'.
            return Response(
                {'error': 'Something went wrong while creating stripe checkout session'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# This view now handles the SUCCESS logic
def success(request):
    # Retrieve the session_id from the URL's query parameters
    order_id = request.GET.get('order_id')
    
    # Check if the session_id exists to prevent errors
    if not order_id:
        # Optionally, render an error page or redirect
        print("Success page loaded without order_id.")
        # Render a generic success page if there's no ID
        return render(request, 'success.html')

    try:
        # Find the order that the webhook should have already completed.
        order = Order.objects.get(id=order_id)
        # We no longer need to update the status here. The webhook did it.
        return render(request, 'success.html', {'order': order})

    except Order.DoesNotExist:
        # This is a safeguard in case the order_id is invalid.
        print(f"User redirected to success page, but Order with ID {order_id} not found.")
        return render(request, 'success.html') # Render a generic success page


# Cancel view remains unchanged
def cancel(request):
    return render(request, 'cancel.html')