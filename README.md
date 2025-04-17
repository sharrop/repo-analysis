# repo-analysis
Python Script to analyze pull-requests in a GitHub repo: Pulling PR metadata into a Dataframe
and visualize them in the hope of deriving a ranking system for "which one to deal with next"

<div style="text-align: center;">
    <img src="./PR-Analysis.gif" alt="3D Scatter Plot of Pull-Requests">
</div>


Instructions:
Install the required libraries:
```
pip install -r requirements.txt
```
Update `.env` File:
```
GITHUB_TOKEN=your_github_token
REPO_NAME=owner/repo_name
MAIN_BRANCH=main  # Replace with the name of your main branch if different
```

Run the script:

The script will save the pull request data to a CSV file named pull_requests.csv in the same directory.


This performs a complexity analysis of pull requests and prioritizes them:

## Additional Metrics:
- **Lines of Code Changed**:
Sum of additions and deletions (additions + deletions).
Larger changes may indicate higher complexity.
Number of Changed Files:

- **Number of Comments**:
Sum of comments and review_comments.
More comments may indicate more discussion or contention.
Time Open:

- Calculate the **duration between created_at and closed_at** (or the current date if still open). Longer durations may indicate complexity or delays.

- Merge Status:
Whether the pull request is merged (merged_at is not None).
Labels:

- **Analyze labels** (e.g., "bug", "enhancement", "critical") to prioritize based on importance.

- **Commits Behind/Ahead Main**:
Already included in the previous script. Larger numbers may indicate more divergence from the main branch.

- **Author Activity**:
Number of pull requests created by the author (to identify experienced contributors).


Notes:
Ensure your account/token has the repo scope if the repository is private.
The script fetches all pull requests (open, closed, and merged) and includes metadata like labels, comments, and file changes.

## Proxy Servers:
If you have problems with corporate proxy servers, you might try (With `set` in Windows, `export` in Linux/Bash):
```
set HTTP_PROXY=http://username:password@proxy.company.com:port
set HTTPS_PROXY=http://username:password@proxy.company.com:port
```
Or use an explict proxy setting like:
```
pip install -r requirements.txt -- 
```
