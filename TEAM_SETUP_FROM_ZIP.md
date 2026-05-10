# ProcureWise Team Setup From Discord ZIP

Use this guide after downloading the project ZIP from Discord.

## What You Downloaded

This ZIP contains our ISYS 573 AI Agent project, ProcureWise. It is a Track A single AI Agent that reviews purchase requests for procurement and vendor risk.

Team members:

- Jesus Arteaga
- Omar Ferrufino
- Marie Trejo Sandoval

The agent can:

- Read a purchase request.
- Pull useful policy evidence from the knowledge base.
- Check sample vendor risk data.
- Decide the approval path.
- Score the request as low, medium, or high risk.
- Show next steps and an audit-friendly tool trace.

## Step 1: Unzip The Folder

Download the ZIP from Discord and unzip it somewhere easy to find.

Good places:

- Windows: `Documents`
- macOS: `Documents` or `Desktop`

After unzipping, open the folder named something like:

```text
ProcureWise_AI_Agent_Project
```

## Step 2: Check Python

Open Terminal or PowerShell and run:

```text
python --version
```

If that does not work on macOS, run:

```text
python3 --version
```

Python 3.10 or newer is recommended.

## Step 3: Run The Local App

### Windows Option 1: Double Click

Double-click:

```text
start_local_app.bat
```

Keep that window open.

Then open:

```text
http://127.0.0.1:8502
```

### Windows Option 2: PowerShell

From inside the project folder:

```powershell
.\start_local_app.ps1
```

If PowerShell blocks it:

```powershell
powershell -ExecutionPolicy Bypass -File .\start_local_app.ps1
```

Then open:

```text
http://127.0.0.1:8502
```

### macOS

Open Terminal, go into the unzipped project folder, and run:

```zsh
python3 app/basic_server.py
```

You can also run:

```zsh
sh start_local_app.command
```

Keep Terminal open.

Then open:

```text
http://127.0.0.1:8502
```

## Step 4: Test A Sample

Paste this request into the app:

```text
We need to buy a $42,000 annual subscription from CloudDesk AI for the Customer Success team. It will process customer emails and support tickets. Can we approve it this week?
```

Expected result:

- Risk level: Medium
- Approval path: Department VP, Procurement, and Security review
- The app should show policy evidence and next steps.

## Step 5: Run The Checks

Windows:

```powershell
python run_checks.py
```

macOS:

```zsh
python3 run_checks.py
```

Expected output:

```text
All ProcureWise checks passed.
```

## What Still Needs To Be Finished

Before final submission, the team should:

- Add team names and roles to the report.
- Review and polish `docs/final_report.md`.
- Convert the final report to PDF or Word.
- Record the 5-minute demo video using `docs/demo_script.md`.
- Upload the project to GitHub.
- Test the app on at least one Windows computer and one macOS computer.
- Submit the report, GitHub link, video, and deployment instructions.

## Important Note

The app only works while the terminal window is open. If the terminal is closed, the browser will show a connection error. Start the app again and reload the browser page.
