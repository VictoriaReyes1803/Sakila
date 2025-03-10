from rest_framework.routers import DefaultRouter
from .views import *

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

urlpatterns = router.urls
