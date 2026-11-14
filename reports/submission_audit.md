# T02 submission audit

Status: working prototype, **HOLD pending owner review**. No grade or bonus is guaranteed.

| Rubric item | Evidence | Remaining limitation |
|---|---|---|
| E2E (22) | Five logical stages in pipeline; offline runner; prediction, queue, HTML, audit and decision outputs | Classroom demo not observed |
| Gold + metric (18) | Standard evaluator; fixed budget and split; separate controlled-transform labels and protocol | Transform labels are not human usability gold; instructor GT unavailable |
| Baseline vs PoC (18) | Same 60-sample pool, seed and budget; measured JSON/table; ablation | Recall ties at budget ceiling; no demonstrated primary improvement; fixture hidden score unknown |
| Human-in-loop + gate (12) | 20-image contact sheet, per-image recommendations, override/audit tests, stale-review rejection | Owner has not signed decisions; 8 recommendations require escalation |
| Reliability (12) | Manifest checks, tests, offline/GT guards, deterministic outputs, pinned direct dependencies, source hashes | Isolated-install result recorded separately; not tested on another machine |
| Report + Git (10) | Individual report, metric contract, source commits and contribution evidence | Individual submission format needs instructor acceptance if course requires groups |
| Showcase + debate (8) | Five-slide outline and real failure cases | Presentation/debate not performed in this audit |

## Confirmed defects and corrections

- Stale review CSV could apply to a changed queue: now score/action/evidence checked before approval.
- A failed rerun after GO could leave old approval: pipeline now writes HOLD before validating new inputs; regression test covers GO → bad rerun → HOLD.
- Several KEEP suggestions contain visible compression artifacts: captured in `visual_review.md`; scoring thresholds unchanged after inspecting eval images.

## Not claimed

- No hidden-test result, perfect accuracy, legal-compliance certification, human sign-off, deadline bonus or debate bonus.
- Synthetic input labels generated in the internal benchmark describe applied corruptions, not instructor answers.

## Owner steps before claiming full completion

1. Open contact sheet; confirm clear cases and resolve escalated image-usefulness judgments.
2. Export reviewed CSV into `out/poc/review_queue_reviewed.csv`; run `make run TRACK=t02`.
3. Copy final evidence into report using the report script and review its status statements before submission.
4. Submit the repository/report link in LMS yourself; instructor controls hidden evaluation and exact deadline.
