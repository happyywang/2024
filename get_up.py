import argparse
import pendulum
from github import Github


# 1 real get up
GET_UP_ISSUE_NUMBER = 1
GET_UP_MESSAGE_TEMPLATE = "Today's Wakeup Time is --{get_up_time}.\r\n\r\n 5 am project starts now ~~~。"

TIMEZONE = "Europe/Berlin"

def login(token):
    return Github(token)

def get_today_get_up_status(issue):
    comments = list(issue.get_comments())
    if not comments:
        return False, []
    up_list = []
    for comment in comments:
        try:
            s = comment.body.splitlines()[6]
            up_list.append(s)
        except Exception as e:
            print(str(e), "!!")
            continue
    latest_comment = comments[-1]
    now = pendulum.now(TIMEZONE)
    latest_day = pendulum.instance(latest_comment.created_at).in_timezone(
        "Europe/Berlin"
    )
    is_today = (latest_day.day == now.day) and (latest_day.month == now.month)
    return is_today, up_list


def make_get_up_message(weather_message):
    now = pendulum.now(TIMEZONE)
    # 3 - 8 means early for me
    is_get_up_early = 3 <= now.hour <= 8
    get_up_time = now.to_datetime_string()
    
    weather_msg = f"The current weather is {weather_message}\n" if weather_message else ""
    
    body = GET_UP_MESSAGE_TEMPLATE.format(get_up_time=get_up_time, weather_message = weather_msg)
    return body


def main(
    github_token,
    repo_name,
    weather_message
):
    u = login(github_token)
    repo = u.get_repo(repo_name)
    issue = repo.get_issue(GET_UP_ISSUE_NUMBER)
    is_today, _ = get_today_get_up_status(issue)
    if is_today:
        print("Today I have recorded the wake up time")
        return
    body = make_get_up_message(weather_message)
    
    if not is_today:
        issue.create_comment(body)
    else:
        print("You wake up late")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("github_token", help="github_token")
    parser.add_argument("repo_name", help="repo_name")
    parser.add_argument(
        "--weather_message", help="weather_message", nargs="?", default="", const="")
    
    options = parser.parse_args()
    main(
        options.github_token,
        options.repo_name,
        options.weather_message
    )
