import os
import json
import urllib.request
from datetime import datetime, timedelta


# =========================
# GitHub Username
# =========================

USERNAME = "mithunnaik28"

TOKEN = os.environ["GH_TOKEN"]


# =========================
# GitHub GraphQL Query
# =========================

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


# =========================
# Get GitHub Contributions
# =========================

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
        result = json.loads(
            response.read().decode("utf-8")
        )

    if "errors" in result:
        print(result["errors"])
        raise Exception("GitHub API Error")

    calendar = (
        result["data"]
        ["user"]
        ["contributionsCollection"]
        ["contributionCalendar"]
    )

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


# =========================
# Calculate Streaks
# =========================

def calculate_streaks(days):

    days.sort(key=lambda x: x["date"])

    # -------------------------
    # Current Streak
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

        current_start = days[i]["date"]
        current_end = days[i]["date"]

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
    # Longest Streak
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


# =========================
# Format Date
# =========================

def format_date(date):

    if date is None:
        return "-"

    return date.strftime("%b %d")


# =========================
# CREATE SVG CARD
# =========================

def create_svg(total, days, streak):

    # -------------------------
    # First contribution date
    # -------------------------

    first_contribution = None

    for day in days:
        if day["count"] > 0:
            first_contribution = day["date"]
            break

    if first_contribution:
        first_date = first_contribution.strftime("%b %d, %Y")
    else:
        first_date = "-"


    # -------------------------
    # Dates
    # -------------------------

    current_dates = (
        f"{format_date(streak['current_start'])} - "
        f"{format_date(streak['current_end'])}"
    )

    longest_dates = (
        f"{format_date(streak['longest_start'])} - "
        f"{format_date(streak['longest_end'])}"
    )


    # -------------------------
    # SVG CARD
    # -------------------------

    svg = f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="600"
height="190"
viewBox="0 0 600 190">

<!-- Background -->

<rect
x="0"
y="0"
width="600"
height="190"
rx="7"
fill="#0d1117"
stroke="#30363d"
stroke-width="1"/>


<!-- ========================= -->
<!-- DIVIDER 1 -->
<!-- ========================= -->

<line
x1="200"
y1="25"
x2="200"
y2="165"
stroke="#30363d"
stroke-width="1"/>


<!-- ========================= -->
<!-- DIVIDER 2 -->
<!-- ========================= -->

<line
x1="400"
y1="25"
x2="400"
y2="165"
stroke="#30363d"
stroke-width="1"/>


<!-- ========================= -->
<!-- TOTAL CONTRIBUTIONS -->
<!-- ========================= -->

<text
x="100"
y="76"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="32"
font-weight="700"
fill="#ffffff">

{total}

</text>


<text
x="100"
y="112"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="16"
fill="#e6edf3">

Total Contributions

</text>


<text
x="100"
y="143"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="13"
fill="#8b949e">

{first_date} - Present

</text>


<!-- ========================= -->
<!-- CURRENT STREAK -->
<!-- ========================= -->

<!-- Flame -->

<g transform="translate(0,0) scale(0.7)">
<path
d="
M 300 23
C 295 16 298 9 304 3
C 305 10 312 13 313 20
C 315 28 309 34 302 34
C 295 34 290 30 290 24
C 290 19 293 15 297 11
C 296 17 298 20 300 23
Z
"
fill="#ff8c00"/>
</g>

<!-- Current Number -->

<text
x="300"
y="76"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="32"
font-weight="700"
fill="#ffffff">

{streak["current"]}

</text>


<!-- Current Streak -->

<text
x="300"
y="112"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="16"
font-weight="700"
fill="#ff8c00">

Current Streak

</text>


<!-- Current Dates -->

<text
x="300"
y="143"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="13"
fill="#8b949e">

{current_dates}

</text>


<!-- ========================= -->
<!-- LONGEST STREAK -->
<!-- ========================= -->

<text
x="500"
y="76"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="32"
font-weight="700"
fill="#ffffff">

{streak["longest"]}

</text>


<text
x="500"
y="112"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="16"
fill="#e6edf3">

Longest Streak

</text>


<text
x="500"
y="143"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="13"
fill="#8b949e">

{longest_dates}

</text>


</svg>
'''


    # -------------------------
    # Save SVG
    # -------------------------

    with open(
        "streak.svg",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(svg)

# =========================
# RUN
# =========================

total, days = get_contributions()

streak = calculate_streaks(days)

create_svg(
    total,
    days,
    streak
)

print("Streak SVG created successfully!")
