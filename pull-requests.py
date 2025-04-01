from datetime import datetime
import matplotlib.pyplot as plt
from github import Github
import os
import pandas as pd
from dotenv import load_dotenv
from typing import List, Dict
import numpy as np


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

    for pr in pull_requests:
        # Compare the PR branch with the main branch
        comparison = repo.compare(MAIN_BRANCH, pr.head.ref)
        time_open = datetime.utcnow() - pr.created_at  # Time open until now

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
    Visualize pull request complexity using a scatter plot.
    """
    # Scatter plot: Lines changed vs. Time open
    plt.figure(figsize=(10, 6))
    merged = pr_df["is_merged"]
    plt.scatter(
        pr_df["lines_changed"], pr_df["time_open_days"],
        c=merged.map({True: 'green', False: 'red'}),
        alpha=0.6, edgecolors='w', s=pr_df["changed_files"] * 10
    )
    plt.colorbar(label="Merged (Green) vs. Not Merged (Red)")
    plt.xlabel("Lines Changed")
    plt.ylabel("Time Open (Days)")
    plt.title("Pull Request Complexity Analysis")
    plt.grid(True)
    plt.show()

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
    return pr_df

def get_env_variables():
    """
    Fetch GitHub credentials and repository name from environment variables.
    """
    load_dotenv()
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO_NAME = os.getenv("REPO_NAME")
    MAIN_BRANCH = os.getenv("MAIN_BRANCH", "main")  # Default to "main" if not specified

    # Ensure required environment variables are set
    if not GITHUB_TOKEN or not REPO_NAME:
        print("Error: Missing GITHUB_TOKEN or REPO_NAME in .env file.")
        return None, None, None

    return GITHUB_TOKEN, REPO_NAME, MAIN_BRANCH

def main():
    """
    Main function to execute the script.
    """
    # Load environment variables
    GITHUB_TOKEN, REPO_NAME, MAIN_BRANCH = get_env_variables()
    # Ensure required environment variables are set
    if not GITHUB_TOKEN or not REPO_NAME:
        print("Error: Missing GITHUB_TOKEN or REPO_NAME in .env file.")
        return

    # Fetch non-closed pull requests
    pr_list = fetch_pull_requests(REPO_NAME)

    # Create a DataFrame
    pr_df = create_dataframe(pr_list)

    # Save the DataFrame to a CSV file
    pr_df.to_csv("open_pull_requests.csv", index=False)
    print("Open pull requests saved to open_pull_requests.csv")

    # Visualize the pull requests
    visualize_pull_requests(pr_df)