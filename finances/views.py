from rest_framework import viewsets, status
from django.db.models import Sum
from .models import Category, Item, Budget
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, redirect
from .serializers import UserRegistrationSerializer, UserSerializer
from .serializers import (
    CategorySerializer, 
    CategoryListSerializer, 
    ItemSerializer,
    BudgetSerializer
)

def index(request):
     return render(request, 'index.html')
def budget_view(request):
    budget = Budget.objects.all()
    context = {'budget': budget}
    return render(request, 'budget.html', context)
def category_view(request):
       categories = Category.objects.all()
       print(f"Categories found: {categories.count()}")  # Add this
       context = {'categories': categories}
       return render(request, 'category.html', context)
def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

@api_view(['POST'])
@permission_classes([AllowAny])  # Or use IsAuthenticated if needed
def add_category(request):
    """Add a new category"""
    name = request.POST.get('name')
    
    if name:
        Category.objects.create(name=name)
        return redirect('category_view')  # Redirect back to category page
    
    return redirect('category_view')

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer

    @action(detail=False, methods=['get'])
    def total_assets(self, request):
        total = Item.objects.aggregate(total=Sum('amount'))['total'] or 0
        return Response({'total_assets': total})

class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    
    def get_queryset(self):
        queryset = Item.objects.all()
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset
    
    def perform_create(self, serializer):
        """Automatically attach the logged-in user to new items"""
        serializer.save(user=self.request.user)

class BudgetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    
    def get_queryset(self):
        queryset = Budget.objects.all()
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset
    
    def perform_create(self, serializer):
        """Automatically attach the logged-in user to new items"""
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user"""
    from django.contrib.auth import authenticate
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    
    return Response(
        {'error': 'Invalid credentials'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['GET'])
def get_user_profile(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)