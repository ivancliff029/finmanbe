from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.db import transaction # Import transaction for safe updates
from decimal import Decimal
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

# DRF Imports
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

# Import your models
from .models import Category, Item, Budget, ToBuy

# Import your serializers
from .serializers import (
    UserRegistrationSerializer, 
    UserSerializer,
    CategorySerializer, 
    CategoryListSerializer, 
    ItemSerializer,
    BudgetSerializer
)

# ==========================================
# 1. HTML/TEMPLATE VIEWS
# ==========================================

def index(request):
    return render(request, 'index.html')

def login_view(request):
    return render(request, 'login.html')

def register_view(request):
    return render(request, 'register.html')

@login_required(login_url='/auth/login/')
def budget_view(request):
    budgets = Budget.objects.filter(user=request.user).order_by('-created_at')
    categories = Category.objects.all()
    context = {'budget': budgets, 'categories': categories}
    return render(request, 'budget.html', context)

@login_required(login_url='/auth/login/')
def item_view(request):
    # Using 'items_added' related_name from your User model
    items = Item.objects.filter(user=request.user).order_by('-created_at')
    categories = Category.objects.all()
    context = {'items': items, 'categories': categories}
    return render(request, 'item.html', context)

@login_required(login_url='/auth/login/')
def category_view(request):
    categories = Category.objects.all()
    # Calculate total current balance of assets
    total_assets = Item.objects.filter(user=request.user).aggregate(total=Sum('current_balance'))['total'] or 0
    context = {'categories': categories, 'total_assets': total_assets}
    return render(request, 'category.html', context)

@login_required(login_url='/auth/login/')
@csrf_protect
def to_buy_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        amount = request.POST.get('amount')
        category_id = request.POST.get('category') 
        
        if name and amount and category_id:
            category = get_object_or_404(Category, id=category_id)
            
            ToBuy.objects.create(
                user=request.user,
                name=name,
                amount=amount,
                category=category,
                description=request.POST.get('description', '')
            )
            return redirect('to-buy') 

    items_to_buy = ToBuy.objects.filter(user=request.user).order_by('-created_at')
    categories = Category.objects.all() 
    
    context = {
        'items_to_buy': items_to_buy,
        'categories': categories
    }
    return render(request, 'to_buy.html', context)

@login_required(login_url='/auth/login/')
def delete_to_buy(request, pk):
    item = get_object_or_404(ToBuy, pk=pk, user=request.user)
    item.delete()
    return redirect('to-buy')


# ==========================================
# 2. DRF API VIEWSETS
# ==========================================

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]
    queryset = Category.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer

    @action(detail=False, methods=['get'])
    def total_assets(self, request):
        total = Item.objects.aggregate(total=Sum('current_balance'))['total'] or 0
        return Response({'total_assets': total})

    # --- NEW: WITHDRAW LOGIC (FIFO) ---
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def withdraw(self, request, pk=None):
        category = self.get_object()
        
        try:
            withdraw_amount = Decimal(str(request.data.get('amount', 0)))
        except:
            return Response({"error": "Invalid amount format"}, status=400)

        if withdraw_amount <= 0:
            return Response({"error": "Amount must be positive"}, status=400)

        # 1. Calculate Total Available Funds in this Category
        total_available = category.itemsItem.aggregate(sum=Sum('current_balance'))['sum'] or Decimal('0.00')

        if withdraw_amount > total_available:
            return Response({
                "error": f"Insufficient funds. Available: {total_available}, Requested: {withdraw_amount}"
            }, status=400)

        # 2. FIFO Strategy: Get items with balance > 0, oldest first
        items = category.itemsItem.filter(current_balance__gt=0).order_by('created_at')

        remaining_to_withdraw = withdraw_amount
        affected_items = []

        # 3. Atomic Transaction
        with transaction.atomic():
            for item in items:
                if remaining_to_withdraw <= 0:
                    break

                # Take from item: min(what's in item, what we need)
                deduction = min(item.current_balance, remaining_to_withdraw)

                item.current_balance -= deduction
                item.save()

                remaining_to_withdraw -= deduction
                
                affected_items.append({
                    "item_id": item.id,
                    "name": item.name,
                    "deducted": deduction,
                    "remaining_balance": item.current_balance
                })

        return Response({
            "message": "Withdrawal successful",
            "withdrawn_amount": withdraw_amount,
            "new_category_balance": total_available - withdraw_amount,
            "items_affected": affected_items
        })


class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ItemSerializer
    
    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # When creating an item, current_balance is handled by the model's save() method
        serializer.save(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = BudgetSerializer
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ==========================================
# 3. AUTHENTICATION API
# ==========================================

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
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
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user is not None:
        login(request, user)
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)