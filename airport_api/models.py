from typing import Type

from django.conf import settings
from django.db import models
from user.models import User


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}\n Closest big city: {self.closest_big_city}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_from"
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.CASCADE,
        related_name="routes_to"
    )
    distance = models.FloatField()

    class Meta:
        ordering = ["source"]

    @property
    def km_to_miles(self):
        return self.distance * 1.6

    @property
    def distance_km(self):
        return f"{self.distance} km / {self.km_to_miles} miles"

    def __str__(self):
        return f"{self.source.name} -> {self.destination.name}. Distance : {self.distance} km."


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}. Type: {self.airplane_type}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.CASCADE,
        related_name="route_flights"
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.CASCADE,
        related_name="airplane_flights"
    )
    crews = models.ManyToManyField(
        Crew,
        related_name="crew_flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    @property
    def flight_time(self):
        return str(self.arrival_time - self.departure_time)

    def __str__(self):
        return (
            f"{self.route.source.name} -> {self.route.destination.name}. "
            f"Distance: {self.route.distance} km. "
            f"Flight time: {self.flight_time}"
        )


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(
        Flight,
        on_delete=models.CASCADE,
        related_name="flight_tickets"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_seat_and_rows(
            seat: int,
            num_seats: int,
            row: int,
            num_rows: int,
            error_to_raise: Type[Exception]
    ):
        if not (1 <= seat <= num_seats):
            raise error_to_raise(
                {
                    "seat": f"seat must be in a range of "
                            f"[1,{num_seats}],not [{seat}]"
                }
            )
        elif not (1 <= row <= num_rows):
            raise error_to_raise(
                {
                    "row": f"row must be in a range of "
                           f"[1,{num_rows}],not [{row}]"
                }
            )

    def clean(self):
        Ticket.validate_seat_and_rows(
            self.seat,
            self.flight.airplane.seats_in_row,
            self.row,
            self.flight.airplane.rows,
            ValueError
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        self.full_clean()
        super(Ticket, self).save(
            force_insert,
            force_update,
            using,
            update_fields
        )

    def __str__(self):
        return (
            f"{self.flight.route.source.name} -> {self.flight.route.destination.name}:\n"
            f"Ordered seats: Row: {self.row}  | Seat: {self.seat}\n"
            f"Departure time: {self.flight.departure_time}\n"
            f"Arrival time: {self.flight.arrival_time}\n"
            f"Flight time: {self.flight.flight_time}\n"
        )
