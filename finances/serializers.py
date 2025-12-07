from rest_framework import serializers
from .models import Category, Item, Budget
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


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
    total_amount = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        read_only=True
    )
    items_count = serializers.IntegerField(source='itemsItem.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'total_amount', 
                  'items_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CategoryListSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        read_only=True
    )
    items_count = serializers.IntegerField(source='itemsItem.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'total_amount', 'items_count']


class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'category', 'category_name', 'amount', 
                  'description', 'user', 'user_name', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Budget
        fields = ['id', 'name', 'category', 'category_name', 'amount', 
                  'description','type', 'user', 'user_name', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class CategoryDetailSerializer(serializers.ModelSerializer):
    """Detailed category view with all items"""
    items = ItemSerializer(many=True, read_only=True, source='itemsItem')
    budgets = BudgetSerializer(many=True, read_only=True, source='itemsBudget')
    total_amount = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        read_only=True
    )
    items_count = serializers.IntegerField(source='itemsItem.count', read_only=True)
    budgets_count = serializers.IntegerField(source='itemsBudget.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'items', 'budgets', 'total_amount', 
                  'items_count', 'budgets_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ToBuySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'name', 'category', 'category_name', 'amount', 
                  'description', 'user', 'user_name', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']