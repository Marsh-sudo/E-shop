from django.shortcuts import render,redirect
import stripe
import json
from django.http import JsonResponse
from django.views.generic import DetailView,ListView
from django.views import View
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout,login,authenticate
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.contrib import messages
from .models import *
from .forms import *
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
class RegisterView(View):
    form_class = RegisterForm
    initial = {'key': 'value'}
    template_name = 'register.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}')

            return redirect('login')

        return render(request, self.template_name, {'form': form})

def login_request(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('home')

        else:
            return redirect("login")

    else:
        return render(request,"login.html",{})



@login_required(login_url='login')
def home(request):
    categories = Category.objects.all()
    return render(request,"home.html",{"categories":categories})

@login_required(login_url='login')
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
        order = {"get_cart_items": 0,"get_cart_total":0}
    context = {'items':items,'order':order}
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

def profile_update(request):
    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile is updated successfully')
            return redirect(to='profile')
    else:
        user_form = UpdateUserForm(instance=request.user)
        profile_form = UpdateProfileForm(instance=request.user.profile)

    return render(request, 'profile-update.html', {'user_form': user_form, 'profile_form': profile_form})


class ProfileView(ListView):
	model = Profile
	template_name = "profile.html"


def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("login")

def updateItem(request):
    data = json.loads(request.data)
    productId = data['productId']
    action = data['action']

    print('Action:' ,action)
    print('productId:', productId)
    return JsonResponse('Item was added', safe=False)