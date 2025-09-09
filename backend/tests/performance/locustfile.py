from locust import HttpUser, task, between
import random
import json


class CRMERPUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get authentication token"""
        response = self.client.post("/api/v1/auth/login/", json={
            "username": "admin",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access"]
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
        else:
            self.token = None
    
    @task(3)
    def view_dashboard(self):
        """View dashboard - most common task"""
        self.client.get("/api/v1/dashboard/")
    
    @task(2)
    def list_customers(self):
        """List customers"""
        self.client.get("/api/v1/customers/")
    
    @task(2)
    def list_products(self):
        """List products"""
        self.client.get("/api/v1/products/")
    
    @task(1)
    def create_customer(self):
        """Create a new customer"""
        customer_data = {
            "first_name": f"Test Customer {random.randint(1, 1000)}",
            "last_name": "Performance Test",
            "email": f"test{random.randint(1, 1000)}@example.com",
            "phone_number": f"0912{random.randint(1000000, 9999999)}",
            "customer_type": random.choice(["individual", "legal"]),
            "status": "active"
        }
        
        self.client.post("/api/v1/customers/", json=customer_data)
    
    @task(1)
    def create_product(self):
        """Create a new product"""
        product_data = {
            "name": f"Test Product {random.randint(1, 1000)}",
            "description": "Performance test product",
            "price": random.uniform(1000, 100000),
            "status": "active"
        }
        
        self.client.post("/api/v1/products/", json=product_data)
    
    @task(1)
    def search_customers(self):
        """Search customers"""
        search_terms = ["test", "customer", "performance", "demo"]
        search_term = random.choice(search_terms)
        
        self.client.get(f"/api/v1/customers/?search={search_term}")
    
    @task(1)
    def get_customer_stats(self):
        """Get customer statistics"""
        self.client.get("/api/v1/customers/stats/")
    
    @task(1)
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        self.client.get("/api/v1/dashboard/stats/")


class HighLoadUser(HttpUser):
    wait_time = between(0.1, 0.5)
    weight = 1  # Lower weight for high load users
    
    def on_start(self):
        """Login and get authentication token"""
        response = self.client.post("/api/v1/auth/login/", json={
            "username": "admin",
            "password": "admin123"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access"]
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
        else:
            self.token = None
    
    @task(10)
    def rapid_api_calls(self):
        """Make rapid API calls to test rate limiting"""
        endpoints = [
            "/api/v1/customers/",
            "/api/v1/products/",
            "/api/v1/dashboard/",
            "/api/v1/customers/stats/"
        ]
        
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)
    
    @task(5)
    def concurrent_creates(self):
        """Test concurrent creation of resources"""
        if random.choice([True, False]):
            # Create customer
            customer_data = {
                "first_name": f"Load Test {random.randint(1, 10000)}",
                "last_name": "Concurrent",
                "email": f"load{random.randint(1, 10000)}@test.com",
                "phone_number": f"0912{random.randint(1000000, 9999999)}",
                "customer_type": "individual",
                "status": "active"
            }
            self.client.post("/api/v1/customers/", json=customer_data)
        else:
            # Create product
            product_data = {
                "name": f"Load Product {random.randint(1, 10000)}",
                "description": "Concurrent test product",
                "price": random.uniform(1000, 100000),
                "status": "active"
            }
            self.client.post("/api/v1/products/", json=product_data)