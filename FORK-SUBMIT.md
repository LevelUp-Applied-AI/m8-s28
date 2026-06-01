# Module 8 Thursday Stretch (Honors) — Fork-and-Submit Flow

All Module 8 assignments use a fork-and-submit flow instead of GitHub
Classroom. GitHub is sunsetting Classroom (full transition 2026-08-28),
and the M8 drill pilot validated this replacement on 2026-05-31.

## 5 steps

1. **Fork this repo** (button top-right) → owner = your personal GitHub
   account → Create fork.
2. **Enable Actions on your fork.** Actions tab → click *"I understand my
   workflows, go ahead and enable them"*. One-time per fork; the autograder
   cannot run on your PR until this is done.
3. **Clone your fork** (not this repo): `git clone https://github.com/<you>/m8-s28.git`
4. **Branch, implement, commit, push:**
   ```bash
   git checkout -b stretch-cross-encoder-rerank
   # edit the stretch files (see the Thursday Stretch page for the deliverables)
   git add .
   git commit -m "Stretch (Thu): cross-encoder re-ranking"
   git push origin stretch-cross-encoder-rerank
   ```
5. **Open a PR *within your fork*** — base `main`, compare `stretch-cross-encoder-rerank`,
   **base repository = your fork** (GitHub defaults to upstream — change it).
   When CI passes, paste the PR URL into TalentLMS → Module 8 → Thursday Stretch.

## Common failure modes

- **PR opened against upstream `LevelUp-Applied-AI/m8-s28` instead of your fork.**
  GitHub disables Actions secrets and downgrades the workflow token for
  cross-fork PRs, and TAs will see your work in a flood of cross-cohort
  PRs to the template. Always change the base-repository dropdown to your
  own fork.
- **Actions disabled on the fork.** No green or red CI check on the PR.
  Re-do Setup step 2, then push an empty commit to retrigger:
  `git commit --allow-empty -m "ci: trigger" && git push`.
- **Forgot to start Weaviate locally before running `pytest tests/ -v`.**
  Local tests fail but CI is fine — the autograder workflow brings up its
  own Weaviate service container.
