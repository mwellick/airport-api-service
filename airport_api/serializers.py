from django.db import transaction
from rest_framework import serializers
from .models import (
    Crew,
    Country,
    City,
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
            "last_name",
        ]


class CrewListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = [
            "id",
            "first_name",
            "last_name",
        ]


class CrewRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = [
            "full_name",
            "flying_hours"
        ]


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = [
            "id",
            "name"
        ]


class CountryListSerializer(CountrySerializer):
    class Meta(CountrySerializer.Meta):
        pass


class CountryRetrieveSerializer(CountryListSerializer):
    class Meta:
        model = Country
        exclude = [
            "id"
        ]


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = [
            "id",
            "name"
        ]


class CityListSerializer(CitySerializer):
    class Meta(CitySerializer.Meta):
        pass


class CityRetrieveSerializer(serializers.ModelSerializer):
    country = serializers.CharField(
        source="country.name",
        read_only=True
    )

    class Meta:
        model = City
        fields = [
            "id",
            "name",
            "country",

        ]


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = [
            "id",
            "name",
            "closest_big_city"
        ]


class AirportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = [
            "id",
            "name",
        ]


class AirportRetrieveSerializer(serializers.ModelSerializer):
    closest_big_city = serializers.CharField(
        source="closest_big_city.name",
        read_only=True
    )
    country = serializers.CharField(
        source="closest_big_city.country.name"
    )

    class Meta:
        model = Airport
        fields = [
            "name",
            "closest_big_city",
            "country"
        ]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = [
            "id",
            "source",
            "destination",
            "distance"
        ]


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.CharField(
        source="source.name",
        read_only=True
    )
    destination = serializers.CharField(
        source="destination.name",
        read_only=True
    )

    class Meta:
        model = Route
        fields = [
            "id",
            "source",
            "destination",
        ]


class RouteRetrieveSerializer(serializers.ModelSerializer):
    source = serializers.CharField(
        source="source.name",
        read_only=True
    )
    destination = serializers.CharField(
        source="destination.name",
        read_only=True
    )

    class Meta:
        model = Route
        fields = [
            "source",
            "destination",
            "distance_in_km_and_miles",
        ]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = [
            "id",
            "name"
        ]


class AirplaneTypeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = [
            "id",
            "name"
        ]


class AirplaneTypeRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["name"]


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type"
        ]


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.CharField(
        source="airplane_type.name",
        read_only=True
    )

    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "image"
        ]


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = [
            "id",
            "image"
        ]


class AirplaneRetrieveSerializer(AirplaneSerializer):
    airplane_type = serializers.CharField(
        source="airplane_type.name",
        read_only=True
    )

    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
            "image",
        ]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "crews",
            "departure_time",
            "arrival_time"
        ]

    def create(self, validated_data):
        crews = validated_data.pop("crews", [])
        flight = Flight.objects.create(**validated_data)
        flight.crews.set(crews)
        return flight

    def update(self, instance, validated_data):
        crews = validated_data.pop("crews", [])
        instance = super().update(instance, validated_data)
        instance.crews.set(crews)
        return instance

    def validate(self, attrs):
        crews = attrs.get("crews", [])
        crew_ids = [crew.id for crew in crews]
        if Flight.has_overlapping_crew(
                crew_ids,
                attrs["departure_time"],
                attrs["arrival_time"]
        ):
            raise serializers.ValidationError(
                {
                    "detail": "One or more crew members are already assigned to another flight during this time."
                }
            )

        return attrs


class FlightListSerializer(serializers.ModelSerializer):
    airplane = serializers.CharField(source="airplane.name")
    route = RouteListSerializer()

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
        ]


class FlightRetrieveSerializer(serializers.ModelSerializer):
    airplane = serializers.CharField(source="airplane.name")
    route = RouteListSerializer()
    crews = CrewListSerializer(many=True, read_only=True)
    taken_seats = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="seat", source="flight_tickets"
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "crews",
            "taken_seats",
            "tickets_available",
            "departure_time",
            "arrival_time",
            "flight_time",
            "flight_is_over",
        ]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight"]

    def validate(self, attrs):
        flight = attrs.get("flight")
        if flight and flight.flight_is_over:
            raise serializers.ValidationError(
                {
                    "detail": "Unavailable to sell tickets for a flight that has already completed"
                }
            )

        Ticket.validate_seat_and_rows(
            attrs["seat"],
            attrs["flight"].airplane.seats_in_row,
            attrs["row"],
            attrs["flight"].airplane.rows,
            serializers.ValidationError,
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
    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "flight"
        ]


class TicketRetrieveSerializer(serializers.ModelSerializer):
    flight_info = serializers.CharField(
        source="flight",
        read_only=True
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "flight_info"
        ]


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(
        many=True,
        read_only=False,
        allow_empty=False
    )

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

    def update(self, instance, validated_data):
        tickets_data = validated_data.pop("tickets")
        instance = super().update(instance, validated_data)

        instance.tickets.all().delete()
        for ticket_data in tickets_data:
            ticket_data.pop("order", None)
            Ticket.objects.create(order=instance, **ticket_data)

        return instance


class OrderListSerializer(serializers.ModelSerializer):
    tickets = TicketListSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "tickets"
        ]


class OrderRetrieveSerializer(serializers.ModelSerializer):
    tickets = TicketRetrieveSerializer(
        read_only=True,
        many=True
    )

    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "tickets"
        ]
