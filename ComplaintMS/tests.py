from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile, Complaint, Grievance

class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.profile = Profile.objects.create(user=self.user, collegename='College1', contactnumber='1234567890')

    def test_profile_creation(self):
        # Check if the profile is correctly associated with the user
        self.assertEqual(self.profile.user.username, 'testuser')
        self.assertEqual(self.profile.collegename, 'College1')
        self.assertEqual(self.profile.contactnumber, '1234567890')

    def test_profile_str_method(self):
        # Check the __str__ method of Profile
        self.assertEqual(str(self.profile), "testuser's Profile")

class ComplaintModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.complaint = Complaint.objects.create(
            Subject='Complaint about teacher',
            user=self.user,
            Type_of_complaint='Teacher',
            Description='Description of the complaint',
            status=3
        )

    def test_complaint_creation(self):
        # Test that the complaint is correctly saved
        self.assertEqual(self.complaint.Subject, 'Complaint about teacher')
        self.assertEqual(self.complaint.status, 3)
        self.assertEqual(self.complaint.user.username, 'testuser')

    def test_complaint_str_method(self):
        # Test the __str__ method of Complaint
        self.assertEqual(str(self.complaint), 'Teacher - Complaint about teacher')

    def test_complaint_status_change(self):
        # Test if changing the complaint's status works correctly
        self.complaint.status = 1
        self.complaint.save()
        self.assertEqual(self.complaint.status, 1)

class GrievanceModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.grievance = Grievance.objects.create(guser=self.user)

    def test_grievance_creation(self):
        # Test that the grievance is correctly created
        self.assertEqual(self.grievance.guser.username, 'testuser')

    def test_grievance_str_method(self):
        # Test the __str__ method of Grievance
        self.assertEqual(str(self.grievance), 'testuser')

class ViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_complaint_view(self):
        # Log in the user
        self.client.login(username='testuser', password='password')

        # Test if the complaint view is accessible
        response = self.client.get('/complaints/')  # Change URL to your complaint list view
        self.assertEqual(response.status_code, 200)

    def test_create_complaint_view(self):
        # Log in the user
        self.client.login(username='testuser', password='password')

        # Test the form submission for creating a complaint
        response = self.client.post('/complaints/create/', {
            'Subject': 'New complaint',
            'Type_of_complaint': 'Teacher',
            'Description': 'Details of the complaint'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful form submission

