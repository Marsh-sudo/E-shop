from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .forms import LoginForm
from .views import ProductListView,CreateStripeCheckoutSessionView,RegisterView,ProfileView


urlpatterns = [
    path("", ProductListView.as_view(), name="home"),
    path('register/', RegisterView.as_view(), name='users-register'),
    path("category/<int:id>",views.product,name="product-detail"),
    path(
        "create-checkout-session/<int:pk>/",
        CreateStripeCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("cart/",views.cart,name="cart"),
    path("profile/",ProfileView.as_view(),name="profile"),
    path("Updateprofile",views.profile_update,name="Updateprofile"),
    path("login/",views.login_request,name="login")
]
if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)