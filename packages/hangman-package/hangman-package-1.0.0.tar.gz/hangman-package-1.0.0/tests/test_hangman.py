from hangman import Hangman


def test_choose_word():
    hangman = Hangman(words=["hello", "world"])
    word = hangman.choose_word()
    assert word in ["hello", "world"]


def test_correct_check_guess():
    hangman = Hangman(words=["hello"])
    hangman.setup()
    hangman.check_guess("h")
    assert hangman.guessed == ["h", "_", "_", "_", "_"]


def test_wrong_check_guess():
    hangman = Hangman(words=["hello"])
    hangman.setup()
    hangman.check_guess("a")
    assert hangman.wrong_guesses == 1


def test_check_game_over_win():
    hangman = Hangman(words=["hello"])
    hangman.setup()
    hangman.guessed = ["h", "e", "l", "l", "o"]
    assert hangman.check_game_over()


def test_check_game_over_loss():
    hangman = Hangman(words=["hello"])
    hangman.setup()
    hangman.wrong_guesses = 7
    assert hangman.check_game_over()
