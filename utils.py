

def calculate_bmr(gender, weight, height, age):
    '''
    calculates bmr
    '''
    if gender.lower() == "male":
        return 88.362 + 13.397 * weight + 4.799 * height - 5.677 * age
    elif gender.lower() == "female":
        return 447.593 + 9.247 * weight + 3.098 * height - 4.33 * age
    
