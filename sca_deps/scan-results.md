# Full SCA scan results

Scan run from the repo root (all child paths), 2026-10-03 around 00:12Z to 00:15Z, via the Endor MCP `scan` tool with `quick_scan: false` and scan types `vulnerabilities` and `dependencies`.

## Where the results landed
- Namespace: jose-demo
- Project: https://github.com/jose-endor/python-vuln-app.git (UUID 459aa376-a925-46a3-ade0-888e255a351c)
- Project createTime: 2026-10-03T00:14:18Z, which is during this scan. The project did not exist before this scan, so it was created by it (it is not a pre-existing project with prior history).
- Project state: SCAN_STATE_IDLE, automated scanning disabled (disableAutomatedScan: true), platform source GITHUB.
- Scanned ref: main at commit 8c7255e. sca_deps/ was untracked at scan time, so the GitHub file links on findings (blob/main/sca_deps/...) will not resolve until sca_deps/ is committed and pushed.

## Totals (whole repo, all manifests)
| Severity | Findings |
|---|---|
| Critical | 105 |
| High | 461 |
| Medium | 1174 |
| Low | 462 |
| Total | 2202 |

These totals cover the whole repo, not just sca_deps/. Some top findings are Python code findings (e.g. insecure pickle deserialization, weak PRNG), so the count includes more than npm dependency vulnerabilities.

Top 5 by severity as returned by the tool:
1. Insecure Deserialization in Python's Pickle Library (CRITICAL)
2. Use of cryptographically weak PRNG, python_random_rule-random (CRITICAL)
3. GHSA-f2jv-r9rf-7988, Remote code execution in handlebars when compiling templates (CRITICAL)
4. GHSA-f598-mfpv-gmfx, Sequelize raw attributes with parentheses (CRITICAL)
5. GHSA-jf85-cpcp-j695, Prototype pollution in lodash (CRITICAL)

## Verified detail for one finding (handlebars@4.5.0)
- Finding 80581e66-7870-4110-b93b-bc761491bbc8, stored in jose-demo, context CI_RUN
- callGraphAnalysisType: CALL_GRAPH_ANALYSIS_TYPE_FULL
- Dependency files: sca_deps/package.json, sca_deps/package-lock.json
- Tags: direct dependency, unreachable function, unreachable dependency, fix available
- Summary: "No vulnerable function is known to be reachable." Fixed in 4.7.7, latest 4.7.9.

## Not verified (data gaps)
- Total resolved dependencies vs the 2,974 packages in package-lock.json: not confirmed.
- Whether call-graph generation succeeded for every package, and for other manifests in the repo (requirements.txt, frontend/, partner-packages/): not confirmed. Only the handlebars finding above was inspected.
- Reachability breakdown (reachable / unreachable / potentially reachable) across the 2202 findings: not retrieved.
- The scan tool returned no errors. That is not the same as proof of complete resolution. A read-only troubleshooting pass to confirm resolution and reachability stalled and returned nothing.
