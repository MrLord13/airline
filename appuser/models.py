from django.db import models
from django.contrib.auth.models import AbstractUser
from appuser.myusermanager import AdminUserManager
from core import settings

# Create your models here.
CREW_ROLE = [
    ("PI", "Pilot"),
    ("CO-PI", "Co-Pilot"),
    ("FL-EN", "Flight Engineer"),
    ("FL-ATE", "Flight Attendant")
]

class AdminUser(AbstractUser):
    username = models.CharField(unique=True, max_length=50)
    email = models.EmailField(unique=True, max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)  # All admin users are staff
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    objects = AdminUserManager()

    def __str__(self):
        return self.first_name + " " + self.last_name


class CrewMember(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True, max_length=50)
    role = models.CharField(max_length=10, choices=CREW_ROLE)
    expertise_level = models.IntegerField(default=None, null=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    availability_time = models.TextField(
        help_text="Enter your availability time (e.g., Monday-Friday 9:00-17:00)",
        null=True,
        blank=True
    )
    location = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_role_display()}"
