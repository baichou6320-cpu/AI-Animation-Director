# Publish To GitHub

This repository is prepared locally. The recommended GitHub repository name is:

```text
AI-Animation-Director
```

Recommended full name, based on the current git user config:

```text
baichou6320-cpu/AI-Animation-Director
```

At the time of preparation, this repository did not exist on GitHub yet.

## 1. Create The Empty GitHub Repository

Create a new GitHub repository:

- Owner: `baichou6320-cpu`
- Repository name: `AI-Animation-Director`
- Visibility: public is recommended for an open-source Skill.
- Do not initialize with README, license, or `.gitignore`; this local repository already has them.

Use `docs/repository-metadata.md` for the repository description and topics.

If you have a GitHub token with repository creation permission, you can create the repository from this workspace:

```powershell
$env:GITHUB_TOKEN = "your-token"
powershell -ExecutionPolicy Bypass -File .\scripts\create_github_repo.ps1
```

The script does not store the token and never writes it to project files.

For an organization repository, pass `-Owner your-org -UseOrg`.

## 2. Add Remote

After creating the empty repository, run:

```powershell
git remote add origin https://github.com/baichou6320-cpu/AI-Animation-Director.git
```

If you prefer SSH:

```powershell
git remote add origin git@github.com:baichou6320-cpu/AI-Animation-Director.git
```

Alternatively, use the helper script:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish_to_github.ps1
```

## 3. Push Main

```powershell
git push -u origin main
```

## 4. Confirm GitHub Actions

After the push, open the repository Actions tab and confirm:

```text
Validate Skill Package
```

Expected result:

```text
Skill package validation passed.
```

## 5. Create First Tag

After checking the README, examples, and Actions result:

```powershell
git tag v0.1.0
git push origin v0.1.0
```

Or publish and tag in one command:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\publish_to_github.ps1 -Tag v0.1.0
```

Suggested release title:

```text
v0.1.0 - Prompt-only Skill with experimental Jimeng adapter
```

Suggested release notes:

Use `docs/release-notes-v0.1.0.md`.

## If Remote Already Exists

If `origin` already exists, inspect it:

```powershell
git remote -v
```

Then update it if needed:

```powershell
git remote set-url origin https://github.com/baichou6320-cpu/AI-Animation-Director.git
```
