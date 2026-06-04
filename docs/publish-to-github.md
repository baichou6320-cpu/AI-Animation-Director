# Publish To GitHub

This repository is prepared locally. The recommended GitHub repository name is:

```text
ai-animation-director
```

Recommended full name, based on the current git user config:

```text
baichou6320-cpu/ai-animation-director
```

At the time of preparation, this repository did not exist on GitHub yet.

## 1. Create The Empty GitHub Repository

Create a new GitHub repository:

- Owner: `baichou6320-cpu`
- Repository name: `ai-animation-director`
- Visibility: public is recommended for an open-source Skill.
- Do not initialize with README, license, or `.gitignore`; this local repository already has them.

## 2. Add Remote

After creating the empty repository, run:

```powershell
git remote add origin https://github.com/baichou6320-cpu/ai-animation-director.git
```

If you prefer SSH:

```powershell
git remote add origin git@github.com:baichou6320-cpu/ai-animation-director.git
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

Suggested release title:

```text
v0.1.0 - Prompt-only Skill with experimental Jimeng adapter
```

Suggested release notes:

```markdown
Initial release of AI Animation Director.

- Codex Skill for AI animation pre-production.
- Quick Mode for Jimeng-ready short video execution packages.
- Prompts Only mode for copy-first prompt output.
- Modular prompt pipeline for story, director treatment, character/scene bible, shot list, image prompts, video prompts, routing, and output composition.
- Experimental Jimeng-compatible manifest execution layer.
```

## If Remote Already Exists

If `origin` already exists, inspect it:

```powershell
git remote -v
```

Then update it if needed:

```powershell
git remote set-url origin https://github.com/baichou6320-cpu/ai-animation-director.git
```
