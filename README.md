# Tech Support Dataset — SQL & Python EDA

## Project Overview
This project performs an end-to-end exploratory and business analysis of a technical support conversation dataset using **Python, Pandas, Matplotlib, SQLite and SQL**.
The objective is to understand support demand, resolution performance, issue/category behavior, escalation risk, response effectiveness, data quality, and operational opportunities.

## Dataset
- Rows: **1,896**
- Columns: 6
- Conversation IDs: 1,896 unique
- Missing values: **0**
- Resolution time range: **5–120 minutes**
- Average resolution time: **63.02 minutes**
- Median resolution time: **65 minutes**

### Source fields
| Field | Description |
|---|---|
| Conversation_ID | Unique support conversation identifier |
| Customer_Issue | Customer's reported technical problem |
| Tech_Response | Technical response provided |
| Resolution_Time | Resolution duration stored as text |
| Issue_Category | Support category |
| Issue_Status | Current/final support status |

## Tools & Technologies
- Python
- Pandas
- NumPy
- Matplotlib
- SQLite
- SQL

## Analysis Workflow

### 1. Python EDA
The Python workflow begins with:
- Shape and schema inspection
- Data type inspection
- Missing-value analysis
- Duplicate-row checks
- Unique-value profiling
- Categorical frequency analysis
- Resolution-time parsing
- Descriptive statistics
- Outlier/percentile review

### 2. Data Preparation
`Resolution_Time` is converted from strings such as `56 minutes` into:
- `Resolution_Minutes`
- `Resolution_Hours`
This allows numerical analysis and SQL aggregation.

### 3. Business Analysis
The project answers:
- What issues generate the most support volume?
- Which categories take longest to resolve?
- Which issues have the highest escalation risk?
- What is the direct vs eventual resolution rate?
- How large is the pending backlog?
- Which technical responses are associated with longer resolution times?
- How is resolution time distributed?
- Are issue/category/response relationships logically consistent?

### 4. SQL Analysis
The SQL layer contains queries for:
- Overall KPIs
- Issue volume and share
- Category performance
- Status mix
- Issue-level resolution and escalation
- Response performance
- Category × status analysis
- Resolution-time bands
- Data-quality checks

## Key Business Findings

### Support volume
**Slow system performance** is the most frequent issue with **293 conversations**.

### Resolution performance
Average resolution time is **63.02 minutes**, while the median is **65 minutes**. The 75th percentile is **93 minutes**, meaning a meaningful portion of cases take more than 1.5 hours.

### Status distribution
- Resolved: **26.64%**
- Pending: **25.21%**
- Resolved after follow-up: **24.89%**
- Escalated: **23.26%**

Only about **26.64%** are directly resolved, while **51.53%** are resolved when follow-up cases are included.

### Escalation risk
**Blue screen error** has the highest escalation rate at approximately **28.74%**.

### Category performance
**Network** is the slowest issue category, averaging approximately **65.26 minutes**.

### Response quality / data validation
A business-rule mapping from each customer issue to its expected troubleshooting response produces only **13.66% alignment** with the `Tech_Response` field.

This is an important data-quality finding. The response field appears weakly associated with the customer issue, so response-level operational conclusions should be treated cautiously until the source system is validated.

The issue-to-category distribution is similarly diffuse: no customer issue has more than roughly 26% concentration in a single category. This may indicate noisy categorization or a synthetic/randomized dataset.

## Recommendations
1. Build an issue-to-playbook triage matrix.
2. Route blue-screen cases to specialist support earlier.
3. Investigate network troubleshooting workflows to reduce resolution time.
4. Introduce SLA buckets and breach monitoring.
5. Track first-contact resolution separately from follow-up resolution.
6. Audit response and category labels in the source system.
7. Add root-cause and agent-level fields in future data collection.
8. Use a clean semantic data model before building an executive dashboard.

## Visualizations
The `visualizations/` folder contains eight charts covering:
- Issue volume
- Category resolution time
- Status mix
- Resolution-time distribution
- Issue × status
- Escalation rate
- Response resolution time
- Category × status mix

## Conclusion
The dataset shows a support operation with moderate resolution times but a fragmented outcome profile: only **26.64%** of cases are directly resolved, while **23.26%** are escalated and **25.21%** remain pending. The highest operational attention should go to **blue-screen escalations** and **network-related resolution delays**.
However, the most important analytical finding is a **data-quality concern**: the customer issue, category, and technical response fields show weak logical alignment. Before using this dataset to evaluate agents, playbooks, or response effectiveness, the organization should validate how these fields are generated and linked. Once the data model is reliable, the same SQL/Python framework can be extended into an SLA dashboard, root-cause analysis, agent performance model, and support forecasting solution.
