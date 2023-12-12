def get_player_numbers(player_name):
    print(f"{player_name}, enter your 4 numbers (from 1 to 20), separated by spaces:")
    numbers = input().split()
    return [int(num) for num in numbers]


def evaluate_guess(guess, target):
    correct_numbers = set(guess) & set(target)
    return len(correct_numbers)


def main():
    print("Welcome to the Number Guessing Game!")
    player1_name = input("Enter the name of Player 1: ")
    player2_name = input("Enter the name of Player 2: ")

    player1_numbers = get_player_numbers(player1_name)
    player2_numbers = get_player_numbers(player2_name)

    attempts = 0
    while True:
        print(f"\n{player1_name}'s Turn:")
        guess = get_player_numbers(player1_name)
        correct_numbers = evaluate_guess(guess, player2_numbers)

        print("Correct Numbers: {}".format(correct_numbers))

        attempts += 1

        if correct_numbers == 4:
            print(
                f"{player1_name} guessed all correct numbers in {attempts} attempts! {player1_name} wins!")
            break

        print(f"\n{player2_name}'s Turn:")
        guess = get_player_numbers(player2_name)
        correct_numbers = evaluate_guess(guess, player1_numbers)

        print("Correct Numbers: {}".format(correct_numbers))

        attempts += 1

        if correct_numbers == 4:
            print(
                f"{player2_name} guessed all correct numbers in {attempts} attempts! {player2_name} wins!")
            break


if __name__ == "__main__":
    main()
