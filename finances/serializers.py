from rest_framework import serializers
from .models import Category, Item, Budget, ToBuy
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.db.models import Sum

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class CategorySerializer(serializers.ModelSerializer):
    # We use a method field to ensure we sum the CURRENT AVAILABLE balance, not the history
    total_amount = serializers.SerializerMethodField()
    items_count = serializers.IntegerField(source='itemsItem.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'total_amount', 
                  'items_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_total_amount(self, obj):
        # Sums up the 'current_balance' of all items in this category
        total = obj.itemsItem.aggregate(sum=Sum('current_balance'))['sum']
        return total if total is not None else 0.00


class CategoryListSerializer(serializers.ModelSerializer):
    total_amount = serializers.SerializerMethodField()
    items_count = serializers.IntegerField(source='itemsItem.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'total_amount', 'items_count']

    def get_total_amount(self, obj):
        total = obj.itemsItem.aggregate(sum=Sum('current_balance'))['sum']
        return total if total is not None else 0.00


class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    # Crucial: Expose current_balance so the frontend can show "Remaining / Original"
    current_balance = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = Item
        fields = ['id', 'name', 'category', 'category_name', 'amount', 'current_balance',
                  'description', 'user', 'user_name', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at', 'current_balance']


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Budget
        fields = ['id', 'name', 'category', 'category_name', 'amount', 
                  'description','type', 'user', 'user_name', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class ToBuySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ToBuy
        fields = ['id', 'name', 'category', 'category_name', 'amount', 
                  'description', 'user', 'user_name', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']