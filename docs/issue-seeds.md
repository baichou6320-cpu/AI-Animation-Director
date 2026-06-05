# GitHub Issue Seeds

Use these after publishing the repository. They convert the backlog into copy-ready GitHub issues.

## P0 - Launch

### Issue: Confirm GitHub remote and first Actions run

Labels: `release`, `p0`

Body:

```markdown
## Goal

Confirm the repository is published and CI is running.

## Tasks

- [ ] Create or verify `baichou6320-cpu/AI-Animation-Director`.
- [ ] Push `main`.
- [ ] Confirm `Validate Skill Package` runs on GitHub Actions.
- [ ] Add repository topics from `docs/repository-metadata.md`.

## Acceptance

- `git remote -v` points to the GitHub repository.
- GitHub Actions has a passing validation run.
- Repository description and topics are set.
```

### Issue: Publish v0.1.0

Labels: `release`, `p0`

Body:

```markdown
## Goal

Create the first tagged release.

## Tasks

- [ ] Push tag `v0.1.0`.
- [ ] Use `docs/release-notes-v0.1.0.md` as release notes.
- [ ] Make clear that v0.1.0 is prompt-only with an experimental Jimeng-compatible adapter.

## Acceptance

- GitHub release exists.
- Release notes mention examples, validation, and boundaries.
```

## P1 - Skill Quality

### Issue: Add more final-format examples

Labels: `example`, `p1`

Body:

```markdown
## Goal

Add examples that validate more realistic user requests.

## Examples to add

- [ ] Cyberpunk product ad, 15 seconds, 4 shots, Jimeng.
- [ ] Stop-motion toy short, 20 seconds, 5 shots.
- [ ] Documentary realism, 30 seconds, 4 shots.
- [ ] English prompt output.

## Acceptance

- Each example uses final user-facing output only.
- Jimeng examples include `IMG-REF`, `IMG-Sxx`, and `VID-Sxx`.
- No example includes internal reasoning, `Project Packet`, or handoff notes.
```

### Issue: Strengthen static validation for routing and output rules

Labels: `validation`, `p1`

Body:

```markdown
## Goal

Prevent accidental removal of core routing and copy-first output rules.

## Tasks

- [ ] Check that `SKILL.md` stays under the chosen size threshold.
- [ ] Check that `quick_package_router.md` exists.
- [ ] Check that `output_composer.md` contains `Prompts Only`, `Quick Mode`, and copy-block rules.
- [ ] Check examples for matching `IMG-Sxx` and `VID-Sxx` IDs.

## Acceptance

- Python validator fails when routing or output composition rules are missing.
- GitHub Actions covers the validator on Linux and Windows.
```

### Issue: Document platform support levels

Labels: `platform`, `docs`, `p1`

Body:

```markdown
## Goal

Make platform support boundaries explicit and avoid implying unverified API support.

## Tasks

- [ ] Define support levels: generic prompt, Jimeng quick package, experimental API adapter, unverified.
- [ ] Update README and platform adapter docs.
- [ ] Add contribution rule requiring official docs for platform-specific parameters.

## Acceptance

- README does not imply verified API support where none exists.
- New platform requests have a place to provide official docs or mark assumptions.
```

## P2 - Productization

### Issue: Add export templates for shot tables and manifests

Labels: `enhancement`, `p2`

Body:

```markdown
## Goal

Make generated production plans easier to move into tools.

## Tasks

- [ ] Add Markdown shot table export template.
- [ ] Add JSON production manifest export template.
- [ ] Add CSV shot list export template.
- [ ] Document expected fields.

## Acceptance

- Export schema is documented.
- At least one example includes an exported manifest or table.
```

### Issue: Strengthen Jimeng-compatible execution layer

Labels: `execution`, `p2`

Body:

```markdown
## Goal

Make the experimental execution layer safer and clearer.

## Tasks

- [ ] Separate provider config from generic manifest validation.
- [ ] Add dry-run fixtures that require no network and no credentials.
- [ ] Add clearer retry and failure states.
- [ ] Document live-run provider assumptions.

## Acceptance

- Dry run works without credentials.
- Live run is clearly documented as provider-specific.
```

## P3 - Presentation

### Issue: Add social preview and README demo

Labels: `docs`, `presentation`, `p3`

Body:

```markdown
## Goal

Make the project easy to understand at a glance.

## Tasks

- [ ] Create a social preview showing input idea and `IMG/VID` output blocks.
- [ ] Add a compact before/after section to README.
- [ ] Avoid large screenshots that make the README noisy.

## Acceptance

- GitHub preview communicates the project in one glance.
- README demonstrates the copy-first workflow quickly.
```
