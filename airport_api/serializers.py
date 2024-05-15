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
            "airplane_type"
        ]


class AirplaneListSerializer(AirplaneSerializer):
    class Meta:
        model = Airplane
        exclude = ["id", "rows", "seats_in_row"]


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

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "distance"
        ]


class FlightRetrieveSerializer(FlightListSerializer):
    crews = CrewSerializer(many=True)

    class Meta:
        model = Flight
        fields = [
            "route",
            "airplane",
            "crews",
            "departure_time",
            "arrival_time",
            "flight_time",
            "distance"
        ]


class TicketSerializer(serializers.ModelSerializer):
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


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

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
