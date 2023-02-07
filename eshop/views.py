from django.shortcuts import render,redirect
import stripe
from django.views.generic import DetailView,ListView
from django.views import View
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,login,authenticate
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from .models import *
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
class ProductListView(ListView):
    model = Category
    context_object_name = "categories"
    template_name = "home.html"

def product(request,id):
    items = Category.objects.get(id=id)
    product = Product.objects.filter(category=items)
    return render(request,"product_detail.html",{"items":items,"products":product})

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()

    else:
        items = []
    context = {'items':items}
    return render(request,"cart.html",context)

class CreateStripeCheckoutSessionView(View):
    """
    Create a checkout session and redirect the user to Stripe's checkout page
    """

    def post(self, request, *args, **kwargs):
        price = Product.objects.get(id=self.kwargs["pk"])

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(price.price) * 10,
                        "product_data": {
                            "name": price.name,
                            "description": price.description,
                            "images": [
                                f"{settings.BACKEND_DOMAIN}/{price.image}"
                            ],
                        },
                    },
                    "quantity": price.quantity,
                }
            ],
            metadata={"product_id": price.id},
            mode="payment",
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
        )
        return redirect(checkout_session.url)