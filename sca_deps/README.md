# sca_deps

Test fixture for Endor Labs SCA: a 200-package npm manifest (mostly 2018 to 2021 era pinned versions) used to exercise dependency resolution, vulnerability and malware checks, and reachability analysis against this repo.

## Contents
- package.json: 200 direct dependencies, all pinned to exact versions
- package-lock.json: full resolved tree (2,974 packages including transitives)
- dependency-verdicts.md: per-package Endor verdict for all 200 direct dependencies
- scan-results.md: results of the full Endor SCA scan with reachability (added after the scan runs)

node_modules/ is gitignored at the repo root. Regenerate it with `npm install --ignore-scripts --legacy-peer-deps`. Do not run install scripts for this fixture, the manifest intentionally contains old and vulnerable packages.

## How it was built
- 120 packages from an earlier test plus 80 additional ones, versions validated against the npm registry before install. One pin was adjusted (highlight.js 9.15.0 -> 9.15.9, 9.15.0 does not exist).
- Installed 2026-10-03 00:08:53Z to 00:10:40Z with `--ignore-scripts`.
- Each of the 200 direct dependencies was checked with Endor `check_dependency_for_risks` right after install (the 80 new ones on this run, the original 120 on the earlier run, same tool and same namespace).

## Summary of verdicts
| Metric | Count |
|---|---|
| Direct dependencies checked | 200 |
| Tool errors / invalid versions | 0 |
| Malware flagged | 0 |
| Vulnerable | 106 |
| Clean | 94 |
| Advisory IDs (not deduplicated) | 345 |

Most advisories:
- axios@0.21.0: 20 advisories (fix: 0.34.0)
- nodemailer@6.4.0: 17 advisories (fix: 10.0.13)
- xmldom@0.1.27: 17 advisories (fix: none)
- dompurify@2.0.8: 16 advisories (fix: 3.4.16)
- node-forge@0.9.0: 15 advisories (fix: none)
- tar@4.4.0: 15 advisories (fix: 7.5.22)
- angular@1.7.0: 13 advisories (fix: none)
- handlebars@4.5.0: 12 advisories (fix: 4.7.9)
- brace-expansion@1.1.8: 9 advisories (fix: 2.1.7)
- elliptic@6.5.0: 9 advisories (fix: none)

Vulnerable with no fixed version offered (10): xmldom@0.1.27, node-forge@0.9.0, angular@1.7.0, elliptic@6.5.0, showdown@1.9.0, braces@3.0.2, hoek@4.2.0, ip@1.1.5, lodash.set@4.3.2, request@2.88.0

Vulnerable where the only suggested upgrade is a prerelease (6): prismjs@1.17.1, immutable@3.8.2, dot@1.1.2, mongodb@3.5.0, vue@2.6.10, yaml@1.7.0

Known data-quality quirks in the lookup output: some `latest_version` values are odd (minimist reports 0.2.4, react reports an experimental build), and several recommendations point at canary/nightly builds.
