from . import models


def data_was_changed(answers: models.Answers) -> bool:

    # No EPC -> nothing to change
    if answers.selected_epc is None:
        return False

    # Dynamically find all the prepopulatable fields:
    for field in models.Answers._meta.get_fields():
        if field.name[-5:] == "_orig":
            # Data has been corrected if data derived value was presented
            # and the user entered a value which does not agree with it
            data_derived_value = getattr(answers, field.name)
            user_entered_value = getattr(answers, field.name[:-5])

            if (
                data_derived_value not in ["", None]
                and user_entered_value not in ["", None]
                and data_derived_value != user_entered_value
            ):
                return True

    return False
