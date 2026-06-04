from fastapi import FastAPI

app = FastAPI(title="Dharwad Local Eats API")

@app.get("/health")
def health_check():
    # Kubernetes will hit this endpoint constantly. If it fails, K8s kills the pod.
    return {"status": "healthy", "database": "connected"}

@app.get("/api/orders/popular")
def get_popular_orders():
    # Mock data for our Zomato-style microservice
    return {
        "region": "Karnataka",
        "trending_items": [
            {"id": 1, "item": "Benne Masala Dosa", "price": 80, "status": "available"},
            {"id": 2, "item": "Thatte Idli", "price": 40, "status": "available"},
            {"id": 3, "item": "Kadai Paneer", "price": 180, "status": "preparing"}
        ]
    }