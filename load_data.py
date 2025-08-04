import requests

BASE_URL = "http://127.0.0.1:5000"

users = [
    {
        "name": "Rahul",
        "age": 28,
        "weight": 70.5,
        "height": 175,
        "gender": "male",
        "goal": "maintain"
    },
    {
        "name": "Anita",
        "age": 32,
        "weight": 60.0,
        "height": 162,
        "gender": "female",
        "goal": "weight_loss"
    }
]

meals = [
    {
        "userName": "Rahul",
        "mealType": "lunch",
        "foodItems": ["Jeera Rice", "Dal"]
    },
    {
        "userName": "Rahul",
        "mealType": "breakfast",
        "foodItems": ["Jeera Rice"]
    },
    {
        "userName": "Anita",
        "mealType": "dinner",
        "foodItems": ["Dal", "Cucumber"]
    }
]

def load_users():
    for user in users:
        response = requests.post(f"{BASE_URL}/register", json=user)
        if response.status_code == 201:
            print(f"✅ Registered user: {user['name']}")
        elif response.status_code == 400:
            print(f"⚠️ User already exists: {user['name']}")
        else:
            print(f"❌ Failed to register {user['name']}: {response.text}")

def load_meals():
    for meal in meals:
        response = requests.post(f"{BASE_URL}/log_meals", json=meal)
        if response.status_code == 200:
            print(f"✅ Logged meal for {meal['userName']} - {meal['mealType']}")
        else:
            print(f"❌ Failed to log meal: {response.text}")

if __name__ == "__main__":
    load_users()
    load_meals()
