from ..generators import start_interactive_math
from ..hints import generate_hint
from .utils import load_user_data, dump_user, create_file

FILE_PATH = "users.json"


def process_user_message(user_id, message_text=""):
    """
    there are 2 possible states: question and hint, default is question
    Algorithm:
    1. load user by user id
    2. create new user in case he doesn't exist
    3. get student state, skill level and last answer result (right or wrong)
    4.
        4.1. If last state is question and last answer is wrong get user a hint
        4.2. If last state is question and last answer is right increase the skill_score and get new question
        4.3. If last state is hint and last answer is wrong decrease the skill_score and get user a new question
        4.4. If last state is hint and last answer is right leave the skill_score on the same level, but generate new question with same skill_score
    10. dump user
    """

    create_file(FILE_PATH)
    user_data = load_user_data(user_id, FILE_PATH)
    if len(user_data) == 0:
        user_data = {"skill_score": 0.01, "state": "question"}
    state = user_data["state"]
    if (
        state == "hint"
        and "answer" in user_data
        and user_data["answer"] == int(message_text)
    ) or (
        state == "question"
        and (
            message_text == ""
            or "answer" in user_data
            and user_data["answer"] == int(message_text)
        )
    ):
        do_increase_skill_score = (
            "leave"
            if state == "hint" or state == "question" and message_text == ""
            else "increase"
        )
        output = start_interactive_math(
            user_data["skill_score"], do_increase_skill_score
        )
        user_data["state"] = "question"
    elif "answer" in user_data and user_data["answer"] != int(message_text):
        if state == "hint":
            do_increase_skill_score = "decrease"
            user_data["state"] = "question"
        elif state == "question":
            do_increase_skill_score = "leave"
            user_data["state"] = "hint"
        output = (
            start_interactive_math(user_data["skill_score"], do_increase_skill_score)
            if state == "hint"
            else generate_hint(**user_data)
        )

    user_data.update(**output)

    dump_user(user_id, user_data, FILE_PATH)
    text = output["text"]
    message_package = {
        "messages": text.split(" "),
        "input_prompt": message_text,
        "state": user_data["state"],
    }
    return message_package
