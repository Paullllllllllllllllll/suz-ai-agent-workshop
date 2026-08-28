# Reading List: Working with AI, Responsibly

This list accompanies the closing discussion of the workshop (08.09.2026)
and travels with the follow-up package. It is organized around the five
questions the discussion raises: what happens to skills you stop
practicing, whether AI-generated text can be detected, what sustained AI
use does to attention and judgment, what the trajectory of these tools
means for our own work, and what you can defensibly use them for in
research. A closing section covers synthetic participants, the case the
afternoon demonstrated. Each entry carries a short note on what it shows
and why it earns its place; none of them requires technical background.
Where a paper is open access, the link leads straight to it; the rest
open through the university network.

## 1. Deskilling and cognitive offloading

The oldest question on the list, and the one with the newest evidence:
when a tool takes over part of your thinking, what happens to the part
you kept?

- Braverman, H. (1974). *Labor and Monopoly Capital: The Degradation of
  Work in the Twentieth Century*. Monthly Review Press.
  The canonical sociological theory of deskilling: technology absorbs
  craft knowledge and separates conception from execution. It supplies
  the vocabulary that lets the 2025 findings below read as a
  continuation rather than a novelty.
- Sparrow, B., Liu, J., & Wegner, D. M. (2011). Google effects on
  memory: Cognitive consequences of having information at our
  fingertips. *Science*, 333(6043), 776-778.
  <https://www.science.org/doi/10.1126/science.1207745>
  People remember where information lives rather than the information
  itself once they expect continued access. Cognitive offloading
  predates LLMs; the debate is about degree and domain, not rupture.
- Dell'Acqua, F. (2022). Falling asleep at the wheel: Human/AI
  collaboration in a field experiment on HR recruiters. Working paper,
  Harvard Business School. <https://www.fabriziodellacqua.com/>
  Recruiters given better AI evaluated faster but less accurately and
  stopped improving, while those with weaker AI stayed vigilant. The
  quality of the assistant changes how much of your own judgment you
  keep exercising.
- Bastani, H., Bastani, O., Sungu, A., Ge, H., Kabakcı, Ö., &
  Mariman, R. (2025). Generative AI without guardrails can harm
  learning: Evidence from high school mathematics. *PNAS*, 122(26).
  <https://www.pnas.org/doi/10.1073/pnas.2422633122>
  A randomized trial with about 1,000 students: unrestricted GPT-4
  access raised practice scores and cut later unaided exam scores by
  17 percent; a tutor-style scaffolded version removed the harm.
  Deskilling is a design variable, not an inherent property of the
  technology.
- Budzyń, K., et al. (2025). Endoscopist deskilling risk after exposure
  to artificial intelligence in colonoscopy. *The Lancet
  Gastroenterology & Hepatology*, 10(10), 896-903.
  <https://doi.org/10.1016/S2468-1253(25)00133-5>
  After routine AI assistance was introduced, detection rates in
  *unassisted* procedures fell measurably: the first real-world
  evidence tying automation-induced deskilling to professional
  outcomes.
- Lee, H.-P., et al. (2025). The impact of generative AI on critical
  thinking: Self-reported reductions in cognitive effort and confidence
  effects from a survey of knowledge workers. *CHI 2025*.
  <https://doi.org/10.1145/3706598.3713778>
  Across 936 real work episodes, confidence in the AI predicts less
  critical thinking; effort shifts from doing to supervising. The best
  available account of what "cognitive surrender" looks like in
  professional practice.
- Kosmyna, N., et al. (2025). Your brain on ChatGPT: Accumulation of
  cognitive debt when using an AI assistant for essay writing.
  arXiv:2506.08872. <https://arxiv.org/abs/2506.08872>
  The widely cited EEG study: LLM-assisted writers showed the weakest
  neural connectivity and often could not quote their own text. Read it
  together with its critics (it is not peer reviewed, the sample is
  small, and a formal critique exists) — which makes it a useful
  exercise in evidence appraisal as well as a finding.

## 2. Detecting AI-generated text

Detection is asymmetric: the standard tools fail in ways that harm
exactly the people research is meant to describe, while the newest
generation is better than its reputation — and still not evidence.

- Liang, W., Yuksekgonul, M., Mao, Y., Wu, E., & Zou, J. (2023). GPT
  detectors are biased against non-native English writers. *Patterns*,
  4(7). <https://doi.org/10.1016/j.patter.2023.100779>
  Seven widely used detectors misclassified more than half of essays by
  non-native English speakers as AI-generated while judging native
  speakers near-perfectly. The canonical fairness objection to running
  detectors on student work or survey responses in a multilingual
  population.
- Emi, B., & Spero, M. (2024). Technical report on the Pangram
  AI-generated text classifier. arXiv:2402.14873.
  <https://arxiv.org/abs/2402.14873>
  The vendor's account of the detector the discussion names: a
  supervised classifier reporting error rates far below zero-shot
  methods, including near-zero false positives on learner-English
  corpora — an explicit answer to Liang et al., though from the vendor
  itself.
- Glickenhaus, B., et al. (2026). Pangram 4 technical report.
  arXiv:2607.27183. <https://arxiv.org/abs/2607.27183>
  The current generation, including detection of mixed human/AI
  authorship — the realistic case, since student and respondent text is
  rarely fully AI-written.
- Jabarian, B., & Imas, A. (2025). Artificial writing and automated
  detection. NBER Working Paper 34223.
  <https://www.nber.org/papers/w34223>
  The key independent evaluation: across genres, lengths, and
  "humanizer" attacks, Pangram reaches near-zero error rates and
  substantially outperforms its rivals. Its "policy cap" framework for
  choosing an acceptable error trade-off is the practical takeaway for
  any department considering deployment. Even so: a low false-positive
  rate is a population statistic, not defensible evidence in an
  individual case.

## 3. Dependence and affective use

What does it change when the tool is also a conversation partner?

- Phang, J., et al. (2025). Investigating affective use and emotional
  well-being on ChatGPT. arXiv:2504.03888.
  <https://arxiv.org/abs/2504.03888>
  The OpenAI/MIT collaboration, platform side: affective engagement is
  rare overall but concentrated in a small group of heavy users, where
  it tracks loneliness and emotional dependence.
- Fang, C. M., et al. (2025). How AI and human behaviors shape
  psychosocial effects of extended chatbot use: A longitudinal
  randomized controlled study. arXiv:2503.17473.
  <https://arxiv.org/abs/2503.17473>
  The strongest causal evidence available: a four-week preregistered
  trial with about 1,000 participants, with effects moderated by
  baseline attachment and trust — exactly the heterogeneity a
  sociologist would predict.
- Zhang, Y., Zhao, D., Hancock, J. T., Kraut, R., & Yang, D. (2025).
  The rise of AI companions: Interaction with AI companions and
  psychological well-being. arXiv:2506.12605.
  <https://arxiv.org/abs/2506.12605>
  A vulnerability cycle: people with weaker human support lean hardest
  on chatbot companionship and are most exposed to its risks. Selection
  versus causation, in its newest costume.
- Hung, J. W., Lee, C. K. Y., Kasturiratna, K. T. A. S., & Hartanto, A.
  (2026). Parasocial relationships with artificial intelligence: A
  systematic review of benefits and risks. *Computers in Human
  Behavior: Artificial Humans*, 8.
  <https://doi.org/10.1016/j.chbah.2026.100323>
  The field's best entry point, and honest about its weakness: no
  consistent definition or measurement, and almost no longitudinal
  work.

## 4. What this means for our own work

The question a day of hands-on use raises and cannot answer. Today was
the floor, not the ceiling: these tools are the least capable they will
ever be. Section 1 asks what happens to a skill you stop practicing;
this asks what happens to the job. Read the entry below against
Dell'Acqua and Bastani above, which describe the same shift at the level
of the individual rather than the profession.

- Brynjolfsson, E., Li, D., & Raymond, L. R. (2023). Generative AI at
  work. *NBER Working Paper* 31161.
  <https://www.nber.org/papers/w31161>
  A field study of 5,179 customer-support agents: average productivity
  rose 14 percent, and almost all of the gain went to the least
  experienced workers. Read it as a question about apprenticeship rather
  than about productivity. If the tool compresses the distance between a
  novice and an expert, and absorbs precisely the junior tasks through
  which novices used to become experts, what is left of the path from one
  to the other?

## 5. The defensible core: using AI in research

The constructive question the discussion ends on: what can you use these
tools for, and what do you owe a reader when you do?

- European Commission / ERA Forum (2026). *Living Guidelines on the
  Responsible Use of Generative AI in Research* (third version, May
  2026).
  <https://research-and-innovation.ec.europa.eu/news/all-research-and-innovation-news/updated-era-living-guidelines-responsible-use-generative-ai-research-2026-05-08_en>
  The de facto European reference framework and the baseline a Swiss
  researcher will increasingly be held to: reliability, honesty,
  respect, and accountability, with separate duties for researchers,
  institutions, and funders.
- Abdurahman, S., Salkhordeh Ziabari, A., Moore, A. K., Bartels, D. M.,
  & Dehghani, M. (2025). A primer for evaluating large language models
  in social-science research. *Advances in Methods and Practices in
  Psychological Science*, 8(2).
  <https://doi.org/10.1177/25152459251325174>
  The most directly actionable item on this list: how to use an LLM as
  a coder or annotator and survive peer review — model and version
  reporting, prompt disclosure, human-validation subsets, robustness
  checks.
- Messeri, L., & Crockett, M. J. (2024). Artificial intelligence and
  illusions of understanding in scientific research. *Nature*,
  627(8002), 49-58. <https://doi.org/10.1038/s41586-024-07146-0>
  The epistemological counterweight: four visions of AI in research,
  each exploiting cognitive limits to produce illusions of
  understanding. Not "is it accurate?" but "what kinds of knowledge
  does adopting it foreclose?"
- Desai, M., Card, D., & Jacobs, A. Z. (2026). Validating LLMs in
  social science: Epistemic threats and emerging norms.
  arXiv:2607.07915. <https://arxiv.org/abs/2607.07915>
  What published studies actually do when they prompt LLMs for
  measurement — and how thin current validation practice is. Pairs with
  the Abdurahman primer as description against prescription.
- Journal policies, continuously revised and worth checking live:
  Springer Nature (<https://www.nature.com/nature-portfolio/editorial-policies/ai>)
  and Science/AAAS (<https://www.science.org/content/blog-post/change-policy-use-generative-ai-and-large-language-models>).
  Both refuse AI authorship; both now require disclosure rather than
  banning use; Nature additionally forbids uploading manuscripts under
  review to AI tools.

- Mittelstadt, B. (2019). Principles alone cannot guarantee ethical AI.
  *Nature Machine Intelligence*, 1(11), 501-507.
  <https://arxiv.org/abs/1906.06668>
  Seven pages on why a shared list of principles does not produce ethical
  practice: the field has none of the professional structures, fiduciary
  duties or enforcement that made principled ethics work in medicine. The
  sharpest short account of ethics washing, and the reason the guidelines
  above are a floor rather than an answer.
- Raji, I. D., Smart, A., White, R. N., Mitchell, M., Gebru, T.,
  Hutchinson, B., Smith-Loud, J., Theron, D., & Barnes, P. (2020).
  Closing the AI accountability gap: Defining an end-to-end framework for
  internal algorithmic auditing. *Proceedings of FAccT 2020*, 33-44.
  <https://dl.acm.org/doi/pdf/10.1145/3351095.3372873>
  The scholarly form of the move you made in the hands-on block: auditing
  a system you built yourself, before anyone outside ever sees it. Worth
  reading precisely because you have now done a small version of it by
  hand and know where it is uncomfortable.
- Binz, M., et al. (2025). How should the advancement of large language
  models affect the practice of science? *PNAS*, 122(5), e2401227121.
  <https://doi.org/10.1073/pnas.2401227121>
  Eighteen authors who do not agree with each other, arguing out the
  question this workshop raises and cannot settle. Read it for the
  disagreement rather than for a verdict: it is the best available map of
  where reasonable people currently stand.

## 6. Synthetic participants: standing in for people

The afternoon generated a synthetic dataset from a codebook. These two
papers are the argument about how far that goes once the rows are meant
to represent people rather than to give a pipeline something to run on.
They disagree, and the disagreement is the point.

- Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., &
  Wingate, D. (2023). Out of one, many: Using language models to simulate
  human samples. *Political Analysis*, 31(3), 337-351.
  <https://doi.org/10.1017/pan.2023.2>
  The paper that opened this line of work and the source of "algorithmic
  fidelity": conditioned on real demographic profiles, a model reproduces
  patterns in American survey data closely enough to be worth taking
  seriously. Start here, then read the next entry before you believe it.
- Gao, Y., Lee, D., Burtch, G., & Fazelpour, S. (2024). Take caution in
  using LLMs as human surrogates. arXiv:2410.19599.
  <https://arxiv.org/abs/2410.19599>
  The counterweight, and the reason the dataset block insists that
  synthetic data gives you the shape of a result and never the result:
  model "participants" diverge from human ones in exactly the places a
  study is usually about.
