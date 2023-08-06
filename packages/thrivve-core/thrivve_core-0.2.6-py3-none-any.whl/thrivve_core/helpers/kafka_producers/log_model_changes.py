from thrivve_core import Topics, Producer


def log_model_changes(
        changes
):
    data = dict(
        topic=Topics.LOG_MODEL_CHANGES,
        # todo: why I should pass this. I see the finance consumer required it.
        payload=changes,
        # token=token,
    )

    Producer().send_topic(
        topic=Topics.LOG_MODEL_CHANGES, datajson=data
    )
