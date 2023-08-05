import json
import requests

try:
    from prefect.engine.state import Failed

    prefect_2 = False
except Exception as e:
    prefect_2 = True

if prefect_2 is False:

    import requests
    import os

    from maisaedu_utilities_prefect.environment import get_env
    from maisaedu_utilities_prefect.constants import PRODUCTION, LOCAL, SLACK, TEAMS
    from prefect.engine.state import Failed
    from prefect.utilities.notifications import slack_notifier

    def notifier_factory(states=[Failed], type=SLACK):
        def empty_handler(obj, old_state, new_state):
            return

        def teams_handler(obj, old_state, new_state):
            if Failed in states:
                if new_state.is_failed():
                    msg = "{0} is now in a Failed state".format(obj.name)
                    url = os.environ.get("TEAMS_WEBHOOK_URL")
                    requests.post(url, json={"text": msg})

            return new_state

        if get_env() == PRODUCTION:
            if type == SLACK:
                notifier = slack_notifier(only_states=states)
            elif type == TEAMS:
                notifier = teams_handler
        elif get_env() == LOCAL:
            notifier = empty_handler

        return notifier

else:

    def notifier_factory():
        return None


def send_teams_alert_on_failure(
    task_future, teams_webhook_path="data/teams_webhook_url.json"
):
    fallback_path = "data/teams_webhook_url.json"
    try:
        with open(teams_webhook_path) as file:
            teams_webhook = json.load(file)
    except Exception as e:
        with open(fallback_path) as file:
            teams_webhook = json.load(file)

    tasks_future = []
    if type(task_future) != list:
        tasks_future.append(task_future)
    else:
        tasks_future = task_future

    for task_future in tasks_future:
        task_future.wait()  # block until completion
        if task_future.get_state().is_failed():
            name_ = task_future.task_run.name
            id_ = task_future.task_run.flow_run_id
            message_ = task_future.task_run.state.message

            requests.post(
                teams_webhook["url"],
                json={
                    "text": f"The task `{name_}` failed in a flow run `{id_}` because of this reason -> `{message_}`"
                },
            )
