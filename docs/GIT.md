# GitHub connection

`D:\NASA` is a Git working tree connected to:

- Remote name: `origin`
- Remote URL: `https://github.com/77bigsun/nasa.git`
- Local branch: `main`
- Upstream branch: `origin/main`
- Remote content at initial connection: an initial README, commit `d150af2`.

Connecting the repository preserved the local website files and attached main to the existing remote history. The setup did not push files. Later commits and pushes remain the responsibility of the person making them; inspect Git status for the current state.

```powershell
cd D:\NASA
git remote -v
git branch -vv
git status
```

`.gitignore` excludes `.venv`, node_modules, dist, `.env`, temporary files, and logs. Source, lockfiles, demonstration data, documentation, and the NASA texture belong in version control.

After reviewing the file list, commit and push with:

```powershell
git add .
git commit -m "Update Earth Analog Finder"
git push -u origin main
```

Complete GitHub authentication with your own account when requested. If Git requests user.name or user.email, set the identity you want in commit history; setup did not guess or change it.

Use feature branches and pull requests for subsequent work. Services remain in one repository and can be reviewed and assigned by directory. Keep code, documentation, fixtures, and commit descriptions in English.
