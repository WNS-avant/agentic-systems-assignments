class StudentMarks:
    def __init__(self, marks):
        self.marks = marks

    def last_three_average(self):
        try:
            if len(self.marks) < 3:
                raise ValueError("Not enough marks")

            average = (self.marks[-1] + self.marks[-2] + self.marks[-3]) / 3
            print(f"Average of last three marks is {average}")

        except ValueError:
            print("Not enough marks to calculate average.")