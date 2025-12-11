from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

class Item(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="items_added"
    )
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='itemsItem'  
    )
    # The original deposit amount (History)
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    # NEW: The remaining money in this specific deposit (Spendable)
    current_balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        default=Decimal('0.00')
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # On creation, if balance is 0, assume it's a new deposit equal to amount
        if not self.pk and self.current_balance == 0:
            self.current_balance = self.amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.current_balance}/{self.amount} UGX"

# ... (ToBuy and Budget models remain unchanged)
class ToBuy(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="tobuy_added"
    )
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='itemsToBuy'
    )
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.amount} UGX"
    
class Budget(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="budget_added"
    )
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='itemsBudget'
    )
    amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    type = models.CharField(max_length=200, default='Daily')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_amount(self):
        return sum(item.amount for item in self.items.all())

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.amount} UGX"