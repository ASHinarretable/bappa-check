# bappa-check — Implementation Plan

> A pre-commit / terminal code checker that runs sanity checks on your staged files and,
> on success, plays an animated ASCII Ganesha with a green **BAPPA APPROVED** badge.
> Ships as a PyPI CLI (`pip install bappa-check`) **and** a `pre-commit` framework hook.

---

## 0. Decisions (assumed defaults — change any before Phase 1)

| Decision | Choice | Why |
|---|---|---|
| Package / CLI name | `bappa-check` (free on PyPI as of 2026-09-14; `bappa`, `bappa-precommit`, `ganesha-check` also free) | Matches the reel CTA `pip install bappa-check` |
| Import name | `bappa_check` | PEP 8 |
| Python | `>=3.9` | Covers every dev machine still in use; `rich` supports it |
| Runtime deps | `rich` only | Animation + colors + panels; zero heavy deps keeps `pip install` instant on camera |
| Build backend | `hatchling` | Simplest modern `pyproject.toml`, no `setup.py` |
| License | MIT | Standard for tools people copy into team repos |
| Layout | `src/` layout | Prevents accidental local-import bugs in tests, PyPI best practice |
| Art | Pure ASCII (no box-drawing / emoji in the figure) | Renders identically on Windows `cmd`, PowerShell, macOS Terminal, VS Code, GitHub Actions logs |
| Checks | Language-agnostic, zero-config | The hook must be useful in a Java/JS/Python repo alike with no setup |
| Repo | New git repo **in this folder** (`git init`) | Current git root is your home dir — must not publish from that |

---

## 1. What "checks the code" means (v1.0 scope)

All checks run on **staged files** by default (`git diff --cached --name-only --diff-filter=ACMR`).
Each check returns `PASS`, `WARN`, or `FAIL`. Any `FAIL` → exit code 1 → commit blocked.
`WARN` never blocks unless `--strict`.

| # | Check | Severity | Detail |
|---|---|---|---|
| 1 | Merge-conflict markers | FAIL | `<<<<<<<`, `=======`, `>>>>>>>` at line start |
| 2 | Secrets | FAIL | Regex set: AWS access keys, private key blocks (`-----BEGIN … PRIVATE KEY-----`), GitHub `ghp_/gho_`, Slack `xox[abp]-`, generic `api_key|secret|password\s*[:=]\s*["'][^"']{8,}` |
| 3 | Large files | FAIL | > 5 MB staged (configurable) |
| 4 | Syntax | FAIL | `.py` via `ast.parse`; `.json` via `json.loads`; `.toml` via `tomllib` (3.11+) / skip; `.yaml` via PyYAML **only if installed** (optional extra) |
| 5 | Debug leftovers | WARN | `pdb.set_trace()`, `breakpoint()`, `debugger;`, `console.log(` in non-test files |
| 6 | Trailing whitespace / missing EOF newline | WARN | Text files only (skip binaries via null-byte sniff) |
| 7 | TODO/FIXME count | INFO | Reported, never blocks |
| 8 | External linter passthrough | WARN | If `ruff` is on PATH and `.py` files are staged → run `ruff check` and surface result. Same for `eslint` if `package.json` exists. Optional, never required |

**Not in v1.0:** running the project's test suite, type checking, formatting. Those are the user's own hooks — bappa-check is the fast, universal "did I do something dumb?" gate.

---

## 2. User experience

### Terminal command
```
bappa-check                 # check staged files (default)
bappa-check --all           # check every tracked file
bappa-check path/ file.py   # check specific paths (this is how pre-commit calls it)
bappa-check --no-anim       # static art, for CI / slow terminals
bappa-check --strict        # WARN counts as FAIL
bappa-check --install-hook  # write .git/hooks/pre-commit in the current repo
bappa-check --uninstall-hook
bappa-check --version
```

### Output on success
1. Header line: `bappa-check v1.0.0 · 7 files staged`
2. Live checklist — each check line flips from `⏳` to green `✔` / yellow `!` / red `✘` as it finishes (rich `Live` + `Table`)
3. **Animation (~1.5 s, 12–16 frames @ ~10 fps):** Ganesha figure fades in, trunk sways left → right, eyes blink once, a ring of `*` sparkles rotates around the head
4. Green badge panel: ` BAPPA APPROVED — Ganpati Bappa Morya!` 
5. Exit 0

### Output on failure
- Same checklist, but findings are printed as `file:line  message` under each failing check
- Static Ganesha with a **red** badge: `✘  BAPPA SAYS: NOT YET` and a one-line hint (`fix the 2 issues above, or run with --strict off`)
- Exit 1

### Environment handling (important for pre-commit + Windows)
- **Not a TTY** (pre-commit framework captures output; CI): skip animation, print the final frame + badge, keep colors via `force_terminal=True` when `PRE_COMMIT=1` or `CI=true`
- **Windows legacy console**: use `rich` (handles ANSI on Win10+); art is ASCII so no codepage issues; badge emoji gated on `sys.stdout.encoding`
- **`--no-anim` / `BAPPA_NO_ANIM=1`**: same as not-a-TTY

---

## 3. Repository structure

```
Bappa check/                        ← this folder, becomes the GitHub repo `bappa-check`
├── src/
│   └── bappa_check/
│       ├── __init__.py             # __version__ (single source of truth, read by hatch)
│       ├── __main__.py             # `python -m bappa_check`
│       ├── cli.py                  # argparse, orchestrates checks → render → exit code
│       ├── art.py                  # Ganesha frames (list[str]) + badge builders
│       ├── animate.py              # rich Live loop, TTY detection, fps control
│       ├── checks/
│       │   ├── __init__.py         # registry: list of Check objects, run_all()
│       │   ├── base.py             # Check dataclass, Finding, Severity enum
│       │   ├── conflict_markers.py
│       │   ├── secrets.py
│       │   ├── large_files.py
│       │   ├── syntax.py
│       │   ├── debug_leftovers.py
│       │   ├── whitespace.py
│       │   └── external.py         # ruff / eslint passthrough
│       ├── git.py                  # staged files, repo root, binary sniff
│       └── hook.py                 # --install-hook / --uninstall-hook
├── tests/
│   ├── conftest.py                 # tmp git repo fixture
│   ├── test_checks_*.py            # one per check
│   ├── test_cli.py                 # exit codes, --no-anim, path args
│   └── test_hook.py
├── demo/
│   ├── demo.tape                   # VHS script → demo.gif for README + reel
│   └── demo.gif
├── .github/workflows/
│   ├── ci.yml                      # pytest on ubuntu/macos/windows × py3.9/3.12; self-check via pre-commit
│   └── publish.yml                 # on tag v* → build → PyPI trusted publishing
├── .pre-commit-hooks.yaml          # exposes hook id `bappa-check`
├── .pre-commit-config.yaml         # dog-fooding: this repo uses its own hook
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
└── .gitignore
```

### Key config files

**`.pre-commit-hooks.yaml`**
```yaml
- id: bappa-check
  name: Bappa Check
  description: Sanity-checks staged files, blesses them with ASCII Ganesha on success
  entry: bappa-check
  language: python
  pass_filenames: true
  verbose: true          # pre-commit hides output of passing hooks unless verbose — we WANT the art shown
  require_serial: true   # one Ganesha, not one per file batch
```

**`pyproject.toml` (essentials)**
```toml
[project]
name = "bappa-check"
dynamic = ["version"]
requires-python = ">=3.9"
dependencies = ["rich>=13"]
[project.optional-dependencies]
yaml = ["pyyaml"]
dev = ["pytest", "pytest-cov", "ruff", "build", "twine"]
[project.scripts]
bappa-check = "bappa_check.cli:main"
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
[tool.hatch.version]
path = "src/bappa_check/__init__.py"
```

**Installed git hook (`--install-hook` writes this)**
```sh
#!/bin/sh
# installed by bappa-check — https://github.com/<user>/bappa-check
exec bappa-check
```
Safety: if a `pre-commit` file already exists and wasn't written by us, refuse and print instructions to add `bappa-check` as a line instead of overwriting.

---

## 4. Phases

Each phase ends in a working, committed state.

### Phase 1 — Scaffold (≈20 min)
- [ ] `git init` in this folder, `.gitignore` (Python + venv + `.pytest_cache` + `dist/`)
- [ ] `pyproject.toml`, `LICENSE`, `README.md` stub, `src/bappa_check/__init__.py` with `__version__ = "0.1.0"`
- [ ] `python -m venv .venv`, `pip install -e ".[dev]"`
- [ ] `bappa-check --version` prints → commit `chore: scaffold package`

### Phase 2 — Art & animation (≈45 min)
- [ ] Draw Ganesha in ASCII, ~22 cols × 16 rows (fits an 80-col terminal with the badge beside/below it)
- [ ] Generate frame variants programmatically from the base frame (trunk offset, eye chars `o`→`-`, sparkle ring positions) rather than hand-drawing 16 frames
- [ ] `animate.play(frames, fps=10)` using `rich.live.Live`; respects TTY / `--no-anim`
- [ ] Green badge (`Panel`, `style="bold white on green"`), red badge variant
- [ ] `python -m bappa_check --demo-art` flag to preview art without running checks (also handy for filming)
- [ ] Verify in: PowerShell, Windows Terminal, Git Bash, VS Code terminal → commit

### Phase 3 — Checks engine (≈1.5 h)
- [ ] `base.py`: `Severity(INFO|WARN|FAIL)`, `Finding(path, line, message)`, `Check(name, run(files) -> list[Finding])`
- [ ] `git.py`: `staged_files()`, `all_tracked_files()`, `repo_root()`, `is_binary(path)`
- [ ] Implement checks 1–7 in the table above, each with its own test file
- [ ] `external.py`: `shutil.which("ruff")` guard, subprocess with timeout, never crash if the tool misbehaves
- [ ] `checks.run_all(files, strict)` → results list + overall pass/fail → commit

### Phase 4 — CLI & hook installer (≈45 min)
- [ ] `cli.py`: argparse, wire checks → live checklist table → animation/badge → exit code
- [ ] `hook.py`: install/uninstall with the "don't clobber a foreign hook" guard; `chmod +x` on POSIX
- [ ] Handle "not a git repo" and "nothing staged" gracefully (print hint, exit 0)
- [ ] `tests/test_cli.py` using `subprocess` against the tmp-repo fixture → commit

### Phase 5 — pre-commit framework integration (≈20 min)
- [ ] `.pre-commit-hooks.yaml` + dog-food `.pre-commit-config.yaml`
- [ ] `pip install pre-commit`, `pre-commit try-repo . bappa-check --verbose --all-files` → confirm art shows
- [ ] Tag `v0.1.0` locally so `rev:` works in the README snippet → commit

### Phase 6 — CI (≈30 min)
- [ ] `ci.yml`: matrix (ubuntu, macos, windows) × (3.9, 3.12); `pytest`, `ruff check`, `python -m build`
- [ ] `publish.yml`: trigger on `push: tags: v*`, build sdist+wheel, publish via **PyPI Trusted Publishing** (no API token in secrets) — needs a one-time "pending publisher" setup on pypi.org that **you** do in the browser
- [ ] Create GitHub repo, push, confirm CI green

### Phase 7 — Publish (≈30 min, part of it is on-camera)
- [ ] Bump to `1.0.0`, `CHANGELOG.md`
- [ ] Dry-run to **TestPyPI** first: `twine upload -r testpypi dist/*`, then `pip install -i https://test.pypi.org/simple/ bappa-check` in a fresh venv
- [ ] `git tag v1.0.0 && git push --tags` → `publish.yml` pushes to PyPI
- [ ] Fresh-venv verification: `pip install bappa-check && bappa-check --demo-art` (this is the shot for the reel)

### Phase 8 — Demo & content (≈45 min)
- [ ] `demo/demo.tape` for [VHS](https://github.com/charmbracelet/vhs): `pip install bappa-check`, `git add .`, `git commit -m "..."` → Ganesha appears. Renders a clean GIF at reel-friendly 1080×1920 or 1200×800 for README
- [ ] README: hero GIF, 3 install paths (pip / `--install-hook` / pre-commit snippet), check list table, FAQ ("how do I skip it? `git commit --no-verify`"), contributing
- [ ] Pinned-comment CTA text ready: *"Want Bappa reviewing your code too? `pip install bappa-check` — repo link in bio"*

---

## 5. Testing strategy

- **Unit** — every check gets positive + negative fixtures (e.g. a file with `AKIA…` key → 1 finding; same file in `tests/` dir → still flagged, secrets never get a pass)
- **Integration** — `conftest.py` builds a real `git init` tmp repo, stages files, runs `bappa-check` via `subprocess`; asserts exit code and that stdout contains `BAPPA APPROVED` / `NOT YET`
- **Animation** — never tested visually in CI; `animate.play` is tested with `no_anim=True` for the frame-count / final-frame contract only
- **Cross-platform** — CI matrix is the real test; Windows path separators and CRLF are the likely bugs (normalize with `pathlib`, open text files with `newline=""`)

---

## 6. Risks & mitigations

| Risk | Mitigation |
|---|---|
| pre-commit hides output of passing hooks | `verbose: true` in `.pre-commit-hooks.yaml`; document that in README |
| Animation makes commits feel slow | Cap at 1.5 s total; auto-skip when not a TTY; `BAPPA_NO_ANIM` env var for people who love it once and hate it forever |
| Secrets regex false positives (e.g. `password = "changeme"` in docs) | Skip `*.md`, `*.example`, `.env.example`; add `# bappa: ignore` inline suppression |
| Windows console garbles art | ASCII-only figure; rich handles ANSI; emoji gated on encoding |
| Name squatting on PyPI before you publish | Do Phase 7 TestPyPI + real PyPI registration early (can publish 0.1.0 as a placeholder right after Phase 1) |
| Hook silently overwrites someone's existing pre-commit hook | Foreign-hook guard in `hook.py` |

---

## 7. Things only you can do (I'll tell you exactly when)

1. Create the empty GitHub repo `bappa-check` (public) and give me the URL / your username for README links
2. Create a PyPI account + configure the Trusted Publisher for `<user>/bappa-check` → workflow `publish.yml` (one-time, in browser)
3. Same on TestPyPI
4. Push the `v1.0.0` tag (on camera, ideally)

---

## 8. Definition of done

- `pip install bappa-check` works in a fresh venv on Windows + macOS + Linux
- `bappa-check --install-hook` blocks a commit containing an AWS key and blesses a clean one with the animation
- The 4-line `.pre-commit-config.yaml` snippet from the README works via `pre-commit run --all-files` and shows the art
- CI green on the 6-cell matrix; README has the GIF
