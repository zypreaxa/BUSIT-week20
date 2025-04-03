import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patheffects as path_effects
from mplsoccer import Pitch
from collections import Counter

# Load the data
possession_data = pd.read_csv("possession_data_filtered.csv")
possession_data = possession_data[['period_id', 'seconds', 'action_type', 'start_x', 'start_y',
                                   'end_x', 'end_y', 'result', 'possession_group', 'team_id']]

tracking_data = pd.read_csv("tracking_data.csv")

# Define the action type dictionary (unchanged)
action_type_dict = {
    0: "pass", 1: "cross", 2: "throw_in", 3: "freekick_crossed", 4: "freekick_short",
    5: "corner_crossed", 6: "corner_short", 7: "take_on", 8: "foul", 9: "tackle",
    10: "interception", 11: "shot", 12: "shot_penalty", 13: "shot_freekick",
    14: "keeper_save", 15: "keeper_claim", 16: "keeper_punch", 17: "keeper_pick_up",
    18: "clearance", 19: "bad_touch", 20: "non_action", 21: "dribble", 22: "goalkick"
}

# Map numeric codes to readable action names
possession_data['action_name'] = possession_data['action_type'].map(action_type_dict)

# Add possession length
possession_lengths = possession_data.groupby('possession_group').size()
possession_data['possession_length'] = possession_data['possession_group'].map(possession_lengths)

# Retrieve all sequences with at least 10 actions
pattern_length = 10
all_sequences = [(group_id, group) for group_id, group in possession_data.groupby('possession_group') if len(group) >= pattern_length]

print(f"Total amount of sequences with at least {pattern_length} actions: {len(all_sequences)}")

# Function to extract 10-action patterns (unchanged)
def extract_action_patterns(data, pattern_length):
    action_patterns = []
    for group_id, group in data.groupby('possession_group'):
        if len(group) >= pattern_length:
            for i in range(len(group) - pattern_length + 1):
                pattern = tuple(group['action_name'].iloc[i:i+pattern_length].tolist())
                action_patterns.append((pattern, group.iloc[i:i+pattern_length]))
    return action_patterns

# Extract all 10-action patterns with associated data
action_patterns = extract_action_patterns(possession_data, pattern_length=pattern_length)
pattern_counter = Counter(pattern for pattern, _ in action_patterns)

# Retrieve the 10 most common patterns with a representative data set
top_10_patterns = []
for pattern, count in pattern_counter.most_common(10):
    for pat, subset in action_patterns:
        if pat == pattern:
            top_10_patterns.append((pattern, subset, count))
            break

print(f"Total number of unique {pattern_length}-action patterns: {len(pattern_counter)}")
print(f"Total number of {pattern_length}-action patterns: {len(action_patterns)}")
print(f"Top 10 most frequent patterns selected")


# Function to simplify action names for visualization (unchanged)
def simplify_action_name(action_name):
    action_mapping = {
        'pass': 'Pass', 'cross': 'Cross', 'dribble': 'Dribble', 'throw_in': 'Throw-in',
        'corner_crossed': 'Corner', 'corner_short': 'Corner', 'freekick_crossed': 'Free Kick',
        'freekick_short': 'Free Kick', 'take_on': 'Take-on', 'shot': 'Shot',
        'shot_penalty': 'Penalty', 'shot_freekick': 'FK Shot', 'interception': 'Intercept',
        'clearance': 'Clear', 'tackle': 'Tackle', 'bad_touch': 'Poor Touch',
    }
    return action_mapping.get(action_name, action_name.capitalize())

# Function to determine zone name based on coordinates (unchanged)
def get_zone_name(x, y):
    if x < 30:
        prefix = "Def."
    elif x < 70:
        prefix = "Mid."
    else:
        prefix = "Att."
    if y < 22:
        suffix = "Left"
    elif y < 44:
        suffix = "Center"
    else:
        suffix = "Right"
    return f"{prefix} {suffix}"

# Function to create chain diagram for a pattern (unchanged)
def create_chain_diagram(pattern_data, ax, title):
    pattern_data = pattern_data.copy().reset_index(drop=True)
    n_actions = len(pattern_data)
    y_pos = 0.5
    box_height = 0.3
    spacing = 1.0
    action_type_colors = {
        'pass': '#66c2a5', 'cross': '#fc8d62', 'dribble': '#8da0cb', 'shot': '#e78ac3',
        'shot_penalty': '#e78ac3', 'shot_freekick': '#e78ac3', 'take_on': '#a6d854',
        'throw_in': '#ffd92f', 'freekick_crossed': '#b3b3b3', 'freekick_short': '#b3b3b3',
        'corner_crossed': '#e5c494', 'corner_short': '#e5c494', 'interception': '#ffed6f',
        'clearance': '#d9d9d9', 'tackle': '#bc80bd', 'bad_touch': '#d9d9d9',
    }
    prev_box_end = None
    for i, row in pattern_data.iterrows():
        action_name = row['action_name']
        zone = get_zone_name(row['start_x'], row['start_y'])
        result = "✓" if row['result'] == 1 else "✗"
        action_display = simplify_action_name(action_name)
        label = f"{i+1}. {action_display}\n{zone}\n{result}"
        box_color = action_type_colors.get(action_name, '#d9d9d9')
        box_alpha = 1.0 if row['result'] == 1 else 0.6
        box_left = i * spacing
        box_right = box_left + 0.8
        rect = plt.Rectangle((box_left, y_pos - box_height/2), 0.8, box_height, 
                             facecolor=box_color, alpha=box_alpha, edgecolor='black', linewidth=1)
        ax.add_patch(rect)
        ax.text(box_left + 0.4, y_pos, label, ha='center', va='center', fontsize=9, fontweight='bold')
        if prev_box_end is not None:
            ax.arrow(prev_box_end, y_pos, box_left - prev_box_end, 0, 
                     head_width=0.05, head_length=0.05, fc='black', ec='black', length_includes_head=True)
        prev_box_end = box_right
    ax.set_xlim(-0.2, n_actions * spacing + 0.2)
    ax.set_ylim(y_pos - box_height - 0.2, y_pos + box_height + 0.2)
    ax.axis('off')
    ax.set_title(title, fontsize=12, pad=10)

# Create visualizations for the top 10 patterns
for pattern_idx, (pattern, pattern_data, count) in enumerate(top_10_patterns):
    # Create a figure for the chain diagram and multiple pitches
    fig = plt.figure(figsize=(20, 4 + 3 * len(pattern_data)))
    grid = GridSpec(len(pattern_data) + 1, 2, figure=fig, width_ratios=[3, 2], hspace=0.3)

    # Chain-diagram
    chain_ax = fig.add_subplot(grid[0, 0])
    pattern_str = " -> ".join(simplify_action_name(action) for action in pattern)
    success_rate = pattern_data['result'].mean() * 100
    sequence_result = "Goal" if (pattern_data['action_type'].isin([11, 12, 13]) & (pattern_data['result'] == 1)).any() else "No Goal"
    title = f"Pattern {pattern_idx + 1}: {pattern_str}\n{success_rate:.1f}% success, {sequence_result}, Freq: {count}"
    create_chain_diagram(pattern_data, chain_ax, title)

    # Make a pitch for each action in the pattern
    cmap = plt.cm.viridis
    for idx, (_, row) in enumerate(pattern_data.iterrows()):
        pitch_ax = fig.add_subplot(grid[idx + 1, :])  # Gebruik volledige breedte voor pitch
        pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white', stripe=True)
        pitch.draw(ax=pitch_ax)

    action_fig = plt.figure(figsize=(10, 7))  # Adjust the size as needed
    action_ax = action_fig.add_subplot(111)
    # Draw all actions up to the current action
    for j, (_, sub_row) in enumerate(pattern_data.iloc[:idx + 1].iterrows()):
        # Create a new figure just for the individual action (pitch)

        
        # Draw the pitch for the current action
        pitch = Pitch(pitch_type='statsbomb', pitch_color='grass', line_color='white', stripe=True)
        pitch.draw(ax=action_ax)

        # Draw the arrow for the current action
        color = cmap(j / max(1, len(pattern_data) - 1))
        alpha = 0.8 if sub_row['result'] == 1 else 0.4
        pitch.arrows(sub_row['start_x'], sub_row['start_y'], 
                    sub_row['end_x'], sub_row['end_y'],
                    width=2, headwidth=6, headlength=6,
                    color=color, alpha=alpha, ax=action_ax)

        # Add text for the current action
        action_display = simplify_action_name(sub_row['action_name'])
        action_ax.text(sub_row['start_x'], sub_row['start_y'], str(j + 1), 
                    color='white', fontsize=10, fontweight='bold',
                    ha='center', va='center',
                    path_effects=[path_effects.withStroke(linewidth=2, foreground='black')])

        # Add player positions based on the time of the current action
        action_time = sub_row['seconds']
        tracking_subset = tracking_data[tracking_data['timestamp'].astype(str).str.startswith(f"17221824{int(action_time):02d}")]
        if not tracking_subset.empty:
            pitch.scatter(tracking_subset['x'], tracking_subset['y'], s=100, color='blue', alpha=0.5, ax=action_ax, label='Players')
            action_ax.legend(loc='upper right', fontsize=8)

        # Title for this individual action
        action_ax.set_title(f"Action {j + 1}: {action_display} at {action_time}s", fontsize=10)


        # Close the individual figure to free up memory
        plt.close(action_fig)  # Close the figure after saving



        # Add player positions based on time of current action
        action_time = row['seconds']
        tracking_subset = tracking_data[tracking_data['timestamp'].astype(str).str.startswith(f"17221824{int(action_time):02d}")]
        if not tracking_subset.empty:
            pitch.scatter(tracking_subset['x'], tracking_subset['y'], s=100, color='blue', alpha=0.5, ax=pitch_ax, label='Players')
            pitch_ax.legend(loc='upper right', fontsize=8)

        # Title for this pitch
        action_display = simplify_action_name(row['action_name'])
        pitch_ax.set_title(f"Action {idx + 1}: {action_display} at {action_time}s", fontsize=10)

        # Save the current pitch for this action as a separate PNG file
        action_filename = f"pattern_{pattern_idx + 1}_action_{idx + 1}_step_{j + 1}_with_players.png"
        action_fig.savefig(action_filename)  # Save the pitch as a separate PNG


    plt.suptitle(f'Top 10 Pattern {pattern_idx + 1}', fontsize=20, y=0.98)
    plt.savefig(f"pattern_{pattern_idx + 1}_with_players.png")  # Opslaan als PNG
    plt.show()

print("Visualizations of the 10 most common 10-action patterns with player positions have been saved as PNG files.")