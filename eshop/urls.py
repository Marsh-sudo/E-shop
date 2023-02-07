from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import ProductListView,CreateStripeCheckoutSessionView

urlpatterns = [
    path("", ProductListView.as_view(), name="product-list"),
    path("category/<int:id>",views.product,name="product-detail"),
    path(
        "create-checkout-session/<int:pk>/",
        CreateStripeCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("cart/",views.cart,name="cart"),
    
]
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)