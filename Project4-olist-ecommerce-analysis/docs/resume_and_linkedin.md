# Resume bullets

**Olist E-Commerce Analysis | SQL, Python, Power BI, Excel, Statistics**  - github.com/<your-username>/data-analyst-portfolio/tree/main/Project4-olist-ecommerce-analysis
- Built an end-to-end analysis of 99k orders: cleaned and joined 8 tables with SQL and pandas, using left joins so orders without items (canceled/unavailable) were not silently dropped from KPIs.
- Found that only 3.0% of customers ordered more than once, segmented customers with a rule-based behavioral model and proposed a second-purchase campaign.
- Showed with a Mann-Whitney U test (p < 0.001, large effect size r = -0.64) that late deliveries were associated with 2.0 fewer review stars (4.29 vs 2.27), with scores falling from 3.3 to 1.7 stars as delays grew from 1-3 to 8+ days.
- Quantified delivery performance across states (8.8 days in SP vs 29.4 in RR; 6.8% of orders late) and tracked R$ 13.2M of revenue growth (monthly revenue +650% from Jan 2017 to Aug 2018).
- Designed a 2-page Power BI dashboard (star schema, DAX measures for revenue, AOV, late-delivery %) and an Excel workbook for non-technical stakeholders.

# LinkedIn post draft

I analysed 99,000 real e-commerce orders to answer one question: where is growth hiding?

3 things I found:
1. Only 3.0% of customers ever ordered twice. Revenue grew 650% in 20 months, so retention is the biggest opportunity.
2. Late deliveries average 2.3 stars vs 4.3 on time, and even 1-3 days late costs about a full star. It's statistically significant, but I'm careful to say associated, not caused.
3. Delivery takes 29 days in the slowest state vs 9 in the fastest.

Tools: SQL, Python (pandas, scipy), Power BI, Excel.
The one lesson: an inner join silently dropped canceled orders and understated the cancellation rate. Check what your joins throw away.

Code + dashboard: <GitHub link>
#dataanalytics #sql #python #powerbi
