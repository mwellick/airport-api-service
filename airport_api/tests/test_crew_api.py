from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport_api.models import Airplane, Crew
from airport_api.serializers import CrewListSerializer, CrewRetrieveSerializer

CREW_URL = reverse("api_airport:crew-list")


def detail_url(crew_id):
    return reverse("api_airport:crew-detail", args=[crew_id])


class UnauthenticatedCrewApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="Test@test.test", password="Testpsw1"
        )
        self.client.force_authenticate(self.user)

        self.crew_member1 = Crew.objects.create(
            first_name="Qwerty", last_name="Johnson", flying_hours=0.0
        )
        self.crew_member2 = Crew.objects.create(
            first_name="John", last_name="Qwerty", flying_hours=0.0
        )

    def test_airport_list(self):
        res = self.client.get(CREW_URL)
        airports = Crew.objects.all()
        serializer = CrewListSerializer(airports, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_crew_member_by_first_name(self):
        res = self.client.get(CREW_URL, data={"first_name": "Qwer"})
        serializer1 = CrewListSerializer(self.crew_member1)
        serializer2 = CrewListSerializer(self.crew_member2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_filter_crew_member_by_last_name(self):
        res = self.client.get(CREW_URL, data={"last_name": "Johns"})
        serializer1 = CrewListSerializer(self.crew_member1)
        serializer2 = CrewListSerializer(self.crew_member2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_retrieve_crew_detail(self):
        res = self.client.get(detail_url(self.crew_member1.id))
        serializer = CrewRetrieveSerializer(self.crew_member1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_crew_member_forbidden(self):
        payload = {
            "first_name": "Michael",
            "last_name": "Ellipsis",
            "flying_hours": 0.0,
        }
        res = self.client.post(CREW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_crew_member_forbidden(self):
        res = self.client.put(detail_url(self.crew_member1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_crew_member_forbidden(self):
        res = self.client.delete(detail_url(self.crew_member1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="Test@test.test", password="Testpsw1", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.crew_member1 = Crew.objects.create(
            first_name="Qwerty", last_name="Johnson", flying_hours=0.0
        )
        self.crew_member2 = Crew.objects.create(
            first_name="John", last_name="Qwerty", flying_hours=0.0
        )

    def test_add_crew_member(self):
        payload = {
            "first_name": "Michael",
            "last_name": "Ellipsis",
            "flying_hours": 0.0,
        }
        res = self.client.post(CREW_URL, payload)

        crew_member = Crew.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Crew.objects.count(), 3)

        for key in payload:
            self.assertEqual(payload[key], getattr(crew_member, key))

    def test_update_crew_member(self):
        payload = {
            "first_name": "Michael",
            "last_name": "Ellipsis",
            "flying_hours": 0.0,
        }

        res = self.client.put(detail_url(self.crew_member2.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        crew_member = Crew.objects.get(id=self.crew_member2.id)
        for key in payload:
            self.assertEqual(payload[key], getattr(crew_member, key))

    def test_delete_crew_member(self):
        res = self.client.delete(detail_url(self.crew_member2.id))
        self.assertEqual(Crew.objects.count(), 1)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_invalid_crew_member(self):
        invalid_id = self.crew_member2.id + 1
        res = self.client.get(detail_url(invalid_id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
