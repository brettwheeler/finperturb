# AI contribution disclosure — manuscript text

Two versions: the full statement for the methods or acknowledgments section
(wherever the venue's policy places AI-use declarations), and a short form for
submission-system declaration fields. Check the target venue's policy for
placement before submitting; the substance below is compatible with COPE and
the major publishers' positions (AI may not be an author; AI use must be
disclosed; the human author bears full accountability).

## Full statement

> **Disclosure of AI contribution.** This study was produced as a human–AI
> collaboration whose division of labor the author prefers to state rather than
> leave to be inferred. Claude (Anthropic; Opus- and Fable-class large
> language models)
> wrote the majority of the analysis code and documentation and made
> substantive methodological contributions: candidate analytic approaches —
> including elements of the pre-registered scoring rules and the treatment of
> decoding stochasticity — typically originated with the model. So did much
> of the work's rigor: the exhaustive elaboration of each analysis — edge
> cases, counter-checks, the test suite, the audit trail — is largely the
> model's work, produced at the author's direction. The author's role was
> direction and ratification: framing the research question,
> requiring the rationale for each proposed method, checking it against
> independent reading, and adopting, revising, or rejecting it on that basis —
> with every registration decision made by the author. The author does not
> claim they could have derived these methods unaided or on this timescale;
> the author does claim to understand each adopted choice well enough to
> defend it, and takes sole and full responsibility for the work's
> correctness and its errors.
> No AI system is credited as an author. AI involvement is recorded at commit
> granularity in the public repository (`Co-Authored-By` trailers on every
> commit after the initial scaffold), and the scoring rules were frozen under
> a public tag (`rules-registered-2026-08-09`) before any confirmatory run.

## Short form (submission-system fields)

> The author used Claude (Anthropic) extensively: it wrote most of the
> analysis code and documentation, and candidate methods typically originated
> with it. The author directed the work, required and checked the rationale
> for each adopted method, and made all final decisions; full responsibility
> for the content rests with the author. AI involvement is recorded per-commit
> in the public repository.

## Notes

- The sentence "The author does not claim they could have derived these
  methods unaided or on this timescale" goes beyond what any policy requires —
  policies ask for contributions, not counterfactual capability. It is
  included deliberately: it is true, it forecloses the discovered-overclaim
  failure mode, and it makes the accountability claim (understanding well
  enough to defend + responsibility) the one actually being made. Cut it only
  with the understanding that the rest of the statement still discloses
  everything policies require.
- Name the specific models if the venue asks for versions; the repo trailers
  record them per-commit (e.g. `Claude Opus 5`, `Claude Fable 5`).
