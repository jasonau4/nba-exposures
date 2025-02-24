import pandas as pd
from flask import Flask, render_template_string

df = pd.read_csv("lineups.csv") # contest file
positions = ["C", "F", "G", "PF", "PG", "SG", "SF", "UTIL"]
app = Flask(__name__)

def getexposures(username):
    lineups = df.loc[df["EntryName"].str.contains(username, case=False, na=False), "Lineup"]
    lineups = lineups.tolist()
    lineups = [[lineup] for lineup in lineups]

    for i in range(len(lineups)):
        split = lineups[i][0].split()
        indices = []
        temp = []
        for position in positions:
            indices.append(split.index(position))
        indices = sorted(indices)
        temp.append(' '.join(split[1:indices[1]]))
        for j in range(1,7):
            temp.append(' '.join(split[indices[j]+1:indices[j+1]]))
        temp.append(' '.join(split[indices[7]+1:]))
        lineups[i] = temp

    count = {}

    for lineup in lineups:
        for player in lineup:
            if player in count:
                count[player] += 1
            else:
                count[player] = 1
    
    count = dict(sorted(count.items(), key=lambda item: item[1], reverse=True))

    for player in count:
        count[player] /= len(lineups) 
        count[player] = round(count[player]*100, 1)
        count[player] = str(count[player]) + "%"

    exposure = pd.DataFrame(list(count.items()), columns=['Player', 'Exposure'])

    return exposure, len(lineups)

@app.route('/<username>')
def show_exposure(username):
    exposure, _ = getexposures(username)
    table_html = exposure.to_html(classes='table table-striped', index=False)

    # HTML template
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Player Exposure Table for {username}</title>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    </head>
    <body>
        <div class="container">
            <h1 class="mt-5">Player Exposure Table for {username}</h1>
            {table_html}
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/')
def index():
    users = ["AaronCosta", "bpcologna", "F0rsaken", "jsn77", "komendera", "LeVerticalDFS", "moklovin", "papagates", "youdacao"]  # users to scrape
    user_links = ""
    
    for user in users:
        _, lineups = getexposures(user)
        user_links += f'<li><a href="/{user}">{user} ({lineups} lineups)</a></li>'

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Player exposures</title>
    </head>
    <body>
        <h1>Player exposures</h1>
        <p>Click on a username to view exposure data:</p>
        <ul>
            {user_links}
        </ul>
    </body>
    </html>
    """