import random
from typing import Literal
from .questions import generate_question_data
from .utils import get_next_skill_score, generate_start_stop_step


def start_interactive_math(
    skill_score=0.01,
    do_increase_skill_score: Literal["increase", "decrease", "leave"] = "leave",
):
    next_skill_score = get_next_skill_score(skill_score, do_increase_skill_score)
    generated_nums = generate_start_stop_step(skill_score)
    start  = generated_nums['start']
    stop  = generated_nums['stop']
    step  = generated_nums['step']
    for value in range(start, stop + 1, step):
        if value <= stop:
            stop = value
        else:
            break
    question_data = generate_question_data(
        start, stop, step, question_num=random.randint(0, 4)
    )

    output = {
        "text": question_data["question"],
        "skill_score": next_skill_score,
        'start': question_data["start"], 
        'stop': question_data["stop"], 
        'step': question_data["step"], 
        'answer': question_data["answer"]
    }
    return output
