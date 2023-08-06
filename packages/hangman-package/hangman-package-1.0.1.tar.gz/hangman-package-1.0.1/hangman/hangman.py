import random
from hangman.drawings import drawings


words = [
    "python",
    "java",
    "javaScript",
    "swift",
    "kotlin",
    "ruby",
    "perl",
    "php",
    "rust",
    "go",
    "haskell",
    "scala",
    "dart",
    "lua",
    "typescript",
    "groovy",
    "assembly",
    "elixir",
    "sql",
    "html",
    "css",
]


class Hangman:
    def __init__(self, words=words):
        self.words = words
        self.guessed = []

    def choose_word(self):
        word = random.choice(self.words)
        return word

    def setup(self):
        self.word = self.choose_word()

        for i in range(len(self.word)):
            self.guessed.append("_")

        self.wrong_guesses = 0
        self.used_letters = []

    def display_state(self):
        print(drawings[self.wrong_guesses])
        print()
        print(" ".join(self.guessed))
        print()
        print("Used letters:", ", ".join(self.used_letters))

    def check_guess(self, guess):
        if (
            len(guess) != 1
            or not guess.isalpha()
            or guess in self.used_letters
            or guess in self.guessed
        ):
            print("Invalid guess!")
            return

        if guess in self.word:
            print("Correct!")
            for i in range(len(self.word)):
                if self.word[i] == guess:
                    self.guessed[i] = guess
        else:
            self.wrong_guesses += 1
            self.used_letters.append(guess)
            print("Incorrect!")

    def check_game_over(self):
        if "_" not in self.guessed:
            print(f'You win! The word was "{self.word}"')
            print(drawings[self.wrong_guesses])
            return True

        if self.wrong_guesses >= len(drawings) - 1:
            print(f'You lose! The word was "{self.word}"')
            print(drawings[self.wrong_guesses])
            return True

    def play(self):
        self.setup()
        while True:
            self.display_state()
            guess = input("Guess a letter: ").lower()
            self.check_guess(guess)
            if self.check_game_over():
                break
