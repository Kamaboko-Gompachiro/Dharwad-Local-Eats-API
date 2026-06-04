from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Dharwad Local Eats API")

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

@app.get("/api/orders/popular")
def get_popular_orders():
    return {
        "region": "Karnataka",
        "trending_items": [
            {"id": 1, "item": "Benne Masala Dosa", "price": 80, "status": "available"},
            {"id": 2, "item": "Thatte Idli", "price": 40, "status": "available"},
            {"id": 3, "item": "Kadai Paneer", "price": 180, "status": "preparing"}
        ]
    }

# NEW: The Web Interface
@app.get("/", response_class=HTMLResponse)
def serve_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dharwad Local Eats</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-900 text-white font-sans p-8">
        <div class="max-w-2xl mx-auto">
            <h1 class="text-4xl font-bold text-orange-500 mb-2">Dharwad Local Eats 🍛</h1>
            <p class="text-gray-400 mb-8">Live Kubernetes API Traffic</p>
            
            <div id="menu-container" class="space-y-4">
                <p class="text-gray-500 animate-pulse">Fetching live data from backend pods...</p>
            </div>
        </div>

        <script>
            fetch('/api/orders/popular')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('menu-container');
                    container.innerHTML = ''; 
                    data.trending_items.forEach(item => {
                        const statusColor = item.status === 'available' ? 'text-green-400' : 'text-yellow-400';
                        container.innerHTML += `
                            <div class="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-lg flex justify-between items-center">
                                <div>
                                    <h2 class="text-2xl font-semibold">${item.item}</h2>
                                    <p class="text-gray-400 text-sm mt-1 border-t border-gray-700 pt-1">ID: ${item.id} | Status: <span class="${statusColor}">${item.status}</span></p>
                                </div>
                                <div class="text-2xl font-bold text-orange-400">₹${item.price}</div>
                            </div>
                        `;
                    });
                });
        </script>
    </body>
    </html>
    """