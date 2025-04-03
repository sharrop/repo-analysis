from datetime import datetime
import matplotlib.pyplot as plt
from github import Github
import os
import pandas as pd
from dotenv import load_dotenv
from typing import List, Dict
import numpy as np
from datetime import timezone
from tabulate import tabulate
import plotly.graph_objects as go


load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("REPO_NAME")
MAIN_BRANCH = os.getenv("MAIN_BRANCH", "main")  # Default to "main" if not specified


def fetch_pull_requests(repo_name):
    """
    Fetch all non-closed pull requests from the specified GitHub repository.
    """
    # Authenticate with GitHub
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(repo_name)

    # Fetch only open pull requests
    pull_requests = repo.get_pulls(state="open")  # Only fetch open PRs
    pr_list = []
    print(f"Fetched {pull_requests.totalCount} pull requests from {repo_name}")

    for pr in pull_requests:
        # Compare the PR branch with the main branch
        comparison = repo.compare(MAIN_BRANCH, pr.head.ref)
        time_open = datetime.now(timezone.utc) - pr.created_at  # Time open until now

        pr_data = {
            "id": pr.id,
            "number": pr.number,
            "title": pr.title,
            "user": pr.user.login,
            "state": pr.state,
            "created_at": pr.created_at,
            "updated_at": pr.updated_at,
            "closed_at": pr.closed_at,
            "merged_at": pr.merged_at,
            "merge_commit_sha": pr.merge_commit_sha,
            "additions": pr.additions,
            "deletions": pr.deletions,
            "changed_files": pr.changed_files,
            "comments": pr.comments,
            "review_comments": pr.review_comments,
            "labels": [label.name for label in pr.labels],
            "commits_behind_main": comparison.behind_by,
            "commits_ahead_main": comparison.ahead_by,
            "lines_changed": pr.additions + pr.deletions,  # Total lines changed
            "time_open_days": time_open.days,  # Time open in days
            "is_merged": pr.merged_at is not None,  # Whether the PR is merged
        }
        pr_list.append(pr_data)

    return pr_list



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
        title="Pull Request Complexity (Interactive 3D)",
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
    Main function to execute the script.
    """
    # Ensure required environment variables are set
    if not GITHUB_TOKEN or not REPO_NAME:
        print("Error: Missing GITHUB_TOKEN or REPO_NAME in .env file.")
        return
    else:
        print("GitHub credentials and repository name loaded successfully.")
        print(f"Repository: {REPO_NAME}")
        print(f"Main Branch: {MAIN_BRANCH}")

    # Fetch non-closed pull requests
    pr_list = fetch_pull_requests(REPO_NAME)

    # Create a DataFrame
    pr_df = create_dataframe(pr_list)

    # Save the DataFrame to a CSV file
    pr_df.to_csv("open_pull_requests.csv", index=False)
    print("Open pull requests saved to open_pull_requests.csv")

    # Visualize the pull requests
    visualize_pull_requests(pr_df)

if __name__ == "__main__":
    main()
