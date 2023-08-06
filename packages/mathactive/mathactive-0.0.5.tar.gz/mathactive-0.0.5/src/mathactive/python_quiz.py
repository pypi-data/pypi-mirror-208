import editdistance

# Define the questions and their corresponding answers
QA_DICT = {
    "Step by step list of instructions that if followed exactly will solve the problem under consideration is called a/an ___": "algorithm",
    "What is the command to print something in Python?": "print",
    "___ is a notation that is more precise than English but generally not as precise as a programming language": "pseudocode",
    "Which loop (in Python) would you use if you want to receive input from the user of your program but you don’t know how long it’ll take for them to be done with your code": "while",
    "Comment 'this word' in Python": "#this word",
    "How do you write 'snake code' in camel code": "SnakeCode",
    "How can you determine the type of a variable?": "type",
    "What is the data type of ‘this is what kind of data’?": "string",
    "After the following statements, what is the value of y ? x = 15 y = x x = 2023": "15",
    "What is a built-in Python function that returns the number of characters in a string?": "len"

}

# Define a function to ask a question and compare the user's answer to the correct answer


def ask_question(question, answer):
    user_answer = input(question + " ")
    similarity_score = 1 - (editdistance.eval(user_answer, answer) / max(len(user_answer), len(answer)))
    return similarity_score


def main(qa_dict=QA_DICT):
    # Ask each question and keep track of the user's total score
    total_score = 0
    for question, answer in qa_dict.items():
        score = ask_question(question, answer)
        total_score += score

    return dict(total_score=total_score, num_questions=len(qa_dict))


if __name__ == '__main__':
    results = main()
    print("Your score is: {total_score} or {total_score*100/num_questions}\%.".format(**results))
