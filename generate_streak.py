import os
import requests
from datetime import datetime, timedelta


USERNAME = "mithunnaik28"

TOKEN = os.environ["GH_TOKEN"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""


def get_contributions():
    response = requests.post(
        "https://api.github.com/graphql",
        json={
            "query": QUERY,
            "variables": {
                "login": USERNAME
            }
        },
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        }
    )

    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise Exception(data["errors"])

    calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]

    days = []

    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            days.append({
                "date": datetime.strptime(day["date"], "%Y-%m-%d").date(),
                "count": day["contributionCount"]
            })

    return calendar["totalContributions"], days


def calculate_streaks(days):
    days = sorted(days, key=lambda x: x["date"])

    # Current streak
    current = 0
    current_start = None
    current_end = None

    today = days[-1]["date"]

    # Start from latest day
    i = len(days) - 1

    # If today has no contribution, check yesterday
    if days[i]["count"] == 0:
        if i > 0 and days[i - 1]["date"] == today - timedelta(days=1):
            i -= 1
        else:
            i = -1

    if i >= 0 and days[i]["count"] > 0:
        current_end = days[i]["date"]
        current = 1
        current_start = days[i]["date"]

        i -= 1

        while i >= 0:
            expected = days[i + 1]["date"] - timedelta(days=1)

            if days[i]["date"] == expected and days[i]["count"] > 0:
                current += 1
                current_start = days[i]["date"]
                i -= 1
            else:
                break

    # Longest streak
    longest = 0
    longest_start = None
    longest_end = None

    temp = 0
    temp_start = None

    for i, day in enumerate(days):

        if day["count"] > 0:

            if temp == 0:
                temp_start = day["date"]

            temp += 1

            if temp > longest:
                longest = temp
                longest_start = temp_start
                longest_end = day["date"]

        else:
            temp = 0

    return {
        "current": current,
        "current_start": current_start,
        "current_end": current_end,
        "longest": longest,
        "longest_start": longest_start,
        "longest_end": longest_end
    }


def format_date(date):
    if date is None:
        return "-"

    return date.strftime("%b %d")


def create_svg(total, streak):
    width = 680
    height = 270

    current_dates = (
        f"{format_date(streak['current_start'])} - "
        f"{format_date(streak['current_end'])}"
    )

    longest_dates = (
        f"{format_date(streak['longest_start'])} - "
        f"{format_date(streak['longest_end'])}"
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}">

<rect
    x="0"
    y="0"
    width="680"
    height="270"
    rx="8"
    fill="#ffffff"
    stroke="#d8dee4"/>

<!-- vertical lines -->

<line
    x1="218"
    y1="35"
    x2="218"
    y2="235"
    stroke="#d8dee4"/>

<line
    x1="450"
    y1="35"
    x2="450"
    y2="235"
    stroke="#d8dee4"/>


<!-- TOTAL -->

<text
    x="110"
    y="110"
    text-anchor="middle"
    font-size="40"
    font-weight="bold"
    font-family="Arial"
    fill="#111111">

    {total}

</text>

<text
    x="110"
    y="160"
    text-anchor="middle"
    font-size="19"
    font-family="Arial"
    fill="#333333">

    Total Contributions

</text>

<text
    x="110"
    y="198"
    text-anchor="middle"
    font-size="16"
    font-family="Arial"
    fill="#666666">

    Contributions

</text>


<!-- CURRENT STREAK -->

<text
    x="335"
    y="112"
    text-anchor="middle"
    font-size="40"
    font-weight="bold"
    font-family="Arial"
    fill="#111111">

    {streak["current"]}

</text>

<text
    x="335"
    y="160"
    text-anchor="middle"
    font-size="19"
    font-weight="bold"
    font-family="Arial"
    fill="#ff8c00">

    🔥 Current Streak

</text>

<text
    x="335"
    y="198"
    text-anchor="middle"
    font-size="16"
    font-family="Arial"
    fill="#666666">

    {current_dates}

</text>


<!-- LONGEST -->

<text
    x="565"
    y="110"
    text-anchor="middle"
    font-size="40"
    font-weight="bold"
    font-family="Arial"
    fill="#111111">

    {streak["longest"]}

</text>

<text
    x="565"
    y="160"
    text-anchor="middle"
    font-size="19"
    font-family="Arial"
    fill="#333333">

    Longest Streak

</text>

<text
    x="565"
    y="198"
    text-anchor="middle"
    font-size="16"
    font-family="Arial"
    fill="#666666">

    {longest_dates}

</text>

</svg>
'''

    with open("streak.svg", "w", encoding="utf-8") as f:
        f.write(svg)


total, days = get_contributions()

streak = calculate_streaks(days)

create_svg(total, streak)

print("Streak SVG generated successfully!")
