---
name: defihacklabs-pr
description: Export a completed tx2poc case into a user-controlled local DeFiHackLabs fork using the repo-native DeFiHackLabs workflow. Use when the user asks to publish, export, submit, or create a DeFiHackLabs PR from a generated tx2poc case, including copying the PoC, running add_new_entry.py, testing with Forge, pushing a branch, and opening a draft PR.
---

# DeFiHackLabs PR

Use this skill only after `tx2poc` has generated a case and the PoC exists. The user should provide the case path, usually `cases/<case>`. Read `AGENTS.md` in the TxAnalyzer repo for the local DeFiHackLabs fork path and PR defaults.

## Core Command

After copying the final PoC into the local DeFiHackLabs fork under `src/test/YYYY-MM/`, run the DeFiHackLabs helper from inside that fork:

```bash
python add_new_entry.py
```

Use this command as the source of truth for README entry creation. It discovers untracked Solidity files under `src/test/`, asks for incident metadata, writes the README entry, and prints the Forge command expected by DeFiHackLabs.

## PR Format

Use one branch per DeFiHackLabs PR. Do not reuse a branch from another exported case.

Use this PR title format:

```text
Add <Name> PoC. <Mon D>. <Lost Amount>
```

Example:

```text
Add TokenHolder PoC. Oct 7. 20 WBNB
```

Use this PR body/message format:

```text
ref: {source: <tweet-or-source-link>}
```

## Workflow

1. Inspect the case path and identify the PoC.
   - Require `metadata.json`, `block.json`, `attack_analysis.md`, and a passing `poc_run.log` or equivalent final verification.
   - If more than one `*_exp.sol` exists, ask the user which PoC to export.
   - Do not inspect a same-transaction DeFiHackLabs sample before the generated PoC exists.

2. Validate the local DeFiHackLabs fork before changing it.

   ```bash
   cd DeFiHackLabs
   git status --short
   git remote -v
   ```

   Require a clean worktree, `origin` as the user's fork, and `upstream` as `SunWeb3Sec/DeFiHackLabs`.

3. Sync the local fork to the latest DeFiHackLabs upstream before duplicate checks.

   ```bash
   git fetch upstream
   git switch main
   git merge --ff-only upstream/main
   ```

   Push `main` to `origin` only when the user wants their fork's main branch updated:

   ```bash
   git push origin main
   ```

4. Check the freshly synced DeFiHackLabs fork for the attack transaction.

   ```bash
   rg -ni "<attack_tx_hash>" . --glob '!.git/**'
   ```

   Stop immediately if the same attack transaction already appears. Do not create a branch, copy files, or open a PR for an existing transaction.

5. Re-check PoC quality before copying.

   Inspect the final tx2poc PoC for TODO/FIXME placeholders, compile-only tests, raw transaction replay, and trace-frame comments. Do not export until the PoC is a self-contained explanatory exploit test that already passed in the tx2poc case.

6. Create a new branch for this PR and copy only the final PoC.

   Derive `YYYY-MM` from the attack timestamp in `block.json`, and use the same timestamp when `add_new_entry.py` asks for the incident timestamp. Before copying, verify the target path does not exist and the PoC basename is not already present in `README.md` or `src/test/`; if it collides, choose a unique PoC filename before running the helper.

   ```bash
   git switch -c tx2poc/<case-or-victim>
   mkdir -p src/test/YYYY-MM
   test ! -e src/test/YYYY-MM/<poc_name>_exp.sol
   rg -ni "<poc_name>_exp.sol" README.md src/test
   ```

   Treat any `rg` output as a collision and stop to choose a unique PoC filename. If the preflight is clean, copy the PoC:

   ```bash
   cp ../cases/<case>/<poc_name>_exp.sol src/test/YYYY-MM/<poc_name>_exp.sol
   ```

7. Run the DeFiHackLabs helper.

   ```bash
   python add_new_entry.py
   ```

   Select the matching network, answer `no` for manually adding a new incident, then answer `yes` to process `.sol` files missing README entries. For the copied PoC, provide the attack timestamp, lost amount from the PoC header, concise details/root cause, and a relevant link reference.

   The existing-file path in `add_new_entry.py` may not preserve the selected network in the generated README command. After it updates `README.md`, manually verify the entry's Forge command against the case chain. Add required network-specific flags, especially `--evm-version shanghai` for Base, optimism, or bsc when DeFiHackLabs expects it.

8. Test, commit, push, and open a draft PR.

   Set the PR title and body using the format above. Use the same title for the commit message. Derive `<owner>` from the `origin` fork URL, not from `upstream`.

   ```bash
   forge test --contracts ./src/test/YYYY-MM/<poc_name>_exp.sol -vvv
   git add src/test/YYYY-MM/<poc_name>_exp.sol README.md
   git commit -m "Add <Name> PoC. <Mon D>. <Lost Amount>"
   git push origin tx2poc/<case-or-victim>
   git remote get-url origin
   gh pr create --repo SunWeb3Sec/DeFiHackLabs --base main --head <owner>:tx2poc/<case-or-victim> --title "Add <Name> PoC. <Mon D>. <Lost Amount>" --body "ref: {source: <tweet-or-source-link>}" --draft
   ```

   Prefer the verified README Forge command if it differs.

## Guardrails

- Treat `DeFiHackLabs/` as a gitignored local clone of the user's fork, not as a TxAnalyzer submodule.
- Require the DeFiHackLabs repo to be clean before applying changes.
- Require `origin` to be the user's fork and `upstream` to point to `SunWeb3Sec/DeFiHackLabs`.
- Sync `base_branch` from `upstream` with fast-forward only before checking for duplicate transactions or creating the export branch.
- Use a separate branch for each DeFiHackLabs PR.
- After syncing latest upstream, stop if the attack transaction hash already appears in DeFiHackLabs.
- Use the attack timestamp from `block.json` for both the `src/test/YYYY-MM/` folder and the timestamp entered into `add_new_entry.py`.
- Do not overwrite existing DeFiHackLabs PoCs or reuse an existing PoC basename.
- Do not export PoCs with TODO/FIXME placeholders, compile-only tests, raw replay, or trace-frame comments.
- Copy only the final Solidity PoC into DeFiHackLabs. Do not copy tx2poc trace JSON, benchmark output, notes, or reviews.
- Create draft PRs by default.
