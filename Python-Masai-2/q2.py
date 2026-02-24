class StudentScores:
    def __init__(self, scores):
        self.scores = scores

    def highest_last_two(self):
        try:
            if len(self.scores) < 2:
                raise ValueError("Not enough scores")

            highest = max(self.scores[-1], self.scores[-2])
            print(f"Highest score among last two is {highest}")

        except ValueError:
            print("Not enough scores to find highest value.")