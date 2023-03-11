from django.shortcuts import render,redirect
import stripe
import json
import datetime
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
from django.db.models import Q

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
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartitems = order.get_cart_items

    else:
        items = []
        order = {"get_cart_items": 0,"get_cart_total":0}
        cartitems = order['get_cart_items']
    items = Category.objects.get(id=id)
    product = Product.objects.filter(category=items)
    return render(request,"product_detail.html",{"items":items,"products":product,"cartitems":cartitems})

def cart(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartitems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_items": 0,"get_cart_total":0,"shipping":False}
        cartitems = order['get_cart_items']
    context = {'items':items,'order':order,"cartitems":cartitems}
    return render(request,"cart.html",context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartitems = order.get_cart_items

    else:
        items = []
        order = {"get_cart_items": 0,"get_cart_total":0}
        cartitems = order.get_cart_items
    context = {'items':items,'order':order,"cartitems":cartitems,"shipping":False}
    return render(request,"checkout.html",context)

class CreateStripeCheckoutSessionView(View):
    """
    Create a checkout session and redirect the user to Stripe's checkout page
    """

    def post(self, request, *args, **kwargs):
        price = Order.objects.get(id=self.kwargs["pk"])

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(price.get_cart_total),
                        "product_data": {
                            "name": price.customer,
                            "description": price.date_ordered,
                            "images": [
                                f"{settings.BACKEND_DOMAIN}/{price.complete}"
                            ],
                        },
                    },
                    "quantity": price.get_cart_items,
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
    #the request method is checked to make sure it is a POST request
    if request.method == "POST":
        #the request body is accessed using request.body, which contains the raw request payload
        data = request.body
        # data is a bytes-like object, so you might want to convert it to a dictionary or a string
        data = data.decode('utf-8')
        # parse the JSON data
        data = json.loads(data)
         # now you can access the data as a dictionary
        productId = data['productId']
        action = data['action']
        print('productId',productId)
        print('action',action)

        customer = request.user
        product = Product.objects.get(id=productId)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

        orderItems = OrderItem.objects.filter(order=order,product=product)
        if not orderItems.exists():
            orderItem = OrderItem.objects.create(order=order,product=product)
        else:
            orderItem = orderItems.last() 
       
        # orderItem, created = OrderItem.objects.get_or_create(order=order,product=product)

        if action == "add":
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == "remove":
            orderItem.quantity = (orderItem.quantity - 1)
        
        orderItem.save()

        if orderItem.quantity <= 0:
            orderItem.delete()

        # return a JSON response
        return JsonResponse({'message': 'Data received'},safe=False)
    else:
        return JsonResponse({'error': 'Bad request'}, status=400)
    
    
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

def searchposts(request):
    if request.method == 'GET':
        query= request.GET.get('q')

        submitbutton= request.GET.get('submit')
        

        if query is not None:
            lookups= Q(name__icontains=query) | Q(price__icontains=query)

            results= Product.objects.filter(lookups).distinct()

            context={'results': results,
                     'submitbutton': submitbutton}

            return render(request, 'search.html', context)

        else:
            return render(request, 'search.html')

    else:
        return render(request, 'search.html')


class SuccessView(TemplateView):
    template_name = "success.html"

class CancelView(TemplateView):
    template_name = "cancel.html"


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    if request.method == "POST":
        data = request.body
        # data is a bytes-like object, so you might want to convert it to a dictionary or a string
        data = data.decode('utf-8')
        # parse the JSON data
        data = json.loads(data)

    if request.user.is_authenticated:
        customer = request.user
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
		        order=order,
		        address=data['shipping']['address'],
		        city=data['shipping']['city'],
		        state=data['shipping']['state'],
		        zipcode=data['shipping']['zipcode'],
            )

    else:
        print('User is not logged in..')
    return JsonResponse("Payment complete",safe=False)


def review(request,id):
    products = Product.objects.get(id=id)
    comments = Review.objects.filter(product=products)
    return render(request,"reviews.html",{"comments":comments})

def comment(request):
    if request.method == "POST":
        data = request.body
        # data is a bytes-like object, so you might want to convert it to a dictionary or a string
        data = data.decode('utf-8')
        # parse the JSON data
        data = json.loads(data)

    if request.user.is_authenticated:
        customer = request.user
        comment , created = Review.objects.get_or_create(customer=customer, complete=False)
        commentId = data['form']['comment']
        
    return JsonResponse("Comments added", safe=False)

