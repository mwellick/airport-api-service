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


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "user"
        ]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "flight",
            "order"
        ]
