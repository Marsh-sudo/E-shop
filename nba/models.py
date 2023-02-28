from django.db import models

# Create your models here.
class NBACategory(models.Model):
    name = models.CharField(max_length=60)
    thumbnail = models.ImageField(upload_to="images/", blank=True)
  
    @staticmethod
    def get_all_categories():
        return NBACategory.objects.all()
  
    def __str__(self):
        return self.name

class NBAProduct(models.Model):
    name = models.CharField(max_length=80)
    price = models.IntegerField(default=0)
    category = models.ForeignKey(NBACategory, on_delete=models.CASCADE, default=1)
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    quantity = models.IntegerField(default=0)
    digital = models.BooleanField(default=False,null=True, blank=True)
    image = models.ImageField(upload_to='images/',blank=True)

    def __str__(self):
        return self.name
  
    @staticmethod
    def get_products_by_id(ids):
        return NBAProduct.objects.filter(id__in=ids)
  
    @staticmethod
    def get_all_products():
        return NBAProduct.objects.all()
  
    @staticmethod
    def get_all_products_by_categoryid(category_id):
        if category_id:
            return NBAProduct.objects.filter(category=category_id)
        else:
            return NBAProduct.get_all_products()