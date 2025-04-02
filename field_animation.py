import dotenv
from matplotlib import animation
from matplotlib import pyplot as plt
import numpy as np
import os
import pandas as pd

from mplsoccer import Pitch

# Loading tracking data from DB

dotenv.load_dotenv()

## Those parameters are stored in the .env file.
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_USER = os.getenv("PG_USER")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")
PG_DATABASE = os.getenv("PG_DB")

## Database connection parameters
import psycopg2
import os

conn = psycopg2.connect(
    host=PG_HOST,
    database=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD,
    port=PG_PORT,
    sslmode="require",
)

## Query to fetch tracking data
query = """
    SELECT pt.frame_id, pt.timestamp, pt.player_id, pt.x, pt.y, p.jersey_number, p.player_name, p.team_id
    FROM player_tracking pt
    JOIN players p ON pt.player_id = p.player_id
    JOIN teams t ON p.team_id = t.team_id
    WHERE pt.game_id = '5uts2s7fl98clqz8uymaazehg';
"""

## Store the received data in a DF
print("Querying the database. This may take a while...")
tracking_df = pd.read_sql_query(query, conn)
print(f"Received dataframe:\n{tracking_df.head()}\n")

## Splitting the data
home_team_id = "8y3iucyxguipljcmf87a11bk9"
away_team_id = "4dtif7outbuivua8umbwegoo5"
ball_team_id = "1oyb7oym5nwzny8vxf03szd2h"

df_home = tracking_df[tracking_df['team_id'] == home_team_id]
df_away = tracking_df[tracking_df['team_id'] == away_team_id]
df_ball = tracking_df[tracking_df['team_id'] == ball_team_id]

# Print the first few rows to verify
print(f"Home team data:\n{df_home.head()}")
print(f"Away team data:\n{df_away.head()}")
print(f"Ball team data:\n{df_ball.head()}\n")

print(len(df_ball), len(df_home), len(df_away))

# ANIMATION
## Figure and axis setup.
pitch = Pitch(pitch_type='opta', goal_type='line', pitch_color='grass',
                pitch_width=68, pitch_length=105)
fig, ax = pitch.draw(figsize=(16, 10.4))

## Plot markers setup.
marker_kwargs = {'marker': 'o', 'markeredgecolor': 'black', 'linestyle': 'None'}
ball, = ax.plot([], [], ms=10, markerfacecolor='#ffce00', zorder=3, **marker_kwargs) # yellow
away, = ax.plot([], [], ms=10, markerfacecolor='#ff0000', **marker_kwargs)  # red
home, = ax.plot([], [], ms=10, markerfacecolor='#008cff', **marker_kwargs)  # blue

##  Animation function.
    # Add player names above the markers for both home and away players

text_objects = []
def animate(i):
    """ Function to animate the data. Each frame it sets the data for the players and the ball."""
    print(text_objects)
    for text in text_objects:
        print(text)
        text.remove()  # Remove the old text objects
    text_objects.clear()  # Clear the list to prepare for new text objects
    timestamp = df_ball.iloc[i, 1]
    # set the ball data with the x and y positions for the ith frame
    ball.set_data(df_ball.iloc[i, [3]], df_ball.iloc[i, [4]])
    # get the frame id for the ith frame
    frame = df_ball.iloc[i, 0]
    # set the player data using the frame id
    ## Loop through the 'away' team to plot each player's position and add their name

    # Collect x and y coordinates for all players at the current frame
    away_x = df_away.loc[df_away.frame_id == frame, 'x'].values
    away_y = df_away.loc[df_away.frame_id == frame, 'y'].values
    home_x = df_home.loc[df_home.frame_id == frame, 'x'].values
    home_y = df_home.loc[df_home.frame_id == frame, 'y'].values

    # Set the data for the away and home players using the sequences of x and y coordinates
    away.set_data(away_x, away_y)
    home.set_data(home_x, home_y)
    for _, row in df_away[df_away.frame_id == frame].iterrows():
        x = row['x']
        y = row['y']
        player_name = row['player_name']
        text = ax.text(x, y + 2, player_name, fontsize=8, ha='center', va='bottom', color='black')  # Add player name above the marker
        text_objects.append(text)  # Keep track of the text object
    ## Loop through the 'home' team to plot each player's position and add their name
    for _, row in df_home[df_home.frame_id == frame].iterrows():
        x = row['x']
        y = row['y']
        player_name = row['player_name']

        text = ax.text(x, y + 2, player_name, fontsize=8, ha='center', va='bottom', color='black')  # Add player name above the marker
        text_objects.append(text)  # Keep track of the text object
    
    ax.set_title(f'Player Positions at Event Timestamp: {timestamp}', fontsize=16)
    return ball, away, home

# Animation function call.
anim = animation.FuncAnimation(fig, animate, frames=len(df_ball), interval=500, blit=False)
plt.show()