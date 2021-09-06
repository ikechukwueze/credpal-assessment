from .test_setup import TestSetUp


class TestViews(TestSetUp):
    def test_user_registration_fail(self):
        res = self.client.post(self.registration_url)
        self.assertEqual(res.status_code, 400)

    def test_user_registration_success(self):
        res = self.client.post(self.registration_url,
                               self.registration_data,
                               format='json')
        self.assertEqual(res.status_code, 201)
    
    def test_user_sign_in(self):
        self.client.post(self.registration_url,
                               self.registration_data,
                               format='json')
        res = self.client.post(self.sign_in_url, self.sign_in_data, format='json')
        self.assertEqual(res.status_code, 200)

        
    

    

    #def test_user_registration(self):
    #    self.client.post(self.registration_url)