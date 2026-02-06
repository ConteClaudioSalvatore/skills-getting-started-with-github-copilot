"""Tests for the Mergington High School Activities API."""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that the endpoint returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data

    def test_activities_have_required_fields(self, client):
        """Test that activities have all required fields."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Tests for the POST /activities/{activity}/signup endpoint."""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds participant to the activity."""
        test_email = "newstudent@mergington.edu"
        
        # Get initial participants
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        
        # Sign up
        client.post(
            "/activities/Chess Club/signup",
            params={"email": test_email}
        )
        
        # Check participant was added
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count + 1
        assert test_email in response.json()["Chess Club"]["participants"]

    def test_signup_duplicate_email(self, client, reset_activities):
        """Test that duplicate signup fails."""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signup for non-existent activity."""
        response = client.post(
            "/activities/Nonexistent Activity/signup",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestUnregister:
    """Tests for the POST /activities/{activity}/unregister endpoint."""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister from an activity."""
        email = "michael@mergington.edu"  # Already signed up for Chess Club
        
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes participant from the activity."""
        email = "michael@mergington.edu"
        
        # Get initial participants
        response = client.get("/activities")
        initial_count = len(response.json()["Chess Club"]["participants"])
        assert email in response.json()["Chess Club"]["participants"]
        
        # Unregister
        client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        
        # Check participant was removed
        response = client.get("/activities")
        new_count = len(response.json()["Chess Club"]["participants"])
        assert new_count == initial_count - 1
        assert email not in response.json()["Chess Club"]["participants"]

    def test_unregister_not_signed_up(self, client, reset_activities):
        """Test unregister for someone not signed up."""
        email = "notsignup@mergington.edu"
        
        response = client.post(
            "/activities/Chess Club/unregister",
            params={"email": email}
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregister from non-existent activity."""
        response = client.post(
            "/activities/Nonexistent Activity/unregister",
            params={"email": "test@mergington.edu"}
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestRoot:
    """Tests for the root endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "static/index.html" in response.headers["location"]
