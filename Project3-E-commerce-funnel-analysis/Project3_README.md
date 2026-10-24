# E-commerce Funnel Analysis

**Tools:** SQLite | SQL | Python | Power BI

## Project overview
Most visitors to an online shop leave without buying. This project analyses shopper behaviour data from the Retailrocket e-commerce dataset to find **where visitors drop off between viewing a product and buying it**, and how long buyers take to decide.

![E-commerce funnel dashboard](images/dashboard.png)

## Business questions
1. How many visitors move from viewing a product to adding it to the cart, and then to buying it?
2. Which step of the funnel loses the most visitors?
3. How do cart visitors and buyers change day by day?
4. Which items get the most views?
5. How long do buyers take to complete a purchase?

## Dataset
Retailrocket e-commerce events data from 2015. Each event records a visitor, an item and an action (view, add to cart or purchase) with a time stamp.

## Method
- Loaded the event data into SQLite
- Wrote SQL queries to count unique visitors at each funnel step, daily cart visitors and buyers, the most viewed items, and the time between a visitor's first view and purchase
- Grouped purchase time into bands: within 1 hour, 1 to 24 hours, 1 to 7 days and over 7 days
- Saved the query results in the `results` folder and used them in a Power BI dashboard

## Dashboard
- **KPI cards:** viewers, cart visitors, buyers, view-to-purchase rate
- **Charts:** visitor funnel, daily cart visitors and buyers, top 20 most viewed items, and how long buyers take to purchase

## Key findings

| Funnel step | Visitors | Share of viewers |
|---|---|---|
| 1. Viewed a product | 1,404,179 | 100% |
| 2. Added to cart | 34,401 | 2.45% |
| 3. Purchased | 10,228 | 0.73% |

1. **The biggest drop is between viewing and adding to cart.** Only about 2.5% of viewers add anything to the cart, so about 97.5% leave before that step.
2. **Once visitors add to the cart, about 30% buy** (10,228 of 34,401). The cart step converts far better than the browsing step.
3. **Overall, 0.73% of viewers buy.**
4. **Most buyers decide fast.** In the time-to-purchase chart, about 7.7K purchases happen within 1 hour, against 1.8K within 1 to 24 hours, 1.0K within 1 to 7 days and 1.2K after more than 7 days. That is about two thirds within the first hour.
5. **The most viewed item (ID 187946) had about 2,900 viewers**, followed by item 5411 with about 2,100. Views are concentrated on a few popular items.
6. **Daily cart visitors and buyers rise and fall in a repeating pattern**, with cart visitors reaching about 400 on peak days and buyers about 100 to 150.

## Recommendations
1. Improve product pages (clear photos, prices, reviews and delivery details) to lift the view-to-cart rate, the largest drop-off.
2. Send cart reminders or offers within the first hour, since most purchases happen quickly.
3. Follow up with buyers who wait more than a day using email or retargeting offers.
4. Feature the most viewed items on the home page and in campaigns.
5. Plan promotions around the high-traffic days seen in the daily trend.

## Project structure
```
Project3-E-commerce-funnel-analysis/
|-- images/        dashboard screenshot
|-- powerbi/       Power BI file
|-- python/        Python scripts
|-- results/       query results used in the dashboard
|-- sql/           SQL queries
`-- README.md
```

## How to view
Open the Power BI file in the `powerbi` folder using Power BI Desktop. The SQL queries are in the `sql` folder.

## Author
**Yash Zade** | yashzade0705@gmail.com | [GitHub](https://github.com/yashzade0705-stack)
