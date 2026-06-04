from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os
import pymysql
from pymemcache.client.base import Client
import pika

app = FastAPI(title="Dharwad Local Eats - Enterprise Edition")

# --- MOCK DATA ---
MENU = [
    {"id": 1, "item": "Benne Masala Dosa", "price": 80},
    {"id": 2, "item": "Thatte Idli", "price": 40},
    {"id": 3, "item": "Kadai Paneer", "price": 180}
]

# --- INFRASTRUCTURE CONNECTIVITY CHECKS ---
def check_infrastructure():
    status = {"mysql": False, "memcache": False, "rabbitmq": False}
    
    # 1. Check MySQL
    try:
        conn = pymysql.connect(host=os.getenv('DB_HOST', 'mysql-service'), user='root', password='password', connect_timeout=1)
        status['mysql'] = True
        conn.close()
    except: pass

    # 2. Check Memcache
    try:
        client = Client((os.getenv('MEMCACHE_HOST', 'memcache-service'), 11211), timeout=1)
        client.version()
        status['memcache'] = True
    except: pass

    # 3. Check RabbitMQ
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=os.getenv('RABBITMQ_HOST', 'rabbitmq-service'), connection_attempts=1, socket_timeout=1))
        status['rabbitmq'] = True
        connection.close()
    except: pass

    return status

# --- API ENDPOINTS ---
@app.get("/api/system/status")
def get_status():
    return check_infrastructure()

@app.get("/api/menu")
def get_menu():
    # In a real app, this would check Memcache first, then MySQL!
    return {"menu": MENU}

@app.post("/api/checkout")
def process_order():
    # In a real app, this would write the user's order to MySQL and push a ticket to RabbitMQ!
    return {"message": "Order Successfully Placed! The kitchen is preparing your food."}


# --- FRONTEND WEB INTERFACE (HTML/JS) ---
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
        <div class="max-w-3xl mx-auto">
            
            <div class="flex justify-between items-center mb-8 border-b border-gray-700 pb-4">
                <h1 class="text-4xl font-bold text-orange-500">Dharwad Local Eats 🍛</h1>
                <div id="user-display" class="hidden text-green-400 font-semibold"></div>
            </div>

            <div id="login-section" class="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-lg mb-8">
                <h2 class="text-2xl font-semibold mb-4">Login or Register</h2>
                <input type="text" id="username" placeholder="Enter your Name" class="w-full p-2 rounded bg-gray-700 text-white border border-gray-600 mb-4">
                <button onclick="login()" class="bg-orange-500 hover:bg-orange-600 text-white font-bold py-2 px-4 rounded w-full">Connect to Database & Login</button>
            </div>

            <div id="app-section" class="hidden space-y-8">
                <div>
                    <h2 class="text-2xl font-semibold mb-4 text-blue-400">1. Select Items (From Memcache)</h2>
                    <div id="menu-container" class="space-y-3"></div>
                </div>

                <div class="bg-gray-800 p-6 rounded-lg border border-gray-700 shadow-lg">
                    <h2 class="text-2xl font-semibold mb-4 text-green-400">2. Your Cart</h2>
                    <ul id="cart-items" class="list-disc pl-5 mb-4 text-gray-300"></ul>
                    <div class="text-xl font-bold mb-4">Total: ₹<span id="cart-total">0</span></div>
                    <button onclick="checkout()" class="bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-4 rounded w-full">Place Order (Send to RabbitMQ)</button>
                </div>
            </div>

            <div id="success-section" class="hidden bg-green-900 border border-green-500 p-6 rounded-lg text-center mt-8">
                <h2 class="text-3xl font-bold text-green-400 mb-2">🎉 Order Successful!</h2>
                <p class="text-green-200">Your order has been saved to the database and sent to the kitchen queue.</p>
                <button onclick="location.reload()" class="mt-4 text-sm underline text-green-300">Start New Order</button>
            </div>

            <div class="mt-12 bg-black p-4 rounded-lg border border-gray-700 font-mono text-sm">
                <h3 class="text-gray-400 mb-2 border-b border-gray-700 pb-1">Kubernetes Infrastructure Status</h3>
                <div class="grid grid-cols-3 gap-4">
                    <div>MySQL DB: <span id="status-mysql" class="text-yellow-500">Checking...</span></div>
                    <div>Memcache: <span id="status-memcache" class="text-yellow-500">Checking...</span></div>
                    <div>RabbitMQ: <span id="status-rabbitmq" class="text-yellow-500">Checking...</span></div>
                </div>
            </div>

        </div>

        <script>
            let cart = [];
            let total = 0;

            // Check DevOps Infra Status
            fetch('/api/system/status').then(r => r.json()).then(data => {
                document.getElementById('status-mysql').innerHTML = data.mysql ? '<span class="text-green-500">Connected</span>' : '<span class="text-red-500">Disconnected</span>';
                document.getElementById('status-memcache').innerHTML = data.memcache ? '<span class="text-green-500">Connected</span>' : '<span class="text-red-500">Disconnected</span>';
                document.getElementById('status-rabbitmq').innerHTML = data.rabbitmq ? '<span class="text-green-500">Connected</span>' : '<span class="text-red-500">Disconnected</span>';
            });

            // Handle Login
            function login() {
                const user = document.getElementById('username').value;
                if(!user) return alert("Please enter a name");
                document.getElementById('login-section').classList.add('hidden');
                document.getElementById('user-display').innerText = `Welcome, ${user}`;
                document.getElementById('user-display').classList.remove('hidden');
                document.getElementById('app-section').classList.remove('hidden');
                loadMenu();
            }

            // Load Menu from API
            function loadMenu() {
                fetch('/api/menu').then(r => r.json()).then(data => {
                    const container = document.getElementById('menu-container');
                    data.menu.forEach(item => {
                        container.innerHTML += `
                            <div class="bg-gray-800 p-4 rounded flex justify-between items-center border border-gray-700">
                                <span class="text-lg">${item.item} - ₹${item.price}</span>
                                <button onclick="addToCart('${item.item}', ${item.price})" class="bg-blue-600 hover:bg-blue-700 px-4 py-1 rounded text-sm font-bold">Add</button>
                            </div>
                        `;
                    });
                });
            }

            // Handle Cart
            function addToCart(item, price) {
                cart.push({item, price});
                total += price;
                document.getElementById('cart-items').innerHTML += `<li>${item} (₹${price})</li>`;
                document.getElementById('cart-total').innerText = total;
            }

            // Handle Checkout
            function checkout() {
                if(cart.length === 0) return alert("Cart is empty!");
                fetch('/api/checkout', {method: 'POST'}).then(r => r.json()).then(data => {
                    document.getElementById('app-section').classList.add('hidden');
                    document.getElementById('success-section').classList.remove('hidden');
                });
            }
        </script>
    </body>
    </html>
    """