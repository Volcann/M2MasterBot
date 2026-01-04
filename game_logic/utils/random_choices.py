import random


def temp_random_choices(score):
    if score < 50:
        random_choices = [2, 4, 8]
    elif score < 100:
        random_choices = [2, 4, 8, 16]
    elif score < 200:
        random_choices = [2, 4, 8, 16, 32]
    elif score < 300:
        random_choices = [2, 4, 8, 16, 32, 64]
    else:
        random_choices = [2, 4, 8, 16, 32, 64]
        
    print(random_choices)
    return random.choices(random_choices)[0]


def dynamic_random_choices(max_value):
    random_choice = set()
    count = 0
    max_value = max_value // 2 // 2
    
    while True:
        if count == 6:
            break
        max_value = max_value // 2
        random_choice.add(max_value)
        count += 1

    random_choices = sorted(list(random_choice))
    return random_choices
