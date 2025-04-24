# repo-analysis
- Extract metadata of pull requests related to a GitHub repo (pointed at by the environment
variable `REPO_NAME` or defined by the command-line `--repo` flag) in the form "`<owner>/<repo>`".
- If `MAIN_BRANCH` is set, it will be used as the main branch to compare against.
Otherwise, the default is `main`.
- You will need to set the environment variable `GITHUB_TOKEN` to your GitHub Personal Access Token (PAT).
- This token should have access to the repository you are trying to analyze.
- The script will fetch all open pull requests, analyze them, and visualize the results.
- The results will be saved to a CSV file if the `--csv <filename>` flag is provided.

If you are in a corporate environment, the script is proxy-aware. Set the environment
variables `HTTP_PROXY` and `HTTPS_PROXY` appropriately and the script will take them
into account.



<div style="text-align: center;">
    <img src="./PR-Analysis.gif" alt="3D Scatter Plot of Pull-Requests">
</div>


## Instructions:
1. **Install the required libraries**:
   ```
   pip install -r requirements.txt
   ```
   Or using an explicit proxy setting like:
   ```
   pip install -r requirements.txt --proxy http://[user:passwd@]proxy.server:port
   ```
2. **Update the `.env` file**:

   Ensure your account/token has the `repo` scope and appropriate access to the repository (eg: it is fine for the repo to be private - as long as your account/token has access to it).
   ```
   GITHUB_TOKEN=your_github_token
   REPO_NAME=owner/repo_name
   MAIN_BRANCH=main  # Replace with the name of your main branch if different
   ```
   **Proxy Servers**: If you have problems with corporate proxy servers, you might add:
   ```
   HTTP_PROXY=http://username:password@proxy.company.com:port
   HTTPS_PROXY=http://username:password@proxy.company.com:port
   ```

3. **Run the script**:
   - For example: `python main.py --repo x/y --branch z --csv pull_requests.csv`
   - The script will save the pull request data from a repo called `y` under GitHub owner `x`to a CSV file named `pull_requests.csv` in the same directory. It will compare how far behind each pull-request is from branch `z`.


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


## Notes:
The script fetches all pull requests (open, closed, and merged) and includes metadata like labels, comments, and file changes.

## Proxy Servers:
If you have problems with corporate proxy servers, you might try (With `set` in Windows, `export` in Linux/Bash):
```
set HTTP_PROXY=http://username:password@proxy.company.com:port
set HTTPS_PROXY=http://username:password@proxy.company.com:port
```
Or use an explict proxy setting like:
```
pip install -r requirements.txt --proxy http://[user:passwd@]proxy.server:port
```
