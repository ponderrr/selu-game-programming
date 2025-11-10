import random

def guessThatNumberUser():
    number = random.randint(1, 100)
    while True:
        guess = int(input("Enter a number between 1 and 100: ")) # user guess

        if guess > number: 
            print("lower")   # number is lower
        elif guess < number:
            print("higher")    # number is higher
        else:
            print("that's it")  # equal
            break

guessThatNumberUser()