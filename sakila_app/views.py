from django.shortcuts import render
from django.db import transaction
from rest_framework import viewsets,status
from .models import *
from rest_framework.response import Response
from .serializers import *

class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
  
    def destroy(self, request, *args, **kwargs):
        actor = self.get_object()

        FilmActor.objects.filter(actor=actor).delete()

        return super().destroy(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        actor = self.get_object()

        FilmActor.objects.filter(actor=actor).delete()

        return super().destroy(request, *args, **kwargs)

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    def destroy(self, request, *args, **kwargs):
        address = self.get_object()

        # ✅ Buscar las tiendas asociadas a esta dirección
        stores = Store.objects.filter(address=address)
        total_rentals = 0

        # ✅ Contar todas las rentas relacionadas con los clientes
        for store in stores:
            customers = Customer.objects.filter(store=store)
            for customer in customers:
                total_rentals += Rental.objects.filter(customer=customer).count()

        
        if total_rentals > 0:
            return Response({
                "error": "No se puede eliminar la dirección.",
                "reason": "Existen rentas asociadas a esta dirección.",
                "total_rentals": total_rentals
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Si no hay más de 3 rentas, proceder a eliminar todo
        with transaction.atomic():
            # 1. Eliminar pagos
            for store in stores:
                customers = Customer.objects.filter(store=store)
                for customer in customers:
                    # Eliminar pagos asociados al alquiler
                    rentals = Rental.objects.filter(customer=customer)
                    for rental in rentals:
                        Payment.objects.filter(rental=rental).delete()

                    # Eliminar rentas y clientes
                    rentals.delete()
                customers.delete()

            # 2. Eliminar las tiendas
            stores.delete()

            # 3. Eliminar la dirección
            return super().destroy(request, *args, **kwargs)




class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def destroy(self, request, *args, **kwargs):
        category = self.get_object()

        # ✅ Buscar las películas asociadas a esta categoría
        film_categories = FilmCategory.objects.filter(category=category)
        total_films = film_categories.count()

       
        if total_films > 0:
            return Response({
                "error": "No se puede eliminar la categoría.",
                "reason": "Existen películas asociadas a esta categoría.",
                "total_films": total_films
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ Si hay 5 películas o menos, proceder a eliminar
        with transaction.atomic():
            # 1. Eliminar la relación FilmCategory
            film_categories.delete()

            # 💡 OPCIONAL: Si deseas eliminar las películas también, descomenta esto.
            # Film.objects.filter(film_category__category=category).delete()

            # 2. Eliminar la categoría
            return super().destroy(request, *args, **kwargs)



class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    def destroy(self, request, *args, **kwargs):
        city = self.get_object()
        
        # Verificar si hay direcciones asociadas a esta ciudad
        addresses = Address.objects.filter(city=city)
        total_addresses = addresses.count()

        # Si hay direcciones asociadas, bloquear la eliminación
        if total_addresses > 0:
            return Response({
                "error": "No se puede eliminar la ciudad.",
                "reason": "Existen direcciones asociadas a esta ciudad.",
                "total_addresses": total_addresses
            }, status=status.HTTP_400_BAD_REQUEST)

        # Si no hay direcciones asociadas, proceder con la eliminación
        return super().destroy(request, *args, **kwargs)

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    def destroy(self, request, *args, **kwargs):
        country = self.get_object()

        # Verificar si hay ciudades asociadas a este país
        cities = City.objects.filter(country=country)
        total_cities = cities.count()

        # Si hay ciudades asociadas, eliminarlas primero
        if total_cities > 0:
            # Eliminar las ciudades asociadas al país
            return Response({
                "error": "No se puede eliminar el país.",
                "reason": "Existen ciudades asociadas a este país.",
                "total_cities": total_cities
            }, status=status.HTTP_400_BAD_REQUEST)

        # Ahora proceder con la eliminación del país
        return super().destroy(request, *args, **kwargs)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    def destroy(self, request, *args, **kwargs):
        customer = self.get_object()

        # Eliminar los pagos asociados al cliente
        payments = Payment.objects.filter(customer=customer)
        total_payments = payments.count()
        if total_payments > 0:
            return Response({
                "error": "No se puede eliminar el cliente.",
                "reason": "Existen pagos asociados a este cliente.",
                "total_payments": total_payments
            }, status=status.HTTP_400_BAD_REQUEST)


        # Ahora proceder con la eliminación del cliente
        return super().destroy(request, *args, **kwargs)



class FilmViewSet(viewsets.ModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer
    def destroy(self, request, *args, **kwargs):
        film = self.get_object()
        
        film_actors = FilmActor.objects.filter(film=film)
        total_actors = film_actors.count()
        if total_actors > 0:
            return Response({
                "error": "No se puede eliminar la película.",
                "reason": "Existen actores asociados a esta película.",
                "total_actors": total_actors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        return super().destroy(request, *args, **kwargs)

class FilmActorViewSet(viewsets.ModelViewSet):
    queryset = FilmActor.objects.all()
    serializer_class = FilmActorSerializer

class FilmCategoryViewSet(viewsets.ModelViewSet):
    queryset = FilmCategory.objects.all()
    serializer_class = FilmCategorySerializer

class FilmTextViewSet(viewsets.ModelViewSet):
    queryset = FilmText.objects.all()
    serializer_class = FilmTextSerializer

class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    def destroy(self, request, *args, **kwargs):
        inventory = self.get_object()
        rentals = Rental.objects.filter(inventory=inventory)
        total_rentals = rentals.count()
        if total_rentals > 0:
            return Response({
                "error": "No se puede eliminar el inventario.",
                "reason": "Existen rentas asociadas a este inventario.",
                "total_rentals": total_rentals
            }, status=status.HTTP_400_BAD_REQUEST)
            
        return super().destroy(request, *args, **kwargs)

class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    def destroy(self, request, *args, **kwargs):
        language = self.get_object()
        films = Film.objects.filter(language=language)
        total_films = films.count()
        if total_films > 0:
            return Response({
                "error": "No se puede eliminar el idioma.",
                "reason": "Existen películas asociadas a este idioma.",
                "total_films": total_films
            }, status=status.HTTP_400_BAD_REQUEST)
            
        return super().destroy(request, *args, **kwargs)
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class RentalViewSet(viewsets.ModelViewSet):
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    def destroy(self, request, *args, **kwargs):
        staff = self.get_object()
        payments = Payment.objects.filter(staff=staff)
        total_payments = payments.count()
        if total_payments > 0:
            return Response({
                "error": "No se puede eliminar el staff.",
                "reason": "Existen pagos asociados a este staff.",
                "total_payments": total_payments
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    def destroy(self, request, *args, **kwargs):
        store = self.get_object()
        customers = Customer.objects.filter(store=store)
        total_customers = customers.count()
        if total_customers > 0:
            return Response({
                "error": "No se puede eliminar la tienda.",
                "reason": "Existen clientes asociados a esta tienda.",
                "total_customers": total_customers
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)
