
from .models import *

from rest_framework import serializers

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = ['id', 'role_name'] 


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','email', 'nombre', 'username','no_empleado','apellido_paterno','apellido_materno', 'rol', 'password', 'is_active', 'is_staff', 'profile_picture']
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)  
            validated_data.pop('password')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    
          
class SendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=100)

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=100)
    new_password = serializers.CharField(write_only=True)


class ResetPasswordResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    
   

class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = '__all__'

class FilmActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilmActor
        fields = '__all__'

class FilmCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FilmCategory
        fields = '__all__'

class FilmTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilmText
        fields = '__all__'

class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'

class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'
        
        


class StaffSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    store = StoreSerializer(read_only=True)
    role = RolSerializer(read_only=True)
    
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), source='address', write_only=True
    )
    store_id = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all(), source='store', write_only=True
    )
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=Roles.objects.all(), source='role', write_only=True
    )
    
    class Meta:
        model = Staff
        fields = [
            'staff_id', 'first_name', 'last_name', 'email', 'username',
            'password', 'active', 'picture', 'last_update', 'otp_code', 'otp_expires_at',
            'address', 'store', 'role',     # salida (read-only)
            'address_id', 'store_id', 'role_id'  # entrada (write-only)
        ]
        extra_kwargs = {'password': {'write_only': True}}


    def update(self, instance, validated_data):
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)  
            validated_data.pop('password')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
 