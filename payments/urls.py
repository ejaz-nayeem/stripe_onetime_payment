from django.urls import path
from . import views
from .views import StripeCheckoutView

urlpatterns = [
    #path('', views.checkout, name='checkout'),
    path('api/checkout/', StripeCheckoutView.as_view(), name='api-checkout'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe-webhook'),
] 