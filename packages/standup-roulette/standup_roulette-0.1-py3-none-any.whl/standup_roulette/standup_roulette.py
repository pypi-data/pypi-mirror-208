import random


def main():
    # Define list of persons
    persons = ['Matthias', 'Martin', 'Bharat', 'Timo', 'Karl', 'Hiep', 'Nitin', 'Kai', 'Robert']

    # Select a random person from the list
    random_person = random.choice(persons)

    # Select a random direction
    direction = random.choice(['clockwise', 'counterclockwise'])

    # Print the selected person and direction
    print('Selected person:', random_person)
    print('Selected direction:', direction)


if __name__ == '__main__':
    main()
