try:
    a = int(input("Enter a number: "))
    b = int(input("Enter another number: "))
except ValueError:
    print("Invalid input")
else:
    print("Sum:", a + b)

    if b == 0:
        print("Cannot divide by zero")
    else:
        print("Division:", a / b)