class StudentPerformance:
    def __init__(self, scores):
        self.scores = scores

    def score_difference(self):
        try:
            if len(self.scores) == 0:
                raise ValueError("Empty list")

            difference = self.scores[-1] - self.scores[0]
            print(f"Difference between last and first score is {difference}")

        except ValueError:
            print("No scores available to calculate difference.")