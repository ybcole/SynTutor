# SynTutor verified Chapter 5 evidence

The native thesis was updated in its Revised - Final ver tab. Section 5.1, related Section 4.4.5 methods, the technical findings summary, and the technical conclusions now use this evidence. Student and professional results were preserved.

The PDF supplies the replacement technical section. The Markdown report is the reconciled technical report. The figures correspond to Figures 5.5–5.7 in the thesis. The evidence directory contains the actual execution records and source manifest.

Production base: 5f582552504fb2d584fa02f4dfa55f1a704e3be1
Evaluation commit: dbfa208341c99cb4fa522736a01ded20d41d7aa6
Successful workflow: https://github.com/ybcole/SynTutor/actions/runs/44694848877
Code and scoring tests: https://github.com/ybcole/SynTutor/pull/176

Verification covered 476 initial sentence records, 320 additional sentence-disjoint validation records, 216 textbook reference inputs, 120 full API explanation audits, and an additional 60-input explanation audit. The original 74 metric/integrity checks and expanded source, split, tree-subset, and raw-record checks passed. Three model-free scoring regression tests passed. Production modules and reference datasets were unchanged.

BLiMP sample B (240 inputs): strict rules accuracy 65.00%, F1 57.14%; hybrid flagging accuracy 83.75%, F1 85.06%. Hybrid flagging includes unverified verdicts. JFLEG binary labels are source/reference proxies and its results are secondary. CoLA is separated from the primary result because the hybrid model was fine-tuned on CoLA.

Tree scoring: 103/216 normalized; 94 yield-aligned; full labeled F1 70.46%, triangle-aware labeled F1 90.10%, on aligned outputs. Triangle-aware exact matches 59/216 overall. The fixed reference-only non-triangle subset contains 83 inputs.

XAI checks are automated consistency and delivery checks. Nonempty surface-token membership passed for 33/41 error-bearing sentences (80.49%). Two inspected root questions received subordinate-clause wording, and 37 repeated prose occurrences were observed. The human worksheet has 59 cases and no completed ratings. No human accuracy or clarity scores were invented.

These results supersede the supplied provisional 100% technical presentation and the supplied post-remediation figures whose production changes could not be matched to the committed repository. Both external samples had been examined before this reproducibility run. A hash match and sentence disjointness do not establish historical untouched status.

The case-record JSON preserves the predicted and reference structures used for the tree scores and the per-case explanation audit records. The manifest hashes refer to the uncompressed evidence files. The frozen file retains its supplied filename for traceability; the report deliberately calls it a previously examined validation sample.
