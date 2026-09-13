# GitHub collaboration

## Repository owner setup

1. Create a public repository named `resilichain-ai` without a generated README, license, or `.gitignore`.
2. Push the existing `main` branch from this project.
3. Open **Settings → Collaborators → Add people** and invite each teammate by their exact GitHub username.
4. Keep `main` stable; use pull requests for feature work.

## Teammate workflow

```bash
git clone https://github.com/Akarsh-42/resilichain-ai.git
cd resilichain-ai
git switch -c feature/short-description

# make and test changes
git add .
git commit -m "Describe the implemented change"
git push -u origin feature/short-description
```

Open a pull request into `main`, have another member review it, and merge only after CI passes.

## Suggested ownership

| Workstream | Suggested branch prefix |
| --- | --- |
| Agents and orchestration | `agents/` |
| Digital twin and API | `backend/` |
| Optimization and evaluation | `optimization/` |
| Frontend and deployment | `frontend/` |

Every teammate should make genuine commits from an email connected to their GitHub account. Never
share one account, fabricate contribution history, or commit API keys and credentials.
