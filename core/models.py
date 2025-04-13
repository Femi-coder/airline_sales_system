from django.db import models

# Create your models here.
from django.db import models

class Customer(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)

class Admin(models.Model):
    name = models.CharField(max_length=100)
    access_level = models.CharField(max_length=50)

class Staff(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)

class Destination(models.Model):
    city = models.CharField(max_length=100)
    airport_code = models.CharField(max_length=10)

class Flight(models.Model):
    flight_number = models.CharField(max_length=50)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    base_price = models.FloatField()
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE)

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_date = models.DateField(auto_now_add=True)
    total_price = models.FloatField()
    admin = models.ForeignKey(Admin, on_delete=models.SET_NULL, null=True, blank=True)
    staff = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, blank=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.FloatField()