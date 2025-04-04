from rest_framework.routers import DefaultRouter
from .views import *
from django.urls import path,  include
from .auth_views import *

router = DefaultRouter()

router.register(r'actors', ActorViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'cities', CityViewSet)
router.register(r'countries', CountryViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'films', FilmViewSet)
router.register(r'film-actors', FilmActorViewSet)
router.register(r'film-categories', FilmCategoryViewSet)
router.register(r'film-texts', FilmTextViewSet)
router.register(r'inventories', InventoryViewSet)
router.register(r'languages', LanguageViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'rentals', RentalViewSet)
router.register(r'staffs', StaffViewSet)
router.register(r'stores', StoreViewSet)

# urlpatterns = router.urls
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-otp/', VerifyCodeView.as_view(), name='verify-otp'),
    path('user/', UserProfileView.as_view(), name='user-profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('send-recovery-email/', SendRecoveryEmailView.as_view(), name='send-recovery-email'),
    path('api/reset-password/<uidb64>/<token>/', reset_password_view, name='reset-password'),
    path('api/api/reset-password/<uidb64>/<token>/', ResetPasswordView.as_view(), name='api-reset-password'),
    
    path('', include(router.urls)),
]
