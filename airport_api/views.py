from datetime import datetime

from django.db.models import Count, F, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiExample,
    extend_schema_view,
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
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
    CrewListSerializer,
    CrewRetrieveSerializer,
    AirportSerializer,
    AirportListSerializer,
    AirportRetrieveSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteRetrieveSerializer,
    AirplaneTypeSerializer,
    AirplaneTypeListSerializer,
    AirplaneTypeRetrieveSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneImageSerializer,
    AirplaneRetrieveSerializer,
    FlightSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
    TicketSerializer,
    TicketListSerializer,
    TicketRetrieveSerializer,
    OrderSerializer,
    OrderListSerializer,
    OrderRetrieveSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Get list of all crew members",
        description="User can get a list of all crew members",
    ),
    create=extend_schema(
        summary="Create a crew member", description="Admin can create a new crew member"
    ),
    retrieve=extend_schema(
        summary="Get a detailed info about specific crew member",
        description="User can get specific info about crew member",
    ),
    update=extend_schema(
        summary="Update specific info about crew member",
        description="Admin can update information about specific crew member",
    ),
    partial_update=extend_schema(
        summary="Partial update of specific crew member",
        description="Admin can make a partial update of specific crew member",
    ),
    destroy=extend_schema(
        summary="Delete a specific crew member",
        description="Admin can delete specific crew member",
    ),
)
class CrewViewSet(ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_queryset(self):
        queryset = self.queryset
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")
        if first_name:
            queryset = queryset.filter(
                first_name__icontains=first_name
            )
        if last_name:
            queryset = queryset.filter(
                last_name__icontains=last_name
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return CrewListSerializer
        elif self.action == "retrieve":
            return CrewRetrieveSerializer
        return CrewSerializer

    @extend_schema(
        methods=["GET"],
        summary="Get list of all crew members",
        description="User can get a list of all crew members",
        parameters=[
            OpenApiParameter(
                name="first_name",
                description="Filter crew members by their first name",
                type=str,
                examples=[OpenApiExample("Example", value="Michael")],
            ),
            OpenApiParameter(
                name="last_name",
                description="Filter crew members by their last name",
                type=str,
                examples=[OpenApiExample("Example", value="Ellipsis")],
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema_view(
    create=extend_schema(
        summary="Create an airport", description="Admin can create an airport"
    ),
    retrieve=extend_schema(
        summary="Get a detailed info about specific airport",
        description="User can get a detailed info about specific airport",
    ),
    update=extend_schema(
        summary="Update info about specific airport",
        description="Admin can update information about specific airport",
    ),
    partial_update=extend_schema(
        summary="Partial update of specific airport",
        description="Admin can make a partial update of specific airport",
    ),
    destroy=extend_schema(
        summary="Delete a specific airport",
        description="Admin can delete specific airport",
    ),
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
                examples=[OpenApiExample("Example", value="Paris")],
            )
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "list":
            return AirportListSerializer
        elif self.action == "retrieve":
            return AirportRetrieveSerializer
        return AirportSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(
                name__icontains=name
            )
        return queryset


@extend_schema_view(
    create=extend_schema(
        summary="Create a flight route", description="Admin can create a flight route"
    ),
    retrieve=extend_schema(
        summary="Get a detailed info about specific route",
        description="User can get a detailed info about specific route",
    ),
    update=extend_schema(
        summary="Update info about specific route",
        description="Admin can update information about specific route",
    ),
    partial_update=extend_schema(
        summary="Partial update of specific route",
        description="Admin can make a partial update of specific route",
    ),
    destroy=extend_schema(
        summary="Delete a specific route", description="Admin can delete specific route"
    ),
)
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
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteRetrieveSerializer
        return RouteSerializer

    @extend_schema(
        methods=["GET"],
        summary="Get list of routes",
        description="User can get a list of all routes",
        parameters=[
            OpenApiParameter(
                name="source",
                description="Filter by departure airport",
                type=str,
                examples=[OpenApiExample("Example", value="Paris")],
            ),
            OpenApiParameter(
                name="destination",
                description="Filter by arrival airport",
                type=str,
                examples=[OpenApiExample("Example", value="London")],
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema_view(
    create=extend_schema(
        summary="Create an airplane type",
        description="Admin can create an airplane type",
    ),
    retrieve=extend_schema(
        summary="Get a detailed info about specific type of airplane",
        description="User can get a detailed info about specific type of airplane",
    ),
    update=extend_schema(
        summary="Update info about specific airplane type",
        description="Admin can update information about specific airplane type",
    ),
    partial_update=extend_schema(
        summary="Partial update of specific airplane type",
        description="Admin can make a partial update of specific airplane type",
    ),
    destroy=extend_schema(
        summary="Delete a specific airplane type",
        description="Admin can delete specific airplane type",
    ),
)
class AirplaneTypeViewSet(ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "create"):
            return AirplaneTypeListSerializer
        return AirplaneTypeRetrieveSerializer

    @extend_schema(
        methods=["GET"],
        summary="Get list of all airplane types",
        description="User can get a list of all airplane types",
        parameters=[
            OpenApiParameter(
                name="name",
                description="Filter by airplane type name",
                type=str,
                examples=[OpenApiExample("Example", value="Commercial")],
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema_view(
    create=extend_schema(
        summary="Create an airplane model",
        description="Admin can create an airplane model",
    ),
    retrieve=extend_schema(
        summary="Get a detailed info about specific airplane",
        description="User can get a detailed info about specific airplane",
    ),
    update=extend_schema(
        summary="Update info about specific airplane",
        description="Admin can update information about specific airplane",
    ),
    partial_update=extend_schema(
        summary="Partial update of specific airplane",
        description="Admin can make a partial update of specific airplane",
    ),
    destroy=extend_schema(
        summary="Delete a specific airplane",
        description="Admin can delete specific airplane",
    ),
)
class AirplaneViewSet(ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

    def get_serializer_class(self):
        if self.action == "upload_image":
            return AirplaneImageSerializer
        elif self.action == "retrieve":
            return AirplaneRetrieveSerializer
        elif self.action == "list":
            return AirplaneListSerializer
        return AirplaneSerializer

    @extend_schema(
        methods=["GET"],
        summary="Get list of all airplanes ",
        description="User can get a list of all airplanes",
        parameters=[
            OpenApiParameter(
                name="name",
                description="Filter by airplane name",
                type=str,
                examples=[OpenApiExample("Example", value="Airbus")],
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminAllORIsAuthenticatedOrReadOnly],
    )
    def upload_image(self, request: Request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    create=extend_schema(
        summary="Create a flight", description="Admin can create a flight"
    ),
    retrieve=extend_schema(
        summary="Get a detailed info about specific flight",
        description="User can get a detailed info about specific flight",
    ),
    update=extend_schema(
        summary="Update info about specific flight",
        description="Admin can update information about specific flight",
    ),
    partial_update=extend_schema(
        summary="Partial update of specific flight",
        description="Admin can make a partial update of specific flight",
    ),
    destroy=extend_schema(
        summary="Delete a specific flight",
        description="Admin can delete specific flight",
    ),
)
class FlightViewSet(ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_queryset(self):
        queryset = self.queryset
        flight_id = self.request.query_params.get(
            "id"
        )
        source = self.request.query_params.get(
            "from"
        )
        destination = self.request.query_params.get(
            "to"
        )
        airplane = self.request.query_params.get(
            "plane_name"
        )
        departure_date = self.request.query_params.get(
            "departure_date"
        )
        arrival_date = self.request.query_params.get(
            "arrival_date"
        )
        departure_hour = self.request.query_params.get(
            "departure_hour"
        )
        departure_minute = self.request.query_params.get(
            "departure_minute"
        )
        arrival_hour = self.request.query_params.get(
            "arrival_hour"
        )
        arrival_minute = self.request.query_params.get(
            "arrival_minute"
        )
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
        if departure_date:
            date = datetime.strptime(
                departure_date, "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(
                departure_time__date=date
            )
        if departure_hour:
            queryset = queryset.filter(
                departure_time__hour=departure_hour
            )
        if departure_minute:
            queryset = queryset.filter(
                departure_time__minute=departure_minute
            )
        if arrival_date:
            date = datetime.strptime(
                arrival_date,
                "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(
                arrival_time__date=date
            )
        if arrival_hour:
            queryset = queryset.filter(
                arrival_time__hour=arrival_hour
            )
        if arrival_minute:
            queryset = queryset.filter(
                arrival_time__minute=arrival_minute
            )
        if self.action in ("list", "retrieve"):
            return (
                queryset.select_related()
                .prefetch_related("crews")
                .annotate(
                    tickets_available=F("airplane__rows") * F("airplane__seats_in_row")
                    - Count("flight_tickets")
                )
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer

    @extend_schema(
        methods=["GET"],
        summary="Get list of all flights",
        description="User can get a list of all flights",
        parameters=[
            OpenApiParameter(
                name="id",
                description="Filter by flight id",
                type=int,
                examples=[OpenApiExample("Example", value=1)],
            ),
            OpenApiParameter(
                name="airplane",
                description="Filter by airplane name",
                type=str,
                examples=[OpenApiExample("Example", value="Airbus")],
            ),
            OpenApiParameter(
                name="source",
                description="Filter by departure airport",
                type=str,
                examples=[OpenApiExample("Example", value="London")],
            ),
            OpenApiParameter(
                name="destination",
                description="Filter by arrival airport",
                type=str,
                examples=[OpenApiExample("Example", value="Paris")],
            ),
            OpenApiParameter(
                name="departure_time",
                description="Filter by airplane departure time",
                type=OpenApiTypes.DATETIME,
                examples=[OpenApiExample("Example", value="2024-05-21")],
            ),
            OpenApiParameter(
                name="departure_hour",
                description="Filter by airplane departure hour",
                type=OpenApiTypes.TIME,
                examples=[OpenApiExample("Example", value="08")],
            ),
            OpenApiParameter(
                name="departure_minute",
                description="Filter by airplane departure minute",
                type=OpenApiTypes.TIME,
                examples=[OpenApiExample("Example", value="30")],
            ),
            OpenApiParameter(
                name="arrival_time",
                description="Filter by airplane arrival time",
                type=OpenApiTypes.DATETIME,
                examples=[OpenApiExample("Example", value="2024-05-21")],
            ),
            OpenApiParameter(
                name="arrival_hour",
                description="Filter by airplane arrival hour",
                type=OpenApiTypes.DATETIME,
                examples=[OpenApiExample("Example", value="10")],
            ),
            OpenApiParameter(
                name="arrival_minute",
                description="Filter by airplane arrival minute",
                type=OpenApiTypes.DATETIME,
                examples=[OpenApiExample("Example", value="00")],
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema_view(
    create=extend_schema(
        summary="Create an order", description="Authorized user can create an order"
    ),
    retrieve=extend_schema(
        summary="Get a detailed info about specific order",
        description="User can get a detailed info about his order",
    ),
    update=extend_schema(
        summary="Update info about specific order",
        description="Admin can update information about specific order or user can if it's user's own order",
    ),
    partial_update=extend_schema(
        summary="Partial update of specific order",
        description="Admin can make a partial update of specific order or user can if it's user's own order",
    ),
    destroy=extend_schema(
        summary="Delete a specific order",
        description="Admin can delete specific order or user can if it's user's own order",
    ),
)
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @staticmethod
    def params_to_ints(query_str):
        return [int(str_id) for str_id in query_str.split(",")]

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        if not user.is_staff:
            queryset = self.queryset.filter(user=user)

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

    @extend_schema(
        methods=["GET"],
        summary="Get list of all orders ",
        description="User can get a list of orders or admin can get access to all users orders.",
        parameters=[
            OpenApiParameter(
                name="ticket_id",
                description="Filter by ticket ids",
                type=int,
                examples=[OpenApiExample("Example", value=1)],
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema_view(
    retrieve=extend_schema(
        summary="Get a detailed info about specific ticket",
        description="Admin can get a detailed info about specific ticket or user can if it's user's ticket",
    ),
    update=extend_schema(
        summary="Update info about specific ticket",
        description="Admin can update information about specific ticket or user can if it's user's ticket",
    ),
    partial_update=extend_schema(
        summary="Partial update of specific ticket",
        description="Admin can make a partial update of specific ticket or user can if it's user's ticket",
    ),
    destroy=extend_schema(
        summary="Delete a specific flight",
        description="Admin can delete specific ticket or user can if it's user's own ticket",
    ),
)
class TicketViewSet(ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        if not user.is_staff:
            queryset = self.queryset.filter(order__user=user)
        ticket_id = self.request.query_params.get("id")
        flight_info = self.request.query_params.get("route")
        if ticket_id:
            if "-" in ticket_id:
                start_id, end_id = map(int, ticket_id.split("-"))
                queryset = queryset.filter(id__range=(start_id, end_id))
            else:
                queryset = self.queryset.filter(id__in=ticket_id)

        if flight_info:
            queryset = self.queryset.filter(
                Q(flight__route__source__name__icontains=flight_info)
                | Q(flight__route__destination__name__icontains=flight_info)
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

    @extend_schema(
        methods=["GET"],
        summary="Get list of all tickets",
        description="Admin can get a list of all tickets",
        parameters=[
            OpenApiParameter(
                name="id",
                description="Filter ticket by id or range of ids",
                type=int,
                examples=[
                    OpenApiExample("Example 1", value=1),
                    OpenApiExample("Example 2", value=1 - 15),
                ],
            ),
            OpenApiParameter(
                name="route",
                description="Filter tickets by flight info",
                type=str,
                examples=[OpenApiExample("Example", value="Paris")],
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
