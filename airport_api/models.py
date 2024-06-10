import pathlib
import uuid
from datetime import datetime
from typing import Type
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

from user.models import User


class Crew(models.Model):
    first_name = models.CharField(max_length=63)
    last_name = models.CharField(max_length=63)
    flying_hours = models.FloatField(default=0)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Airport(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True
    )
    closest_big_city = models.CharField(
        max_length=255
    )

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
    def km_to_miles(self) -> float:
        return self.distance / 1.6

    @property
    def distance_in_km_and_miles(self) -> str:
        return f"{self.distance} km / {self.km_to_miles} miles"

    def __str__(self):
        return (
            f"{self.source.name} -> {self.destination.name}. "
            f"Distance : {self.distance} km."
        )


class AirplaneType(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


def airplane_image_path(instance: "Airplane", filename: str) -> pathlib.Path:
    filename = (
        f"{slugify(instance.name)}-{uuid.uuid4()}" + pathlib.Path(filename).suffix
    )
    return pathlib.Path("upload/airplanes") / pathlib.Path(filename)


class Airplane(models.Model):
    name = models.CharField(
        max_length=255,
        unique=True
    )
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.CASCADE,
        related_name="airplanes"
    )
    image = models.ImageField(
        null=True,
        upload_to=airplane_image_path
    )

    class Meta:
        ordering = ["name"]

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

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
    accounted = models.BooleanField(
        default=False
    )

    @staticmethod
    def has_overlapping_crew(
        crew_ids: list[int],
        departure_time: datetime,
        arrival_time: datetime
    ) -> bool:
        return Flight.objects.filter(
            crews__id__in=crew_ids,
            departure_time__lt=arrival_time,
            arrival_time__gt=departure_time,
        ).exists()

    @property
    def flight_time(self) -> str:
        return str(self.arrival_time - self.departure_time)

    @property
    def flight_is_over(self) -> bool:
        now = timezone.now()
        return now >= self.arrival_time

    def __str__(self):
        return (
            f"{self.route.source.name} -> {self.route.destination.name}. "
            f"Distance: {self.route.distance} km. "
            f"Flight time: {self.flight_time} "
            f"Flight is over: {self.flight_is_over} "
        )


class Order(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True
    )
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

    class Meta:
        ordering = ["seat"]

    @staticmethod
    def validate_seat_and_rows(
        seat: int,
        num_seats: int,
        row: int,
        num_rows: int,
        error_to_raise: Type[Exception],
    ):
        if not (1 <= seat <= num_seats):
            raise error_to_raise(
                {"seat": f"seat must be in a range of " f"[1,{num_seats}],not [{seat}]"}
            )
        elif not (1 <= row <= num_rows):
            raise error_to_raise(
                {"row": f"row must be in a range of " f"[1,{num_rows}],not [{row}]"}
            )

    def clean(self):
        Ticket.validate_seat_and_rows(
            self.seat,
            self.flight.airplane.seats_in_row,
            self.row,
            self.flight.airplane.rows,
            ValueError,
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
