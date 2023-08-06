import random


def generate_hint(**kwargs):
    hints = [f"What number is greater than {kwargs['answer'] - 1} and less than {kwargs['answer'] + 1}?"]
    hint = random.choice(hints)

    output = {
        "text": hint,
        "skill_score": kwargs['skill_score'],
        'start': kwargs['start'], 
        'stop': kwargs['stop'], 
        'step': kwargs['step'], 
        'answer': kwargs['answer']
    }
    return output
