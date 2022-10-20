"""
Test module for Tasks
"""
import datetime
import time
import unittest
from django.test import TestCase
from .models import Availability, Category, Task

class TestAvailability(TestCase):
    """
    Tests for availability model
    """

    def test_route_is_ok_show(self):

        response = self.client.get('/profile/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
    
    def test_route_is_ok_add(self):

        availability = {
            'monday': 8,
            'tuesday': 8,
            'wednesday': 8,
            'thursday': 8,
            'friday': 8,
            'saturday': 0,
            'sunday': 0
        }
        t_before = time.time()
        response = self.client.post('/profile/', availability)
        t_after = time.time()

        total = t_before - t_after

        # Check request process < 2 seconds
        self.assertLess(total, 2)

        # Check route is ok
        self.assertEqual(response.status_code, 200)

class TestTask(TestCase):
    """
    Tests for Task model
    """
    
    def add_availability(self):
        """
        Adds availability
        """
        Availability.objects.create(monday=8, 
            tuesday=8,
            wednesday=8,
            thursday=8,
            friday=8,
            saturday=0,
            sunday=0
        )

    def add_task(self):
        """
        Add task to db
        """
        task = {
            'description': 'Test',
            'category': 'Test',
            'start': '2022-10-18',
            'deadline': '2022-10-18',
            'status': 'NS',
            'estimated_duration': 8,
            'actual_duration': 0
        }
        category = Category.objects.create(name="Test")
        task = Task.objects.create(
            description='Test',
            category=category,
            start=(datetime.datetime(2022, 10, 18)),
            deadline=(datetime.datetime(2022, 10, 18)),
            estimated_duration=0,
            actual_duration=0,
            status='NS'
        )
        return task.id

    def test_route_is_ok_all(self):

        response = self.client.get('/task/all')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_redirect_no_availability(self):

        response = self.client.get('/task/add')

        # Check that the response is 200 OK.
        self.assertRedirects(response, '/profile/')
    
    def test_route_add(self):

        self.add_availability()

        t_before = time.time()
        response = self.client.get('/task/add')
        t_after = time.time()

        total = t_before - t_after

        self.assertLess(total, 2)
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

    def test_route_is_ok_add_post(self):
        """
        Asserts that task is created successfully
        and redirects to all tasks and request
        process time is less than 2 seconds
        """

        self.add_availability()

        task = {
            'description': 'Test',
            'category': 'Test',
            'start': '2022-10-18',
            'deadline': '2022-10-18',
            'status': 'NS',
            'estimated_duration': 8,
            'actual_duration': 0
        }
        t_before = time.time()
        response = self.client.post('/task/add', task, follow=True)
        t_after = time.time()

        total = t_before - t_after

        self.assertLess(total, 2)
        self.assertRedirects(response, '/task/all')
    
    def test_show_task_route_ok(self):
        """
        Asserts that show task
        route is ok
        """
        self.add_availability()
        task_id = self.add_task()

        t_before = time.time()
        response = self.client.get(f'/task/{task_id}')
        t_after = time.time()

        total = t_before - t_after
        # Check request process < 2 seconds
        self.assertLess(total, 2)

        # Check route is ok
        self.assertEqual(response.status_code, 200)


class TestCategory(TestCase):
    """
    Tests for Category model
    """

    def test_route_is_ok_all(self):
        """
        Asserts route all categories is ok
        and request processes less that 2 seconds
        """

        t_before = time.time()
        response = self.client.get('/category/all')
        t_after = time.time()

        total = t_before - t_after
        # Check request process < 2 seconds
        self.assertLess(total, 2)

        # Check route is ok
        self.assertEqual(response.status_code, 200)

