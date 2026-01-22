from locust import HttpUser, User, task, between, LoadTestShape
import grpc
import glossary_pb2
import glossary_pb2_grpc
import random
import time
import os


class GlossaryRESTUser(HttpUser):
    """Load test for REST API endpoints"""
    host = "http://localhost:8003"
    wait_time = between(1, 3)

    def on_start(self):
        """Setup: Get initial data to use in update tests"""
        response = self.client.get("/glossary/getAll/")
        if response.status_code == 200:
            items = response.json()
            if items:
                self.existing_item_id = items[0].get('id', 1)
            else:
                self.existing_item_id = 1
        else:
            self.existing_item_id = 1

    @task(3)
    def get_all_items(self):
        """Test GET /glossary/getAll/ endpoint"""
        with self.client.get(
            "/glossary/getAll/",
            catch_response=True,
            name="REST: GetAll"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def update_item(self):
        """Test PUT /glossary/update/{id}/ endpoint"""
        item_id = self.existing_item_id
        payload = {
            "name": f"Updated Item {random.randint(1, 1000)}",
            "description": f"Updated description at {random.randint(1, 1000)}"
        }

        with self.client.put(
            f"/glossary/update/{item_id}/",
            json=payload,
            catch_response=True,
            name="REST: UpdateItem"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")


class GlossaryGRPCUser(User):
    """Load test for gRPC endpoints"""
    host = "localhost:50051"
    wait_time = between(1, 3)

    def on_start(self):
        """Setup: Create gRPC channel and stub"""
        self.channel = grpc.insecure_channel(self.host)
        self.stub = glossary_pb2_grpc.GlossaryServiceStub(self.channel)

        # Get an existing item ID for update tests
        try:
            request = glossary_pb2.GetAllGlossaryItemsRequest()
            response = self.stub.GetAllItems(request)
            if response.items:
                self.existing_item_id = response.items[0].id
            else:
                self.existing_item_id = 1
        except Exception:
            self.existing_item_id = 1

    def on_stop(self):
        """Cleanup: Close gRPC channel"""
        if hasattr(self, 'channel'):
            self.channel.close()

    @task(3)
    def get_all_items(self):
        """Test GetAllItems gRPC endpoint"""
        request = glossary_pb2.GetAllGlossaryItemsRequest()

        start_time = time.time()
        try:
            response = self.stub.GetAllItems(request)
            total_time = int((time.time() - start_time) * 1000)

            self.environment.events.request.fire(
                request_type="gRPC",
                name="gRPC: GetAllItems",
                response_time=total_time,
                response_length=len(response.items),
                exception=None,
                context={}
            )
        except grpc.RpcError as e:
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="gRPC",
                name="gRPC: GetAllItems",
                response_time=total_time,
                response_length=0,
                exception=e,
                context={}
            )

    @task(1)
    def update_item(self):
        """Test UpdateItem gRPC endpoint"""
        request = glossary_pb2.UpdateGlossaryItemRequest(
            id=self.existing_item_id,
            name=f"Updated Item {random.randint(1, 1000)}",
            description=f"Updated description at {random.randint(1, 1000)}"
        )

        start_time = time.time()
        try:
            response = self.stub.UpdateItem(request)
            total_time = int((time.time() - start_time) * 1000)

            # Check if response has error
            if response.HasField('error'):
                raise Exception(f"gRPC error: {response.error.message}")

            self.environment.events.request.fire(
                request_type="gRPC",
                name="gRPC: UpdateItem",
                response_time=total_time,
                response_length=1,
                exception=None,
                context={}
            )
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="gRPC",
                name="gRPC: UpdateItem",
                response_time=total_time,
                response_length=0,
                exception=e,
                context={}
            )


# ============================================================================
# Load Test Shapes for Different Scenarios
# ============================================================================
# Run with: locust -f locustfile.py --load-shape <ShapeClassName>
# Or set environment variable: LOAD_TEST_MODE=normal|stress|stability


class NormalWorkloadShape(LoadTestShape):
    """
    Рабочая нагрузка (нормальный режим)

    Simulates realistic usage pattern with gradual ramp-up:
    - 0-30s: Ramp up to 10 users (morning startup)
    - 30s-1min: Ramp up to 50 users (business hours)
    - 1-2.5min: Hold at 50 users (steady operation)
    - 2.5-3min: Ramp up to 80 users (peak hour)
    - 3-4min: Hold at 80 users
    - 4-4.5min: Ramp down to 30 users (afternoon lull)
    - 4.5-5min: Hold at 30 users

    Total duration: 5 minutes
    Peak users: 80
    """

    stages = [
        {"duration": 30, "users": 10, "spawn_rate": 2},     # 0-30s: morning startup
        {"duration": 30, "users": 50, "spawn_rate": 5},     # 30s-1min: ramp to business hours
        {"duration": 90, "users": 50, "spawn_rate": 2},     # 1-2.5min: steady operation
        {"duration": 30, "users": 80, "spawn_rate": 5},     # 2.5-3min: peak hour
        {"duration": 60, "users": 80, "spawn_rate": 2},     # 3-4min: hold peak
        {"duration": 30, "users": 30, "spawn_rate": 5},     # 4-4.5min: afternoon lull
        {"duration": 30, "users": 30, "spawn_rate": 2},     # 4.5-5min: steady low
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
            run_time -= stage["duration"]

        return None


class StressTestShape(LoadTestShape):
    """
    Стресс-тест (приближение к пику)

    Aggressive load increase to find performance limits:
    - 0-20s: Ramp up to 50 users rapidly
    - 20-40s: Ramp up to 100 users
    - 40s-1min: Ramp up to 200 users
    - 1-1.5min: Ramp up to 500 users
    - 1.5-2min: Hold at 500 users (observe system behavior)
    - 2-2.5min: Spike to 800 users
    - 2.5-3min: Hold at 800 users (find breaking point)

    Total duration: 3 minutes
    Peak users: 800
    """

    stages = [
        {"duration": 20, "users": 50, "spawn_rate": 10},     # 0-20s: quick ramp
        {"duration": 20, "users": 100, "spawn_rate": 10},    # 20-40s
        {"duration": 20, "users": 200, "spawn_rate": 15},    # 40s-1min
        {"duration": 30, "users": 500, "spawn_rate": 20},    # 1-1.5min
        {"duration": 30, "users": 500, "spawn_rate": 10},    # 1.5-2min: hold and observe
        {"duration": 30, "users": 800, "spawn_rate": 25},    # 2-2.5min: spike
        {"duration": 30, "users": 800, "spawn_rate": 15},    # 2.5-3min: hold peak
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
            run_time -= stage["duration"]

        return None


class StabilityTestShape(LoadTestShape):
    """
    Тест на стабильность (при длительной нагрузке)

    Long-duration test to check for degradation and memory leaks:
    - 0-1 min: Ramp up to 100 users (warmup)
    - 1-9 min: Hold at 100 users (steady load)
    - 9-10 min: Ramp down to 0 (graceful shutdown)

    Total duration: 10 minutes
    Steady users: 100

    Monitor for:
    - Memory leaks
    - Performance degradation over time
    - Connection pool exhaustion
    - Database connection issues
    """

    stages = [
        {"duration": 60, "users": 100, "spawn_rate": 5},     # 0-1 min: warmup
        {"duration": 480, "users": 100, "spawn_rate": 2},    # 1-9 min: steady load (8 minutes)
        {"duration": 60, "users": 0, "spawn_rate": 5},       # 9-10 min: ramp down
    ]

    def tick(self):
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
            run_time -= stage["duration"]

        return None


# Auto-select load shape based on environment variable
# Usage: LOAD_TEST_MODE=stress locust -f locustfile.py
def get_load_shape():
    """Returns the appropriate load shape based on LOAD_TEST_MODE env var"""
    mode = os.getenv("LOAD_TEST_MODE", "").lower()

    shapes = {
        "normal": NormalWorkloadShape,
        "stress": StressTestShape,
        "stability": StabilityTestShape,
    }

    return shapes.get(mode)
