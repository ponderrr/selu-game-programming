import random

def guessThatNumberComputer():
    number = int(input("Pick a number between 1 and 100 (computer will try to guess): "))
    guess = random.randint(1, 100)
    low = 1
    high = 100

    while True:
        print("Computer guesses:", guess)

        # if higher
        if guess > number:
            print("too high")
            high = guess
            guess = random.randint(low, high)

        # elif lower
        elif guess < number:
            print("too low")
            low = guess
            guess = random.randint(low, high)

        # else equal
        else:
            print("that's it")
            break

guessThatNumberComputer()
