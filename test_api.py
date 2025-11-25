"""
Test script for the Task Management Microservice.

This script demonstrates how to use the API endpoints:
- POST /tasks - Create a new task
- GET /tasks - Get all tasks
- GET /tasks/{task_id} - Get a specific task
- PUT /tasks/{task_id} - Update task status
- DELETE /tasks/{task_id} - Delete a task
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_response(title: str, response: requests.Response, show_json: bool = True):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    if show_json and response.text:
        try:
            print(json.dumps(response.json(), indent=2, default=str))
        except:
            print(response.text)
    else:
        print(response.text or "No content")

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print_response("Health Check", response)
    return response.status_code == 200

def test_create_task(description: str, status: str = "pending") -> int:
    """Create a task and return its ID"""
    payload = {
        "description": description,
        "status": status
    }
    response = requests.post(
        f"{BASE_URL}/tasks",
        json=payload
    )
    print_response(f"Create Task - {description}", response)
    if response.status_code == 201:
        return response.json()["id"]
    return None

def test_get_all_tasks():
    """Get all tasks"""
    response = requests.get(f"{BASE_URL}/tasks")
    print_response("Get All Tasks", response)
    return response.status_code == 200

def test_get_task(task_id: int):
    """Get a specific task"""
    response = requests.get(f"{BASE_URL}/tasks/{task_id}")
    print_response(f"Get Task by ID (ID: {task_id})", response)
    return response.status_code == 200

def test_update_task(task_id: int, new_status: str):
    """Update task status"""
    payload = {"status": new_status}
    response = requests.put(
        f"{BASE_URL}/tasks/{task_id}",
        json=payload
    )
    print_response(f"Update Task Status - ID: {task_id}, New Status: {new_status}", response)
    return response.status_code == 200

def test_delete_task(task_id: int):
    """Delete a task"""
    response = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    print_response(f"Delete Task (ID: {task_id})", response, show_json=False)
    return response.status_code == 204

def test_error_cases():
    """Test error cases"""
    # Try to get non-existent task
    response = requests.get(f"{BASE_URL}/tasks/9999")
    print_response("Error Case - Get Non-existent Task", response)
    
    # Try to delete non-existent task
    response = requests.delete(f"{BASE_URL}/tasks/9999")
    print_response("Error Case - Delete Non-existent Task", response)

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Task Management Microservice - API Tests")
    print("="*60)
    
    try:
        # Health check
        if not test_health_check():
            print("ERROR: Health check failed!")
            return
        
        # Create tasks
        task_id_1 = test_create_task("Complete project documentation")
        task_id_2 = test_create_task("Review code changes", "in_progress")
        task_id_3 = test_create_task("Deploy to production", "pending")
        
        # Get all tasks
        test_get_all_tasks()
        
        # Get specific task
        if task_id_1:
            test_get_task(task_id_1)
        
        # Update task status
        if task_id_1:
            test_update_task(task_id_1, "completed")
        
        if task_id_2:
            test_update_task(task_id_2, "completed")
        
        # Get all tasks after updates
        test_get_all_tasks()
        
        # Delete a task
        if task_id_3:
            test_delete_task(task_id_3)
        
        # Get all tasks after deletion
        test_get_all_tasks()
        
        # Test error cases
        test_error_cases()
        
        print("\n" + "="*60)
        print("Test Suite Completed")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Could not connect to the server!")
        print("Make sure the microservice is running with: python myapp.py")
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")

if __name__ == "__main__":
    main()
