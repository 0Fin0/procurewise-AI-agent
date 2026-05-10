# GitHub Push Instructions

Use these steps from your own PowerShell or Terminal, not from the Codex sandbox.

## Should You Be Signed In?

Yes. You should be signed into GitHub before pushing.

You can either:

- Sign in through your browser and create the repo on GitHub.com.
- Or sign in with GitHub CLI by running `gh auth login`.

## Recommended: Create Repo On GitHub.com

1. Go to GitHub.com.
2. Click **New repository**.
3. Use a name like:

```text
procurewise-ai-agent
```

4. Choose **Private** unless the professor specifically wants it public.
5. Do not add a README, `.gitignore`, or license on GitHub. This project already has those files.
6. Copy the repo URL GitHub gives you.

## Push From Windows PowerShell

From the project folder:

```powershell
cd "C:\Users\omarf\Documents\SFSU\Spring'26\ISYS573\Group Project"
git status
git add .
git commit -m "Initial ProcureWise agent project"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/procurewise-ai-agent.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username.

## If Git Shows A Safe Directory Warning

Run:

```powershell
git config --global --add safe.directory "C:/Users/omarf/Documents/SFSU/Spring'26/ISYS573/Group Project"
```

Then run the push commands again.

## If GitHub Asks You To Sign In

Follow the browser login prompt. Git for Windows usually opens Git Credential Manager.

## Alternative: GitHub CLI

If GitHub CLI is installed and logged in:

```powershell
gh auth login
gh repo create procurewise-ai-agent --private --source=. --remote=origin --push
```

## Important

The project `.gitignore` excludes the Discord ZIP, runtime logs, generated case files, Python cache folders, and the original assignment PDF. The GitHub repo should contain the source code, docs, launchers, sample data, Docker files, and setup instructions.

