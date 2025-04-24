import os
from datetime import datetime, timezone
from typing import Dict, List

import argparse  # Add argparse for command-line argument parsing
import pandas as pd
from dotenv import load_dotenv
import json
import requests  # Import requests for HTTP requests
from github import Github
from tabulate import tabulate
import plotly.graph_objects as go
from tqdm import tqdm  # Add tqdm for progress bar


load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")
MAIN_BRANCH = os.getenv("MAIN_BRANCH", "main")  # Default to "main" if not specified


def fetch_pull_request_data(filename: str) -> pd.DataFrame:
    """
    Load pull request data from a JSON file.
    """
    with open(filename, "r") as f:
        pr_list = pd.read_csv(filename)

    df = pd.DataFrame(pr_list)
    # Convert datetime columns to pandas datetime
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["updated_at"] = pd.to_datetime(df["updated_at"])
    df["closed_at"] = pd.to_datetime(df["closed_at"])
    df["merged_at"] = pd.to_datetime(df["merged_at"])

    return df



def normalize_column(column):
    return (column - column.min()) / (column.max() - column.min())

def create_radar_chart(df):
    metrics = ['num_labels', 'commits_behind_main', 'time_open_days', 'comments']
    normalized_df = df[metrics].apply(normalize_column)
    averages = normalized_df.mean()

    # Add the total number of pull requests as another dimension
    total_prs = len(df)
    averages['total_prs'] = total_prs / total_prs  # Normalize to 1 (constant value)

    # Add the new dimension to the radar chart
    metrics.append('total_prs')

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=averages,
        theta=metrics,
        fill='toself',
        name='Normalized Averages'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True)
        ),
        title="Radar Chart with Normalized Averages and Total PRs",
        showlegend=True
    )

    return fig

def visualize_pull_requests(pr_df):
    """
    Visualize pull request complexity using an interactive 3D scatter plot.
    X-Axis: "Time Open (Days)"
    Y-Axis: "Number of Changed Files"
    Z-Axis: "Commits Behind Main"
    Each point is labeled with the PR Number and Title.
    """
    # Create the 3D scatter plot
    fig = go.Figure(data=[go.Scatter3d(
        x=pr_df["time_open_days"],
        y=pr_df["changed_files"],
        z=pr_df["commits_behind_main"],
        mode='markers+text',
        marker=dict(
            size=8,
            color=pr_df["lines_changed"],  # Color by lines changed
            colorscale='Viridis',  # Color scale
            opacity=0.8
        ),
        # Use hovertemplate to display detailed information
        hovertemplate=(
            "<b>PR Number:</b> %{text}<br>"
            "<b>Title:</b> %{customdata[0]}<br>"
            "<b>Time Open (Days):</b> %{x}<br>"
            "<b>Changed Files:</b> %{y}<br>"
            "<b>Commits Behind Main:</b> %{z}<br>"
            "<b>Lines Changed:</b> %{marker.color}<br>"
            "<b>Author:</b> %{customdata[1]}<br>"
            "<extra></extra>"  # Removes the default trace info
        ),
        text=pr_df["number"].astype(str),  # PR number
        customdata=pr_df[["title", "user"]].values  # Additional data for hovertemplate
    )])

    # Set axis labels
    fig.update_layout(
        scene=dict(
            xaxis_title="Time Open (Days)",
            yaxis_title="Number of Changed Files",
            zaxis_title="Commits Behind Main"
        ),
        title=f"Pull Request Complexity of {REPO_NAME}",
        margin=dict(l=0, r=0, b=0, t=40)
    )

    # Show the plot
    fig.show()
    fig.write_html("interactive_3d_scatter.html")
    print("Interactive 3D scatter plot saved to interactive_3d_scatter.html")

def create_dataframe(pr_list: List[Dict]) -> pd.DataFrame:
    """
    Create a DataFrame from the list of pull requests.
    """
    # Convert the list of dictionaries to a DataFrame
    pr_df = pd.DataFrame(pr_list)
    # Convert datetime columns to pandas datetime
    pr_df["created_at"] = pd.to_datetime(pr_df["created_at"])
    pr_df["updated_at"] = pd.to_datetime(pr_df["updated_at"])
    pr_df["closed_at"] = pd.to_datetime(pr_df["closed_at"])
    pr_df["merged_at"] = pd.to_datetime(pr_df["merged_at"])

    # Print this out in a table using tabulate
    print( tabulate(pr_df, headers="keys", tablefmt="pipe") )

    return pr_df


def main():
    """
    Read a CSV representing pull requests from a GitHub repository and visualize the complexity of the pull requests.
    The complexity is represented by a radar chart and a 3D scatter plot.
    The radar chart shows the average values of specific columns, while the 3D scatter plot visualizes the relationship between time open, number of changed files, and commits behind main.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Visualize GitHub pull requests.")
    parser.add_argument("--csv", type=str, help="Load CSV file of pull-requests.")
    args = parser.parse_args()

    # Create a DataFrame
    pr_df = fetch_pull_request_data(args.csv)
    # Print some statistics about the pull requests
    print(f"Total pull requests: {len(pr_df)}")
    print(f"Average time open: {pr_df['time_open_days'].mean():.2f} days")
    print(f"Average number of changed files: {pr_df['changed_files'].mean():.2f}")
    print(f"Average commits behind main: {pr_df['commits_behind_main'].mean():.2f}")
    print(f"Average lines changed: {pr_df['lines_changed'].mean():.2f}")
    print(f"Average number of labels: {pr_df['num_labels'].mean():.2f}")
    print(f"Average comments: {pr_df['comments'].mean():.2f}")
    # PR IDs and names and num_labels of those PRs with the least number of labels
    print("Top 10 Pull-Requests with the least number of labels:")
    print(tabulate(
        pr_df.nsmallest(10, 'num_labels')[['number', 'title', 'num_labels']],
        headers="keys",
        tablefmt="pipe"
    ))
    # PR IDs, names and metric that are the furthest behind main
    print("\nTop 10 Pull-Requests that are the furthest behind main:")
    print(tabulate(
        pr_df.nlargest(10, 'commits_behind_main')[['number', 'title', 'commits_behind_main']],
        headers="keys",
        tablefmt="pipe"
    ))
    # Top 10 pull-requests that have the most lines changed
    print(f"\nTop 10 Pull-Requests that have the most lines changed:")
    print(tabulate(
        pr_df.nlargest(10, 'lines_changed')[['number', 'title', 'lines_changed']],
        headers="keys",
        tablefmt="pipe"
    ))
    # Top 10 oldest (most days open) pull-requests
    print(f"\nTop 10 oldest (most days open) Pull-Requests:")
    print(tabulate(
        pr_df.nlargest(10, 'time_open_days')[['number', 'title', 'time_open_days']],
        headers="keys",
        tablefmt="pipe"
    ))

    # Extract the top 10 pull requests based on the least values for the three metrics
    top_prs = pr_df.sort_values(by=['commits_behind_main', 'num_labels', 'lines_changed']).head(20)

    # Print the result as a Markdown table
    print("Top 20 Pull-Requests with the least 'commits_behind_main', 'num_labels', and 'lines_changed':")
    print(tabulate(
        top_prs[['number', 'title', 'commits_behind_main', 'num_labels', 'lines_changed']],
        headers="keys",
        tablefmt="pipe"
    ))


    #fig = create_radar_chart(pr_df)
    #fig.show()

    # Visualize the pull requests
    # visualize_pull_requests(pr_df)

if __name__ == "__main__":
    main()
