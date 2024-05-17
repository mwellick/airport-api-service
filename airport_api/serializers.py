from django.db import transaction
from rest_framework import serializers
from .models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Ticket
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = [
            "id",
            "first_name",
            "last_name"
        ]


class CrewRetrieveSerializer(CrewSerializer):
    class Meta:
        model = Crew
        fields = [
            "full_name",
            "flying_hours"
        ]


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = [
            "id",
            "name",
            "closest_big_city"
        ]


class AirportListSerializer(AirportSerializer):
    class Meta:
        model = Airport
        fields = [
            "name"
        ]


class RouteSerializer(serializers.ModelSerializer):
    source = AirportListSerializer()
    destination = AirportListSerializer()

    class Meta:
        model = Route
        fields = [
            "id",
            "source",
            "destination",
        ]


class RouteListSerializer(RouteSerializer):
    class Meta:
        model = Route
        exclude = ["id", "distance"]


class RouteRetrieveSerializer(RouteListSerializer):
    class Meta:
        model = Route
        exclude = ["id"]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = [
            "id",
            "name"
        ]


class AirplaneTypeListSerializer(AirplaneTypeSerializer):
    class Meta:
        model = AirplaneType
        exclude = ["id"]


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeListSerializer()

    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",

        ]


class AirplaneListSerializer(AirplaneSerializer):
    class Meta:
        model = Airplane
        exclude = [
            "rows",
            "seats_in_row",
            "image"
        ]


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "image"]


class AirplaneRetrieveSerializer(AirplaneSerializer):
    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
            "image"

        ]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
        ]


class FlightListSerializer(serializers.ModelSerializer):
    route = RouteListSerializer()
    airplane = serializers.CharField(
        source="airplane.name",
        read_only=True
    )
    distance = serializers.CharField(
        source="route.distance",
        read_only=True
    )
    tickets_available = serializers.IntegerField(
        read_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "distance",
            "tickets_available"
        ]


class TicketSerializer(serializers.ModelSerializer):
    flight = FlightListSerializer()

    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "flight",
        ]

    def validate(self, attrs):
        Ticket.validate_seat_and_rows(
            attrs["seat"],
            attrs["flight"].airplane.seats_in_row,
            attrs["row"],
            attrs["flight"].airplane.rows,
            serializers.ValidationError
        )
        if Ticket.objects.filter(
                seat=attrs["seat"],
                row=attrs["row"],
                flight=attrs["flight"]
        ).exists():
            raise serializers.ValidationError(
                {"detail": "This seat has already been taken for the selected flight"}
            )
        return attrs


class TicketListSerializer(serializers.ModelSerializer):
    flight_info = serializers.CharField(source="flight", read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "flight_info",
        ]


class TicketRetrieveSerializer(serializers.ModelSerializer):
    airplane = serializers.CharField(
        source="flight.airplane",
        read_only=True
    )
    departure_from = serializers.CharField(
        source="flight.route.source.name",
        read_only=True
    )
    arrival_to = serializers.CharField(
        source="flight.route.destination.name",
        read_only=True
    )
    distance = serializers.CharField(
        source="flight.route.distance_km",
        read_only=True
    )
    departure_time = serializers.CharField(
        source="flight.departure_time",
        read_only=True
    )
    arrival_time = serializers.CharField(
        source="flight.arrival_time",
        read_only=True
    )
    flight_time = serializers.CharField(
        source="flight.flight_time",
        read_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            "airplane",
            "row",
            "seat",
            "departure_from",
            "arrival_to",
            "distance",
            "departure_time",
            "arrival_time",
            "flight_time"

        ]


class FlightRetrieveSerializer(FlightListSerializer):
    crews = CrewSerializer(many=True)
    taken_seats = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="seat",
        source="flight_tickets"
    )
    tickets_available = serializers.IntegerField(
        read_only=True)

    class Meta:
        model = Flight
        fields = [
            "route",
            "airplane",
            "crews",
            "departure_time",
            "arrival_time",
            "flight_time",
            "distance",
            "taken_seats",
            "tickets_available"
        ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "tickets"
        ]

    @transaction.atomic()
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)
        for ticket_data in tickets_data:
            ticket_data.pop("order", None)
            Ticket.objects.create(order=order, **ticket_data)
        return order


class OrderListSerializer(OrderSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "tickets"

        ]


class OrderRetrieveSerializer(OrderListSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)
