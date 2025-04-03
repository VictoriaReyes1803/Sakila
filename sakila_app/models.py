
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import jwt
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email debe ser proporcionado')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    roles = [
        ('admin', 'Admin'),
        ('engineer', 'Engineer'),
        ('technician', 'Technician'),
    ]
    email = models.EmailField(unique=True, max_length=150)
    username = models.CharField(unique=True, max_length=100)
    no_empleado = models.CharField(max_length=10, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, null=True)
    rol = models.CharField(max_length=10, choices=roles)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    code = models.CharField(max_length=100, null=True, blank=True)
    reset_token = models.CharField(max_length=100, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username','no_empleado', 'nombre', 'apellido_paterno', 'apellido_materno', 'rol']

    def __str__(self):
        return self.email + " - " + self.rol
    
    def generate_reset_token(self):
        """Genera un token JWT para restablecimiento de contraseña."""
        expiration = timezone.now() + timedelta(minutes=60)  
        token = jwt.encode({
            'user_id': self.id,
            'exp': int(expiration.timestamp())
        }, settings.SECRET_KEY, algorithm='HS256')
        return token

    def verify_reset_token(self, token):
        """Verifica la validez del token JWT para restablecimiento de contraseña."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            return payload['user_id'] == self.id  
        except jwt.ExpiredSignatureError:
            return False
        except (jwt.DecodeError, jwt.InvalidTokenError):
            return False
    def set_password(self, raw_password):
        self.password = make_password(raw_password)




class Actor(models.Model):
    actor_id = models.SmallAutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'actor'


class Address(models.Model):
    address_id = models.SmallAutoField(primary_key=True)
    address = models.CharField(max_length=50)
    address2 = models.CharField(max_length=50, blank=True, null=True)
    district = models.CharField(max_length=20)
    city = models.ForeignKey('City', models.DO_NOTHING)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=20)
    location = models.TextField()
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'address'


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'category'


class City(models.Model):
    city_id = models.SmallAutoField(primary_key=True)
    city = models.CharField(max_length=50)
    country = models.ForeignKey('Country', models.DO_NOTHING)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'city'


class Country(models.Model):
    country_id = models.SmallAutoField(primary_key=True)
    country = models.CharField(max_length=50)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'country'


class Customer(models.Model):
    customer_id = models.SmallAutoField(primary_key=True)
    store = models.ForeignKey('Store', models.DO_NOTHING)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=50, blank=True, null=True)
    address = models.ForeignKey(Address, models.DO_NOTHING)
    active = models.IntegerField()
    create_date = models.DateTimeField()
    last_update = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'customer'


class Film(models.Model):
    film_id = models.SmallAutoField(primary_key=True)
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    release_year = models.TextField(blank=True, null=True)  # This field type is a guess.
    language = models.ForeignKey('Language', models.DO_NOTHING)
    original_language = models.ForeignKey('Language', models.DO_NOTHING, related_name='film_original_language_set', blank=True, null=True)
    rental_duration = models.PositiveIntegerField()
    rental_rate = models.DecimalField(max_digits=4, decimal_places=2)
    length = models.PositiveSmallIntegerField(blank=True, null=True)
    replacement_cost = models.DecimalField(max_digits=5, decimal_places=2)
    rating = models.CharField(max_length=5, blank=True, null=True)
    special_features = models.CharField(max_length=54, blank=True, null=True)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'film'


class FilmActor(models.Model):
    actor = models.OneToOneField(Actor, models.DO_NOTHING, primary_key=True)  # The composite primary key (actor_id, film_id) found, that is not supported. The first column is selected.
    film = models.ForeignKey(Film, models.DO_NOTHING)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'film_actor'
        unique_together = (('actor', 'film'),)


class FilmCategory(models.Model):
    film = models.OneToOneField(Film, models.DO_NOTHING, primary_key=True)  # The composite primary key (film_id, category_id) found, that is not supported. The first column is selected.
    category = models.ForeignKey(Category, models.DO_NOTHING)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'film_category'
        unique_together = (('film', 'category'),)


class FilmText(models.Model):
    film_id = models.PositiveSmallIntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'film_text'


class Inventory(models.Model):
    inventory_id = models.AutoField(primary_key=True)
    film = models.ForeignKey(Film, models.DO_NOTHING)
    store = models.ForeignKey('Store', models.DO_NOTHING)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'inventory'


class Language(models.Model):
    language_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'language'


class Payment(models.Model):
    payment_id = models.SmallAutoField(primary_key=True)
    customer = models.ForeignKey(Customer, models.DO_NOTHING)
    staff = models.ForeignKey('Staff', models.DO_NOTHING)
    rental = models.ForeignKey('Rental', models.DO_NOTHING, blank=True, null=True)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    payment_date = models.DateTimeField()
    last_update = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment'


class Rental(models.Model):
    rental_id = models.AutoField(primary_key=True)
    rental_date = models.DateTimeField()
    inventory = models.ForeignKey(Inventory, models.DO_NOTHING)
    customer = models.ForeignKey(Customer, models.DO_NOTHING)
    return_date = models.DateTimeField(blank=True, null=True)
    staff = models.ForeignKey('Staff', models.DO_NOTHING)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'rental'
        unique_together = (('rental_date', 'inventory', 'customer'),)


class Roles(models.Model):
    id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=45, null=False)

    class Meta:
        managed = False
        db_table = 'roles'

class StaffManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class Staff(AbstractBaseUser):
    staff_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    address = models.ForeignKey(Address, models.DO_NOTHING)
    picture = models.TextField(blank=True, null=True)
    email = models.CharField(max_length=50, blank=False, null=False)
    store = models.ForeignKey('Store', on_delete=models.CASCADE,related_name='staff_members')
    active = models.IntegerField(default=0)
    username = models.CharField(max_length=16)
    password = models.CharField(max_length=128, blank=False, null=False)
    last_update = models.DateTimeField()
    role_id = models.ForeignKey(Roles, models.DO_NOTHING, null=False)
    last_login = None

    @property
    def is_active(self):
        return bool(self.active)

    @property
    def is_authenticated(self):
        return True

    objects = StaffManager()

    USERNAME_FIELD = 'email'

    class Meta:
        managed = False
        db_table = 'staff'


class Store(models.Model):
    store_id = models.AutoField(primary_key=True)
    manager_staff = models.OneToOneField(Staff, on_delete=models.CASCADE,related_name='managed_store')
    address = models.ForeignKey(Address, models.DO_NOTHING)
    last_update = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'store'
