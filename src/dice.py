import random

def roll_dice():
    d1 = random.randint(1,20)
    d2 = random.randint(1,20)
    return f"You rolled {d1} and {d2}"

