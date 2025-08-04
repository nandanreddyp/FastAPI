import uvicorn
from fastapi import FastAPI, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, model_validator
from typing import Literal
import datetime


app = FastAPI()


# data

users = []; meals = []

food_db = {
    "Jeera Rice": {"calories": 250, "protein": 5, "carbs": 45, "fiber": 2},
    "Dal": {"calories": 180, "protein": 12, "carbs": 20, "fiber": 5},
    "Cucumber": {"calories": 16, "protein": 1, "carbs": 4, "fiber": 1}
}


# models

class User(BaseModel):
    name: str
    age: int
    weight: float
    height: float
    gender: Literal["male", "female"]
    goal: str = None

class Meal(BaseModel):
    userName: str
    mealType: Literal["breakfast", "lunch", "dinner"]
    foodItems: list[str]
    loggedAt: datetime.datetime = Field(default_factory=datetime.datetime.now)

class Webhook(BaseModel):
    userName: str
    message: str

# home route

@app.get("/")
async def root():
    """Redirects to docs page."""
    return RedirectResponse(url="/docs", status_code=status.HTTP_308_PERMANENT_REDIRECT)
    # return {"message": "Welcome to APP!"}


# user registration

@app.post("/register", status_code=status.HTTP_201_CREATED, response_model=dict)
def register(user: User):
    '''Create a user.'''
    if any(u.name == user.name for u in users):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists!")
    users.append(user)
    return {"message": "User register successfully!"}

@app.get("/users", response_model=list[User])
def all_users():
    '''List all users.'''
    return users


# meals logging

@app.post("/log_meals", response_model=dict)
def log_meals(meal: Meal):
    '''Creates a meal log.'''

    # checking if user exists
    if not any(user.name == meal.userName for user in users):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User, '{meal.userName}' not found!"
        )

    # validating food item
    not_found_foods = [
        food for food in meal.foodItems
        if food not in food_db
    ]
    if not_found_foods:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Food items, '{not_found_foods}' not in food_db!")

    meals.append(meal)
    return {"message": "Meal registered successfully!"}

@app.get("/log_meals/{userName}")
def get_meal_logs(
    userName: str,
    date: datetime.date = Query(None, description="Date in YYYY-MM-DD format", examples="2025-08-06")
):
    '''List all meals of a user.'''

    # checking if user exists
    if not any(user.name == userName for user in users):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User, '{userName}' not found!"
        )
    
    # filter meals
    filtered_meal_logs = [
        meal for meal in meals
        if meal.userName == userName and (not date or meal.loggedAt.date() == date)
    ]

    msg = f"All meals of user '{userName}'"
    if date:
        msg += f" on date '{date}'"

    return {"message": msg, "meals": filtered_meal_logs}


# User Status

@app.get('/status/{userName}')
def user_status(userName: str):
    """Returns information about user-consumed nutrients for today"""

    # checking if user exists
    if not any(user.name == userName for user in users):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User, '{userName}' not found!"
        )

    today_meals = [
        meal for meal in meals
        if meal.userName == userName and meal.loggedAt.date() == datetime.datetime.today().date()
    ]

    if not today_meals:
        return {"message": f"No meal logs found for user '{userName}' today."}

    nutrients = {"calories": 0, "protein": 0, "carbs": 0, "fiber": 0}
    for meal in today_meals:
        for food in meal.foodItems:
            food_nutrition = food_db.get(food)
            if food_nutrition:
                for key in nutrients:
                    nutrients[key] += food_nutrition.get(key, 0)
    return {"message": f"User, '{userName}' consumed nutrients today", "nutrients": nutrients}

@app.post('/webhook')
def webhook(payload: Webhook):
    user = payload.userName
    message = payload.message

    if not user or not message:
        raise HTTPException(status_code=400, detail="Missing 'user' or 'message'")
    
    # Validate user exists
    if not any(u.name == user for u in users):
        raise HTTPException(status_code=404, detail=f"User '{user}' not found")

    # extract message infor
    # Example "log lunch: Jeera Rice, Dal"
    try:
        message = message.strip()
        if not message.startswith("log "):
            raise ValueError

        parts = message.split(":")
        meal_type = parts[0].strip().split(" ")[-1]
        items = [item.strip().title() for item in parts[1].split(",") if item]

        if meal_type not in ["breakfast", "lunch", "dinner"]:
            raise ValueError(f"Invalid meal type: {meal_type}")

        invalid_items = [item for item in items if item not in food_db]
        if invalid_items:
            raise HTTPException(status_code=400, detail=f"Unknown food items: {invalid_items}")

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc) or "Invalid message format. Expected: 'log <meal>: item1, item2, ...'"
        ) from exc
    
    # create and store the meal
    new_meal = Meal(userName=user, mealType=meal_type, foodItems=items)
    meals.append(new_meal)

    return {"message": f"{meal_type.title()} logged for {user}", "meal": new_meal}

# running application

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
