from django.db import models
from appuser.models import AdminUser, CrewMember

FLIGHT_PERMITS = [
    ('PPL', 'Private Pilot License'),
    ('CPL', 'Commercial Pilot License'),
    ('ATPL', 'Airline Transport Pilot License'),
    ('HPL', 'Helicopter Pilot License'),
    ('GPL', 'Glider Pilot License'),
]

FLIGHT_STATUS = [
    ('SCHEDULED', 'Scheduled'),
    ('DELAYED', 'Delayed'),
    ('CANCELLED', 'Cancelled'),
    ('COMPLETED', 'Completed'),
    ('IN_PROGRESS', 'In Progress'),
]

# Create your models here.
class Flights(models.Model):
    flight_no = models.CharField(unique=True, primary_key=True, max_length=50)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    airline_name = models.CharField(max_length=200)
    airline_code = models.CharField(max_length=50)
    airline_type = models.CharField(max_length=20)
    flight_date = models.DateTimeField()
    arrive_date = models.DateTimeField()
    flight_time = models.CharField(max_length=20)
    flight_permit = models.CharField(max_length=10, choices=FLIGHT_PERMITS)
    aircraft_type = models.CharField(max_length=100, null=True, blank=True)
    total_seats = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=FLIGHT_STATUS, default='SCHEDULED')
    crew_members = models.ManyToManyField(CrewMember, through='FlightCrews')

    def __str__(self):
        return f"{self.flight_no} - {self.origin} to {self.destination}"


CREW_STATUS = [
    ('SUCCESS', 'Success'),
    ('CAN_REQ', 'Cancellation Request'),
    ('CAN_REJ', 'Rejected Cancellation Request'),
    ('CAN', 'Canceled'),
]

CREW_ROLES = [
    ('PI', 'Pilot'),
    ('CO-PI', 'Co-Pilot'),
    ('FL-EN', 'Flight Engineer'),
    ('FL-ATE', 'Flight Attendant'),
]

class FlightCrews(models.Model):
    flight = models.ForeignKey(Flights, on_delete=models.CASCADE)
    crew_member = models.ForeignKey(CrewMember, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=CREW_ROLES)
    status = models.CharField(max_length=20, choices=CREW_STATUS, default='SUCCESS')
    assigned_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('flight', 'crew_member')

    def __str__(self):
        return f"{self.crew_member} - {self.role} in {self.flight}"
