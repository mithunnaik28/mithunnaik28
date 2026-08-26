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

    # First contribution
    first_contribution = None

    for day in days:

        if day["count"] > 0:

            first_contribution = day["date"]

            break

    if first_contribution:

        first_date = first_contribution.strftime("%b %d, %Y")

    else:

        first_date = "-"

    current_dates = (
        f"{format_date(streak['current_start'])} - "
        f"{format_date(streak['current_end'])}"
    )

    longest_dates = (
        f"{format_date(streak['longest_start'])} - "
        f"{format_date(streak['longest_end'])}"
    )


    # =========================
    # SVG
    # =========================

    svg = f'''<svg
xmlns="http://www.w3.org/2000/svg"
width="690"
height="275"
viewBox="0 0 690 275">

<!-- ========================= -->
<!-- Background -->
<!-- ========================= -->

<rect
x="0"
y="0"
width="690"
height="275"
rx="6"
fill="#0d1117"
stroke="#30363d"
stroke-width="1"/>


<!-- ========================= -->
<!-- Vertical Lines -->
<!-- ========================= -->

<line
x1="230"
y1="35"
x2="230"
y2="240"
stroke="#30363d"
stroke-width="1"/>

<line
x1="460"
y1="35"
x2="460"
y2="240"
stroke="#30363d"
stroke-width="1"/>


<!-- ========================= -->
<!-- TOTAL CONTRIBUTIONS -->
<!-- ========================= -->

<text
x="115"
y="112"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="40"
font-weight="700"
fill="#ffffff">

{total}

</text>


<text
x="115"
y="166"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="19"
fill="#e6edf3">

Total Contributions

</text>


<text
x="115"
y="207"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="16"
fill="#8b949e">

{first_date} - Present

</text>


<!-- ========================= -->
<!-- CURRENT STREAK -->
<!-- ========================= -->

<g transform="translate(345,0)">


<!-- Orange Circle -->

<circle
cx="0"
cy="95"
r="57"
fill="none"
stroke="#ff8c00"
stroke-width="7"/>


<!-- Flame -->
<!-- Simple SVG Flame -->

<path
d="
M 0 18
C -4 9 -2 2 5 -7
C 7 0 14 4 13 13
C 12 22 5 27 0 27
C -8 27 -13 22 -13 14
C -13 8 -10 3 -6 -2
C -7 7 -3 12 0 18
Z
"
fill="#ff8c00"
transform="translate(0,-70)"/>


<!-- Current Number -->

<text
x="0"
y="112"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="40"
font-weight="700"
fill="#ffffff">

{streak["current"]}

</text>


<!-- Current Streak -->

<text
x="0"
y="166"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="19"
font-weight="700"
fill="#ff8c00">

Current Streak

</text>


<!-- Current Dates -->

<text
x="0"
y="207"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="16"
fill="#8b949e">

{current_dates}

</text>

</g>


<!-- ========================= -->
<!-- LONGEST STREAK -->
<!-- ========================= -->

<text
x="575"
y="112"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="40"
font-weight="700"
fill="#ffffff">

{streak["longest"]}

</text>


<text
x="575"
y="166"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="19"
fill="#e6edf3">

Longest Streak

</text>


<text
x="575"
y="207"
text-anchor="middle"
font-family="Arial, sans-serif"
font-size="16"
fill="#8b949e">

{longest_dates}

</text>


</svg>
'''


    # =========================
    # Save SVG
    # =========================

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
