from django.shortcuts import render, redirect
from django.db.models import Sum
from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

# Import your models
from .models import Category, Item, Budget

# Import your serializers
# Ensure these exist in your serializers.py
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer,
    CategorySerializer, 
    CategoryListSerializer, 
    ItemSerializer,
    BudgetSerializer
)

# ==========================================
# HTML/Template Views
# ==========================================

def index(request):
    return render(request, 'index.html')

def budget_view(request):
    """Renders the HTML page for budgets"""
    budgets = Budget.objects.all().order_by('-created_at')
    context = {'budget': budgets}
    return render(request, 'budget.html', context)

def item_view(request):
    """
    Renders the HTML page for items.
    This corresponds to the /items URL if mapped in urls.py for the browser.
    """
    items = Item.objects.all().order_by('-created_at')
    context = {'items': items}
    return render(request, 'item.html', context)

def category_view(request):
    """Renders the HTML page for categories"""
    categories = Category.objects.all()
    # Calculate global total for display if needed
    total_assets = Item.objects.aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'categories': categories,
        'total_assets': total_assets
    }
    return render(request, 'category.html', context)

def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

@api_view(['POST'])
@permission_classes([AllowAny]) 
def add_category(request):
    """
    Hybrid view: Accepts POST request to add category 
    and redirects back to the HTML view.
    """
    name = request.POST.get('name')
    description = request.POST.get('description', '')
    
    if name:
        Category.objects.create(name=name, description=description)
        return redirect('category_view') 
    
    return redirect('category_view')

# ==========================================
# API ViewSets (DRF)
# ==========================================

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Categories.
    """
    permission_classes = [AllowAny] # Changed to AllowAny based on your snippet
    queryset = Category.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer

    @action(detail=False, methods=['get'])
    def total_assets(self, request):
        """Returns the sum of amounts of ALL items in the database"""
        total = Item.objects.aggregate(total=Sum('amount'))['total'] or 0
        return Response({'total_assets': total})

class ItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Items.
    To return items on /api/items/ ensure this is registered in urls.py router.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSerializer
    queryset = Item.objects.all()
    
    def get_queryset(self):
        """
        Optionally restricts the returned items to a given category,
        or filters by the logged-in user if you want strict privacy.
        """
        queryset = Item.objects.all()
        
        # Filter by Category ID if provided in URL (e.g., ?category=1)
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # Optional: Uncomment the lines below to only show items belonging to the logged-in user
        # if self.request.user.is_authenticated:
        #     queryset = queryset.filter(user=self.request.user)
            
        return queryset
    
    def perform_create(self, serializer):
        """Automatically attach the logged-in user to new items"""
        serializer.save(user=self.request.user)

class BudgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Budgets.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BudgetSerializer
    queryset = Budget.objects.all()
    
    def get_queryset(self):
        queryset = Budget.objects.all()
        
        # Filter by Category ID
        category_id = self.request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        return queryset
    
    def perform_create(self, serializer):
        """Automatically attach the logged-in user to new budget entries"""
        serializer.save(user=self.request.user)

# ==========================================
# Authentication API Views
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register a new user via API"""
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
    """Login user via API and return JWT tokens"""
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
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get current authenticated user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)