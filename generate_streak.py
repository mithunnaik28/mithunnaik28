import os
import json
import urllib.request
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

    data = json.dumps({
        "query": QUERY,
        "variables": {
            "login": USERNAME
        }
    }).encode("utf-8")

    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=data,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    if "errors" in result:
        print(result["errors"])
        raise Exception("GitHub API error")

    calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]

    days = []

    for week in calendar["weeks"]:
        for day in week["contributionDays"]:

            days.append({
                "date": datetime.strptime(
                    day["date"],
                    "%Y-%m-%d"
                ).date(),

                "count": day["contributionCount"]
            })

    return calendar["totalContributions"], days


def calculate_streaks(days):

    days.sort(key=lambda x: x["date"])

    # -------------------------
    # CURRENT STREAK
    # -------------------------

    current = 0
    current_start = None
    current_end = None

    i = len(days) - 1

    # Latest day
    if days[i]["count"] == 0:

        if (
            i > 0
            and days[i - 1]["date"]
            == days[i]["date"] - timedelta(days=1)
            and days[i - 1]["count"] > 0
        ):
            i -= 1
        else:
            i = -1

    if i >= 0 and days[i]["count"] > 0:

        current = 1
        current_end = days[i]["date"]
        current_start = days[i]["date"]

        i -= 1

        while i >= 0:

            if (
                days[i]["date"]
                == days[i + 1]["date"] - timedelta(days=1)
                and days[i]["count"] > 0
            ):

                current += 1
                current_start = days[i]["date"]

                i -= 1

            else:
                break

    # -------------------------
    # LONGEST STREAK
    # -------------------------

    longest = 0
    longest_start = None
    longest_end = None

    temp = 0
    temp_start = None

    for day in days:

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

    current_dates = (
        f"{format_date(streak['current_start'])} - "
        f"{format_date(streak['current_end'])}"
    )

    longest_dates = (
        f"{format_date(streak['longest_start'])} - "
        f"{format_date(streak['longest_end'])}"
    )

    svg = f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="680"
height="270"
viewBox="0 0 680 270">

<rect
x="0"
y="0"
width="680"
height="270"
rx="8"
fill="white"
stroke="#d8dee4"/>

<!-- Vertical lines -->

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


<!-- TOTAL CONTRIBUTIONS -->

<text
x="110"
y="110"
text-anchor="middle"
font-size="40"
font-weight="bold"
font-family="Arial"
fill="#111">

{total}

</text>

<text
x="110"
y="160"
text-anchor="middle"
font-size="18"
font-family="Arial"
fill="#333">

Total Contributions

</text>


<!-- CURRENT STREAK -->

<text
x="335"
y="110"
text-anchor="middle"
font-size="40"
font-weight="bold"
font-family="Arial"
fill="#111">

{streak["current"]}

</text>

<text
x="335"
y="160"
text-anchor="middle"
font-size="18"
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
fill="#666">

{current_dates}

</text>


<!-- LONGEST STREAK -->

<text
x="565"
y="110"
text-anchor="middle"
font-size="40"
font-weight="bold"
font-family="Arial"
fill="#111">

{streak["longest"]}

</text>

<text
x="565"
y="160"
text-anchor="middle"
font-size="18"
font-family="Arial"
fill="#333">

Longest Streak

</text>

<text
x="565"
y="198"
text-anchor="middle"
font-size="16"
font-family="Arial"
fill="#666">

{longest_dates}

</text>

</svg>
'''

    with open("streak.svg", "w", encoding="utf-8") as file:

        file.write(svg)


total, days = get_contributions()

streak = calculate_streaks(days)

create_svg(total, streak)

print("Streak SVG created successfully!")
