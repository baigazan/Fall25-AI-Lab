def fizzbuzz():
    print("Frizzbuzz Game")

    previous = 0
    score = 0
    
    for num in range(1,11):
        total_num = previous + num
        print(f"number is {total_num }")
        ans = input("enter your answer : ")
        previous = num
        
        if total_num % 3 == 0 and total_num % 5 == 0 :
            result =  "fizzbuzz"
        elif total_num % 3 == 0:
            result =  "fizz"
        elif total_num % 5 == 0:
            result =  "buzz"
        else:
            result = str(total_num)
        if ans == result:
            print(f"correct: {total_num} is {result}")
            score += 1
        else:
            print("wrong answer")
    print("Game over")
    print(f"final score : {score}") 

fizzbuzz()   