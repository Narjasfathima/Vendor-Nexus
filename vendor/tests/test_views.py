from django.test import TestCase,TransactionTestCase
from django.db import transaction

from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from ..models import Vendor, PurchaseOrder, HistoricalPerformance
from ..serializers import VendorModelSer, PurchaseOrderModelSer, PerformanceModelSer


class ViewsTestCase(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username='testuser', password='testpassword')

        # Generate a token for the test user
        self.token = Token.objects.create(user=self.test_user)

        # Create an API client
        self.client = APIClient()

        # Include the token in the client's credentials
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        # Create some test data
        self.vendor_data = {"name": "Test Vendor", "contact_details": "Test Contact", "address": "Test Address"}
        self.vendor = Vendor.objects.create(**self.vendor_data)
        v_ob=Vendor.objects.get(id=self.vendor.id)

        self.purchase_order_dataa = {
            "vendor": self.vendor,
            "order_date": "2023-01-01T01:00:00.00Z",
            "delivery_date": "2023-01-10T01:00:00.00Z",
            "items": {"item1": 10, "item2": 20},
            "quantity": 30,
            "status": "pending",
            "issue_date": "2023-01-20T01:00:00.00Z",
        }
        self.purchase_order_data = {
            "vendor":self.vendor.id,
            "order_date": "2023-01-01T01:00:00.00Z",
            "delivery_date": "2023-01-10T01:00:00.00Z",
            "items": {"item1": 10, "item2": 20},
            "quantity": 30,
            "status": "pending",
            "issue_date": "2023-01-20T01:00:00.00Z",
        }
        self.purchase_order = PurchaseOrder.objects.create(**self.purchase_order_dataa)


    def test_vendor_create(self):
        client = APIClient()
        response = self.client.post("/api/vendors/", self.vendor_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_vendor_list(self):
        client = APIClient()
        response = self.client.get("/api/vendors/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Assuming only one vendor is created in the setup

    def test_vendor_retrieve(self):
        client = APIClient()
        response = self.client.get(f"/api/vendors/{self.vendor.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.vendor_data["name"])

    def test_vendor_update(self):
        client = APIClient()
        updated_data = {"name": "Updated Vendor", "contact_details": "Updated Contact", "address": "Updated Address"}
        response = self.client.put(f"/api/vendors/{self.vendor.id}/", updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.name, updated_data["name"])
        
    
    def test_vendor_delete(self):
        client = APIClient()
        response = self.client.delete(f"/api/vendors/{self.vendor.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Vendor.objects.filter(id=self.vendor.id).exists())

    def test_vendor_performance_retrieval(self):
        client = APIClient()
        response = self.client.get(f"/api/vendors/{self.vendor.id}/performance/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["vendor"]['id'], str(self.vendor.id))
        self.assertIn("on_time_delivery_rate", response.data)  # Assuming this field is present in the response



    def test_purchase_order_create(self):
        client = APIClient()
        response = self.client.post("/api/purchase_orders/", self.purchase_order_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_purchase_order_list(self):
        client = APIClient()
        response = self.client.get("/api/purchase_orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Assuming only one purchase order is created in the setup

    def test_purchase_order_retrieve(self):
        client = APIClient()
        response = self.client.get(f"/api/purchase_orders/{self.purchase_order.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data["po_number"])
        print(self.purchase_order.po_number)
        self.assertEqual(response.data["po_number"], self.purchase_order.po_number)

    def test_purchase_order_update(self):
    # Test updating a purchase order
        data = {
            "acknowledgment_date":"2023-02-20T01:00:00.00Z" ,
            "vendor": self.vendor.id,
            "order_date": "2023-01-01T01:00:00.00Z",
            "delivery_date":"2023-01-25T12:00:00.00Z",
            "items": {"item1": 10, "item2": 20},
            "quantity": 30,
            "status": "completed",
            "issue_date": "2023-01-20T01:00:00.00Z",
        }

        response = self.client.put(f'/api/purchase_orders/{self.purchase_order.id}/', data, format='json')

        print(response.status_code)
        print(response.content.decode('utf-8'))

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.purchase_order.refresh_from_db()
        self.assertEqual(self.purchase_order.status, "completed")


    def test_purchase_order_delete(self):
        # Test deleting a purchase order
        response = self.client.delete(f'/api/purchase_orders/{self.purchase_order.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PurchaseOrder.objects.filter(id=self.purchase_order.id).exists())

    def test_purchase_order_acknowledge(self):
        # Test acknowledging a purchase order
        acknowledgment_date = "2023-12-02 13:28:51.402000+00:00"
        data = {
            "acknowledgment_date": acknowledgment_date
        }
        response = self.client.post(f'/api/purchase_orders/{self.purchase_order.id}/acknowledge/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.purchase_order.refresh_from_db()
        self.assertEqual(str(self.purchase_order.acknowledgment_date), acknowledgment_date)

    def tearDown(self):
        # Clean up any resources created during the tests
        pass
