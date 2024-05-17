from django.db.models import Count, F, Q
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    extend_schema_view
)
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from .models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Ticket,
)
from .permissions import IsAdminAllORIsAuthenticatedOrReadOnly
from .serializers import (
    CrewSerializer,
    AirportSerializer,
    RouteSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    FlightSerializer,
    OrderSerializer,
    TicketSerializer,
    FlightListSerializer,
    RouteListSerializer,
    FlightRetrieveSerializer,
    RouteRetrieveSerializer,
    TicketListSerializer,
    TicketRetrieveSerializer,
    OrderRetrieveSerializer,
    OrderListSerializer,
    AirplaneImageSerializer,
    AirplaneRetrieveSerializer,
    AirplaneListSerializer,
    CrewRetrieveSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Get list of all crew mates",
        description="User can get a list of all crewmates"
    ),
    create=extend_schema(
        summary="Create a crew mate",
        description="Admin can create a new crewmate"
    ),
    retrieve=extend_schema(
        summary="Get a detailed info about specific crewmate",
        description="User can get specific info about crewmate"
    ),
    update=extend_schema(
        summary="Update specific info about crewmate",
        description="Admin can update information about specific crewmate"
    ),
    partial_update=extend_schema(
        summary="Partial update of specific crewmate",
        description="Admin can make a partial update of specific crewmate"
    ),
    destroy=extend_schema(
        summary="Delete a specific crewmate",
        description="Admin can delete specific crewmate"
    )
)
class CrewViewSet(ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_queryset(self):
        queryset = self.queryset
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return CrewSerializer
        elif self.action == "retrieve":
            return CrewRetrieveSerializer
        return CrewSerializer

    @extend_schema(
        methods=["GET"],
        summary="Get list of all crewmates",
        description="User can get a list of all crewmates",
        parameters=[
            OpenApiParameter(
                name="first_name",
                description="Filter crewmates by their first name",
                type=str,
                examples=[
                    OpenApiExample(
                        "Example",
                        value="Michael"
                    )
                ]
            ),
            OpenApiParameter(
                name="last_name",
                description="Filter crewmates by their last name",
                type=str,
                examples=[
                    OpenApiExample(
                        "Example",
                        value="Ellipsis"
                    )
                ]
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema_view(
    create=extend_schema(
        summary="Create an airport",
        description="Admin can create an airport"
    ),
    retrieve=extend_schema(
        summary="Get a detailed info about specific airport",
        description="User can get a detailed info about specific airport"
    ),
    update=extend_schema(
        summary="Update info about specific airport",
        description="Admin can update information about specific airport"
    ),
    partial_update=extend_schema(
        summary="Partial update of specific airport",
        description="Admin can make a partial update of specific airport"
    ),
    destroy=extend_schema(
        summary="Delete a specific airport",
        description="Admin can delete specific airport"
    )
)
class AirportViewSet(ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminAllORIsAuthenticatedOrReadOnly]

    @extend_schema(
        methods=["GET"],
        summary="Get list of airports",
        description="User can get a list of airports",
        parameters=[
            OpenApiParameter(
                name="name",
                description="Filter by airport name",
                type=str,
                examples=[
                    OpenApiExample(
                        "Example",
                        value="Paris"
                    )
                ]
            ),
            OpenApiParameter(
                name="closest_city",
                description="Filter airport by closest big city",
                type=str,
                examples=[
                    OpenApiExample(
                        "Example",
                        value="Brussels"
                    )
                ]
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        city = self.request.query_params.get("closest_city")
        if name:
            queryset = queryset.filter(name__icontains=name)
        if city:
            queryset = queryset.filter(closest_big_city__icontains=city)
        return queryset


class RouteViewSet(ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_queryset(self):
        queryset = self.queryset
        source = self.request.query_params.get("from")
        destination = self.request.query_params.get("to")
        if source:
            queryset = queryset.filter(
                source__name__icontains=source
            )
        if destination:
            queryset = queryset.filter(
                destination__name__icontains=destination
            )
        if self.action in ("list", "retrieve"):
            return queryset.select_related()
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RouteSerializer
        elif self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteListSerializer


class AirplaneTypeViewSet(ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(
                name__icontains=name
            )
        return queryset


class AirplaneViewSet(ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(
                name__icontains=name
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "upload_image":
            return AirplaneImageSerializer
        elif self.action == "retrieve":
            return AirplaneRetrieveSerializer
        elif self.action == "list":
            return AirplaneListSerializer
        return AirplaneSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminAllORIsAuthenticatedOrReadOnly]
    )
    def upload_image(self, request: Request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class FlightViewSet(ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        flight_id = self.request.query_params.get("id")
        source = self.request.query_params.get("from")
        destination = self.request.query_params.get("to")
        airplane = self.request.query_params.get("plane_name")
        if flight_id:
            queryset = self.queryset.filter(
                id__in=flight_id
            )
        if source:
            queryset = self.queryset.filter(
                route__source__name__icontains=source
            )
        if destination:
            queryset = self.queryset.filter(
                route__destination__name__icontains=destination
            )
        if airplane:
            queryset = self.queryset.filter(
                airplane__name__icontains=airplane
            )
        if self.action in ("list", "retrieve"):
            return queryset.select_related(
            ).prefetch_related("crews").annotate(
                tickets_available=F(
                    "airplane__rows"
                ) * F(
                    "airplane__seats_in_row"
                ) - Count(
                    "flight_tickets"
                )
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        instance.update_flying_hours()

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.update_flying_hours()


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @staticmethod
    def params_to_ints(query_str):
        return [int(str_id) for str_id in query_str.split(",")]

    def get_queryset(self):
        queryset = self.queryset
        ticket_ids = self.request.query_params.get("ticket_id")
        if ticket_ids:
            ticket_ids = self.params_to_ints(ticket_ids)
            queryset = queryset.filter(tickets__id__in=ticket_ids)
        if self.action in ("list", "retrieve"):
            return queryset.select_related()
        return queryset.filter(user=self.request.user).distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        elif self.action == "retrieve":
            return OrderRetrieveSerializer
        return OrderSerializer


class TicketViewSet(ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_queryset(self):
        queryset = self.queryset
        ticket_id = self.request.query_params.get("id")
        flight_info = self.request.query_params.get("route")
        if ticket_id:
            queryset = self.queryset.filter(
                id__in=ticket_id
            )
        if flight_info:
            queryset = self.queryset.filter(
                Q(flight__route__source__name__icontains=flight_info) |
                Q(flight__route__destination__name__icontains=flight_info)
            )
        if self.action in ("list", "retrieve"):
            return queryset.select_related()
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        elif self.action == "retrieve":
            return TicketRetrieveSerializer
        return TicketSerializer
