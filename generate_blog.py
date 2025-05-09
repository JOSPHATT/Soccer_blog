import pandas as pd
from datetime import datetime

def fetch_and_process_data(csv_url):
    """
    Fetches match data from the given CSV URL, processes it, and returns team-level summary statistics.

    Parameters:
        csv_url (str): URL of the CSV file containing match data.

    Returns:
        team_summary (pd.DataFrame): Team-level summary statistics.
        findings (list): Interesting findings from the data.
    """
    print(f"Fetching match data from: {csv_url}")
    df = pd.read_csv(csv_url)

    # Remove columns with missing values for all entries
    df = df.dropna(axis=1, how='all')

    # Create team-centric view from both HOME and AWAY data
    home_df = df[['Date', 'HOME', 'H_GOALS', 'A_GOALS']].copy()
    home_df.columns = ['Date', 'TEAM', 'GOALS_FOR', 'GOALS_AGAINST']
    home_df['RESULT'] = home_df['GOALS_FOR'] - home_df['GOALS_AGAINST']

    away_df = df[['Date', 'AWAY', 'A_GOALS', 'H_GOALS']].copy()
    away_df.columns = ['Date', 'TEAM', 'GOALS_FOR', 'GOALS_AGAINST']
    away_df['RESULT'] = away_df['GOALS_FOR'] - away_df['GOALS_AGAINST']

    # Combine both views into one
    all_matches = pd.concat([home_df, away_df], ignore_index=True)

    # Compute outcome categories
    all_matches['IS_WIN'] = (all_matches['RESULT'] > 0).astype(int)
    all_matches['IS_DRAW'] = (all_matches['RESULT'] == 0).astype(int)
    all_matches['IS_LOSS'] = (all_matches['RESULT'] < 0).astype(int)

    # Group by team and summarize
    team_summary = all_matches.groupby('TEAM').agg(
        matches_played=('Date', 'count'),
        total_goals_for=('GOALS_FOR', 'sum'),
        total_goals_against=('GOALS_AGAINST', 'sum'),
        total_wins=('IS_WIN', 'sum'),
    ).reset_index()

    # Add derived features
    team_summary['win_rate'] = (team_summary['total_wins'] / team_summary['matches_played']).round(2)

    # Generate findings
    findings = []
    top_team = team_summary.sort_values('win_rate', ascending=False).iloc[0]
    findings.append(f"The team with the highest win rate is {top_team['TEAM']} with a win rate of {top_team['win_rate']:.2f}.")
    
    return team_summary, findings

def generate_html(team_summary, findings, output_path):
    """
    Generates an HTML blog page with the given data.

    Parameters:
        team_summary (pd.DataFrame): Team-level summary statistics.
        findings (list): Interesting findings from the data.
        output_path (str): Path to save the generated HTML file.
    """
    # Create table rows for team summary
    team_summary_rows = ""
    for _, row in team_summary.iterrows():
        team_summary_rows += f"""
        <tr>
            <td>{row['TEAM']}</td>
            <td>{row['matches_played']}</td>
            <td>{row['total_goals_for']}</td>
            <td>{row['total_goals_against']}</td>
            <td>{row['total_wins']}</td>
            <td>{row['win_rate']:.2f}</td>
        </tr>
        """

    # Create list items for findings
    interesting_findings = ""
    for finding in findings:
        interesting_findings += f"<li>{finding}</li>"

    # Read the HTML template
    with open("index.html", "r") as template_file:
        html_content = template_file.read()

    # Replace placeholders with actual data
    html_content = html_content.replace("{{last_updated}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    html_content = html_content.replace("{{team_summary_rows}}", team_summary_rows)
    html_content = html_content.replace("{{interesting_findings}}", interesting_findings)

    # Write the updated content to the output path
    with open(output_path, "w") as output_file:
        output_file.write(html_content)

    print(f"Blog updated: {output_path}")

# Configuration
CSV_URL = "https://raw.githubusercontent.com/JOSPHATT/Finished_Matches/refs/heads/main/Finished_matches.csv"
OUTPUT_PATH = "index.html"

# Fetch data, process it, and generate the blog
team_summary, findings = fetch_and_process_data(CSV_URL)
generate_html(team_summary, findings, OUTPUT_PATH)