from .utils import convert_sequence_to_string


def generate_question_data(start, stop, step, question_num=1):
    """returns question by provided number with filled parameters

    parameters
    ----------
    :start: current number
    :stop: stop value
    :step: interval between current and next numbers
    :question_num: question number"""
    seq = convert_sequence_to_string(start, stop, step)
    questions = [
        f"Let's practice counting   {convert_sequence_to_string(start, stop, step, sep='... ')}   After {stop}, what is the next number you will count?\n{seq}",
        f"What number comes {step} number after {stop}?\n{seq}",
        f"We're counting by {step}s.  What number is 1 after {stop}?\n{seq}",
        f"What is {step} number up from {stop}?\n{seq}",
        f"If we count up {step} from {stop}, what number is next?\n{seq}",
    ]
    questions_data = []
    for quest in questions:
        questions_data.append(
            {
                "question": quest,
                "answer": stop + step,
                "start": start,
                "stop": stop,
                "step": step,
            }
        )
    return questions_data[question_num]
