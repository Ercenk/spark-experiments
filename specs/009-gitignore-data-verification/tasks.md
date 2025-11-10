# Tasks: Ensure Generated Data is Not Committed to Git

**Purpose**: Verify and improve .gitignore configuration to ensure generated data under `data/` directory is never committed to the git repository while maintaining directory structure.

**Context**: The `data/` directory contains generated output from Docker containers (companies.jsonl, events, manifests, logs). This data should never be version controlled. The .gitignore currently has `data/*` but the .gitkeep files mentioned in exceptions don't exist.

## Current State Analysis

✅ **Already Working**: 
- `.gitignore` line 55-57 correctly excludes `data/*`
- No files in `data/` are currently tracked or untracked in git
- Generated data is successfully being ignored

⚠️ **Missing**:
- `.gitkeep` files referenced in .gitignore exceptions don't exist
- Could cause issues if data directory is deleted and needs to be recreated

## Phase 1: Verification and Improvement

- [ ] T001 Verify current .gitignore excludes data/* correctly (already confirmed ✅)
- [ ] T002 Check if any data files are currently tracked in git repository (already confirmed none ✅)
- [ ] T003 [P] Create data/.gitkeep file to preserve directory structure in git
- [ ] T004 [P] Create data/manifests/.gitkeep file to preserve manifests subdirectory
- [ ] T005 [P] Create data/raw/.gitkeep file to preserve raw subdirectory
- [ ] T006 [P] Create data/processed/.gitkeep file to preserve processed subdirectory
- [ ] T007 [P] Create data/staged/.gitkeep file to preserve staged subdirectory
- [ ] T008 Stage and commit all .gitkeep files to git
- [ ] T009 Verify .gitkeep files are tracked but data files remain ignored
- [ ] T010 Test by creating a dummy file in data/raw/ and verify it's ignored by git
- [ ] T011 Document data directory structure in README.md or appropriate documentation

## Phase 2: CI/CD Safety (Optional Enhancement)

- [ ] T012 Add pre-commit hook to warn if files under data/ (except .gitkeep) are staged
- [ ] T013 Add CI check to fail if data files are accidentally committed
- [ ] T014 Document .gitignore pattern for team in contributing guide

## Execution Order

1. T001-T002 (verification) ✅ **COMPLETE**
2. T003-T007 can run in parallel (create .gitkeep files in different directories)
3. T008-T009 (commit and verify)
4. T010-T011 (test and document)
5. T012-T014 optional (CI/CD safety measures)

## Validation Checklist

After completion:
- [ ] `data/.gitkeep` exists and is tracked in git
- [ ] `data/manifests/.gitkeep` exists and is tracked in git
- [ ] `data/raw/.gitkeep` exists and is tracked in git
- [ ] `data/processed/.gitkeep` exists and is tracked in git
- [ ] `data/staged/.gitkeep` exists and is tracked in git
- [ ] All .gitkeep files are committed to git
- [ ] Generated data files (*.jsonl, events/*, logs/*) remain ignored
- [ ] `git status` shows no untracked files in data/ except new .gitkeep files
- [ ] Test dummy file in data/raw/ is correctly ignored
