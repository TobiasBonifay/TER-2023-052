from locust import HttpUser, task, between


class UserBehavior(HttpUser):
    wait_time = between(1, 2)

    @task(2)
    def get_data(self):
        self.client.get("/data")

    @task(1)
    def put_data(self):
        self.client.put("/data", json={"key": "value"})

    @task(1)
    def compute(self):
        self.client.get("/compute")
