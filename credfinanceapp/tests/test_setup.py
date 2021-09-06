from rest_framework.test import APITestCase
#from django.test import TestCase
from django.urls import reverse

class TestSetUp(APITestCase):

    def setUp(self):
        self.registration_url = reverse('sign_up_api_view')
        self.sign_in_url = reverse('sign_in_api_view')

        self.registration_data = {
            'email': 'tester@test.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'bvn': 12345678901,
            'password': 'passwordfortesting'
        }

        self.sign_in_data = {
            'email':'tester@test.com',
            'password':'passwordfortesting'
        }
        return super().setUp()

    def tearDown(self):
        return super().tearDown()