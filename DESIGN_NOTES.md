# Design notes

Written so I can explain every choice in an interview. Section 9 lists the
questions I should be able to answer.

## 1. Why this question

I wanted a single pointed question that a small dataset can answer, with a
result I could be wrong about. "Do stronger cycles rise faster?" has a definite
answer in the data, a literature to compare against (the Waldmeier effect,
1935), and a built-in trap: rise *rate* is mechanically tied to amplitude, so
the analysis has to be designed to avoid a circular result (section 4). I make
no novelty claim. The value is in a clean, reproducible check.

## 2. Why this dataset

`statsmodels.datasets.sunspots` ships inside the package, so there is no
download, no licence question beyond public domain, and the statsmodels version
pin also pins the data. Alternatives: SILSO's current (2015-recalibrated) series
is better science but needs a download and an external dependency that can
change under me; the repo would stop being one-command reproducible.

## 3. Detecting cycles

Minima are local lows of a 3-year centered mean, accepted lowest-first with at
least 7 years between them (cycles last about 9 to 14 years, so 7 only
suppresses noise wiggles). The peak is the highest smoothed year between two
minima, and amplitude is that smoothed value. I chose this over `scipy
find_peaks` because every line is explainable and there is no prominence
parameter to tune. Validation: the detected minima match published cycle-start
dates within 2 years (a test), which checks the detector without circularity.
Alternative considered: fitting a parametric cycle shape. More principled,
much harder to defend line by line.

## 4. Rise time, not rise rate

Rate = (peak - minimum) / years. Amplitude appears in the numerator, so
correlating rate with amplitude would show a relationship even in random data. Rise
*duration* does not contain amplitude, so a negative correlation is informative.
This is the single most important design decision.

## 5. Spearman, permutation test, bootstrap

Rise time is integer-valued with heavy ties and only 26 points, and the
relationship need not be linear, so a rank correlation fits better than Pearson.
The permutation p-value makes no distributional assumption and handles ties
naturally; I use the +1 correction so p is never zero. The bootstrap resamples
whole cycles (pairs), which keeps each cycle's rise and amplitude together.
10,000 resamples each, fixed seed.

Known weakness: both treat cycles as independent, but cycle strengths are
autocorrelated. A block bootstrap or a model with an autocorrelated error would
be the honest next step (section 8).

## 6. Sensitivity analysis

The detector has two free choices: smoothing window and which early cycles to
trust. Rather than hide this, the README reports all six combinations. The
unsmoothed result (rho about -0.81) is much stronger than the primary
(-0.57). I believe unsmoothed minima and peaks are placed more precisely at
annual resolution, but I did not prove that, so I report the range and keep the
conservative window 3 as headline. Window 3 was chosen before seeing the other
windows' results.

## 7. Engineering choices

- Package in `src/` with small modules; `analysis.py` is a thin CLI. No
  notebook: a script is diff-able and runs in CI.
- Figures are committed (the README embeds them); other outputs are gitignored.
- `tests/test_reported_findings.py` pins the numbers quoted in the README, so a
  code change that moves a result fails the test and forces a README update.
- Pinned dependencies. CI runs ruff, the tests, and the full analysis on Python
  3.11 and 3.12. CI proves the code runs and numbers match on Linux; it does not
  prove the figures are byte-identical across platforms.
- `scripts/push.sh` refuses to commit or push unless tests and the analysis pass.

## 8. What I would do next

1. Block bootstrap / account for cycle-to-cycle autocorrelation.
2. Repeat with the recalibrated SILSO record to see whether the effect
   survives the 2015 revision.
3. Use monthly data for finer rise-time resolution (needs a different data source).
4. Test the fall-time null with an equivalence margin rather than only
   "not significant".

## 9. Questions I should be able to answer

- Why rise time instead of rise rate? (Section 4: circularity.)
- Why does smoothing change rho from -0.57 to -0.81, and which do you believe?
- Why a permutation test rather than a p-value from a formula?
- What does rho = -0.57 mean in plain words, and what does it not mean?
- Why is the p-value probably too optimistic? (Autocorrelated cycles.)
- You tested three outcomes; why is one the headline? (Specified in advance.)
- How do you know the cycle detector works? (Matches published dates.)
- Why is the final partial cycle dropped, and does it matter?
