# Chapter 11 pilot review · Languages, sentences and grammars

Run `python -m http.server 8000 --bind 127.0.0.1 --directory web` from the revision branch and open the [Chapter 11 preview](http://127.0.0.1:8000/?preview=br-11#lesson/br-11/introduction). The eight-page pilot uses device-only progress and XP. Apply the coordination rule with an unfinished input, then combine two complete sentences. Reuse the result and inspect the nested grouping.

## Source receipt

Noel Burton-Roberts, *Analysing Sentences*, third edition, Pearson, 2011, ISBN 9781408233740. The [storyboard](../planning/syntax-foundations-chapter-11-storyboard.md) maps printed pp. 254–268 (PDF pp. 269–283). The coordination diagrams on p. 260 and phrase marker [12] on p. 266 were visually checked. The pilot uses authored examples in two deliberately small grammars.

| Scope | Printed anchors and analysis |
| --- | --- |
| Languages and lists | Pp. 254–259. A complete list determines membership in a fixed, finite toy language. The discussion also acknowledges grammatical variation between speakers. |
| Rules and recursion | Pp. 259–262, p. 260 diagrams. S → S and S formalizes the binary case for the exercise. An earlier S stays intact when reused. The book also illustrates flat coordination. |
| Membership and structure | Pp. 262–265. A grammar specifies permitted sequences and supplies their structural descriptions. Learners use the same toy rule on a new pair and relate that decision to implicit knowledge of grammar. |
| Phrase markers and rules | Pp. 265–268, [11–12]. The word-order contrast applies S → NP VP in a separate toy grammar. Writing a bracketing for the reversed sequence shows grouping, while the rule explains why that order fails in the exercise. |

The version `2.0.0` overlay has five opening and five closing items using existing reviewed catalog source IDs. The pilot uses the existing rule activity with an option to keep the labelled derivation visible. First-time learner timing and independent instructor review are pending. The 9 min 30 sec budget is an estimate. The reviewed catalog and matching immutable assessment seed belong to Phase 5 release preparation.

## Walkthrough

- The browser test verified distinct feedback for missing and unfinished inputs, keyboard operation, and the nested S grouping after reuse. It checked 390 px fit and catalog resume to the transfer page.
- The opening score was 2/5 with no answer review or XP. A 3/5 closing attempt earned 9 XP. A 5/5 retake brought the total to 15 XP.
- The normal Chapter 11 route loaded its published lesson. The preview made no parser requests.

Chapter 10 and all 12 published lesson browser checks passed, along with the lesson and Builder suites, tree-layout checks and filtered static build.

Pilot file hashes:

- `web/content/lessons/br-11-pilot.json` — `47e2663a6034f8c4933b58f9d2d86a91b28bb369f767f45c02b4db72507eaaed`
- `web/js/grammar-pilot.js` — `4eb9964000b51c90eb46caa3399a3e8b00fe3f1df94ba6634f8cc3732eefa666`

Gate 4.11 review precedes the Phase 5 course-wide release checks.
