from django.db import models
import datetime
from PIL import Image
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=60)
    thumbnail = models.ImageField(upload_to="images/", blank=True)
  
    @staticmethod
    def get_all_categories():
        return Category.objects.all()
  
    def __str__(self):
        return self.name

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    username = models.CharField(max_length=65)
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField()
   
    def __str__(self):
        return self.username
  
    # to save the data
    def register(self):
        self.save()
  
    @staticmethod
    def get_customer_by_email(email):
        try:
            return Customer.objects.get(email=email)
        except:
            return False
  
    def isExists(self):
        if Customer.objects.filter(email=self.email):
            return True
  
        return False

class Product(models.Model):
    name = models.CharField(max_length=80)
    price = models.IntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    quantity = models.IntegerField(default=0)
    digital = models.BooleanField(default=False,null=True, blank=True)
    image = models.ImageField(upload_to='images/',blank=True)

    def __str__(self):
        return self.name
  
    @staticmethod
    def get_products_by_id(ids):
        return Product.objects.filter(id__in=ids)
  
    @staticmethod
    def get_all_products():
        return Product.objects.all()
  
    @staticmethod
    def get_all_products_by_categoryid(category_id):
        if category_id:
            return Product.objects.filter(category=category_id)
        else:
            return Product.get_all_products()





class Order(models.Model):
    customer = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)
	

    def __str__(self):
        return str(self.id)

    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total



class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    

    
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
    

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(default='default.jpg', upload_to='profile_images')
    bio = models.TextField()

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)
        if img.height > 100 or img.width > 100:
            new_img = (20, 20)
            img.thumbnail(new_img)
            img.save(self.avatar.path)

class Review(models.Model):
    comment = models.CharField(max_length=60)
    product = models.ForeignKey(Product,on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User,on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.comment}'


class ShippingAddress(models.Model):
	customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address