# Interview prep - questions this project lets you answer

1. **Walk me through the project.** Question -> data (8 tables) -> cleaning/joins -> KPIs -> statistics -> dashboard -> recommendations. Lead with the finding, not the tools.
2. **Why Jan 2017 - Aug 2018 only?** The other months have a handful of orders (e.g. 4 in Sep 2016, none in Nov 2016), so growth rates are meaningless.
3. **Why left joins?** Orders without items (canceled/unavailable) vanish in an inner join, which understated the cancellation rate.
4. **How do you define revenue?** Item price excluding freight, delivered orders. Payments run ~1% higher than items + freight; I flagged it rather than guessing the cause.
5. **Why not classic RFM?** About 97% of customers have frequency 1, so quintile scoring is meaningless. I used rule-based behavioral segments and say so.
6. **Why Mann-Whitney and not a t-test?** Review scores are ordinal and skewed. I also report effect size and a bootstrap CI because with ~95k orders p-values are always tiny.
7. **Does lateness cause bad reviews?** I can only claim association; late orders may differ by region, seller or product.
8. **What would you do next?** Seller-level analysis, a model to predict late deliveries, cohort retention curves, margin data.
9. **What was hardest / what would you change?** (Be honest: e.g. defining a consistent revenue metric across queries.)
10. **How did you check your dashboard numbers?** Reconciled Power BI totals with `results/key_findings.md` and the SQL exports.
