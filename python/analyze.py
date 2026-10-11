
import pandas as pd
import numpy as np
import sqlite3, os
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "tech_support_dataset.csv")
VIZ = os.path.join(BASE, "visualizations")
OUT = os.path.join(BASE, "outputs")
os.makedirs(VIZ, exist_ok=True); os.makedirs(OUT, exist_ok=True)

df = pd.read_csv(DATA)

# -------------------- EDA / DATA QUALITY --------------------
df["Resolution_Minutes"] = df["Resolution_Time"].str.extract(r"(\d+)").astype(int)
df["Resolution_Hours"] = df["Resolution_Minutes"] / 60

eda = pd.DataFrame({
    "column": df.columns,
    "dtype": [str(df[c].dtype) for c in df.columns],
    "unique_values": [df[c].nunique() for c in df.columns],
    "missing_values": [df[c].isna().sum() for c in df.columns],
    "missing_pct": [df[c].isna().mean()*100 for c in df.columns]
})
eda.to_csv(os.path.join(OUT,"eda_data_quality.csv"),index=False)

# -------------------- BUSINESS OUTPUTS --------------------
total = len(df)
kpis = {
    "Total conversations": total,
    "Average resolution (min)": round(df.Resolution_Minutes.mean(),2),
    "Median resolution (min)": round(df.Resolution_Minutes.median(),2),
    "Direct resolution rate (%)": round((df.Issue_Status=="Resolved").mean()*100,2),
    "Eventual resolution rate (%)": round(df.Issue_Status.isin(["Resolved","Resolved after follow-up"]).mean()*100,2),
    "Escalation rate (%)": round((df.Issue_Status=="Escalated").mean()*100,2),
    "Pending rate (%)": round((df.Issue_Status=="Pending").mean()*100,2),
}
pd.DataFrame([kpis]).to_csv(os.path.join(OUT,"kpis.csv"),index=False)

issue_summary = df.groupby("Customer_Issue").agg(
    conversations=("Conversation_ID","count"),
    avg_resolution_min=("Resolution_Minutes","mean"),
    median_resolution_min=("Resolution_Minutes","median"),
    escalation_rate=("Issue_Status",lambda x:(x=="Escalated").mean()*100),
    followup_rate=("Issue_Status",lambda x:(x=="Resolved after follow-up").mean()*100)
).sort_values("conversations",ascending=False)
issue_summary.to_csv(os.path.join(OUT,"issue_summary.csv"))

category_summary = df.groupby("Issue_Category").agg(
    conversations=("Conversation_ID","count"),
    avg_resolution_min=("Resolution_Minutes","mean"),
    median_resolution_min=("Resolution_Minutes","median"),
    escalation_rate=("Issue_Status",lambda x:(x=="Escalated").mean()*100),
    pending_rate=("Issue_Status",lambda x:(x=="Pending").mean()*100)
).sort_values("avg_resolution_min",ascending=False)
category_summary.to_csv(os.path.join(OUT,"category_summary.csv"))

status_summary = df.groupby("Issue_Status").agg(
    conversations=("Conversation_ID","count"),
    avg_resolution_min=("Resolution_Minutes","mean")
)
status_summary["share_pct"] = status_summary["conversations"]/total*100
status_summary.to_csv(os.path.join(OUT,"status_summary.csv"))

response_summary = df.groupby("Tech_Response").agg(
    conversations=("Conversation_ID","count"),
    avg_resolution_min=("Resolution_Minutes","mean")
).sort_values("avg_resolution_min",ascending=False)
response_summary.to_csv(os.path.join(OUT,"response_summary.csv"))

# -------------------- SQL DATABASE --------------------
db = os.path.join(OUT,"tech_support.db")
con=sqlite3.connect(db)
clean=df.rename(columns={
    "Conversation_ID":"conversation_id","Customer_Issue":"customer_issue",
    "Tech_Response":"tech_response","Resolution_Time":"resolution_time",
    "Issue_Category":"issue_category","Issue_Status":"issue_status"
})[["conversation_id","customer_issue","tech_response","resolution_time","issue_category","issue_status","Resolution_Minutes","Resolution_Hours"]]
clean.columns=["conversation_id","customer_issue","tech_response","resolution_time","issue_category","issue_status","resolution_minutes","resolution_hours"]
clean.to_sql("tech_support",con,if_exists="replace",index=False)
con.close()

# -------------------- VISUALIZATIONS --------------------
def savefig(name):
    plt.tight_layout(); plt.savefig(os.path.join(VIZ,name),dpi=180,bbox_inches="tight"); plt.close()

plt.figure(figsize=(9,5))
issue_summary["conversations"].sort_values().plot(kind="barh")
plt.title("Conversation Volume by Customer Issue"); plt.xlabel("Conversations"); plt.ylabel("")
savefig("01_issue_volume.png")

plt.figure(figsize=(9,5))
category_summary["avg_resolution_min"].sort_values().plot(kind="barh")
plt.title("Average Resolution Time by Issue Category"); plt.xlabel("Minutes"); plt.ylabel("")
savefig("02_category_resolution.png")

plt.figure(figsize=(9,5))
status_summary["conversations"].sort_values().plot(kind="bar")
plt.title("Conversation Status Mix"); plt.ylabel("Conversations"); plt.xlabel("")
plt.xticks(rotation=25,ha="right")
savefig("03_status_mix.png")

plt.figure(figsize=(9,5))
df["Resolution_Minutes"].plot(kind="hist",bins=20,edgecolor="black")
plt.axvline(df.Resolution_Minutes.mean(),linestyle="--",label=f"Mean = {df.Resolution_Minutes.mean():.1f} min")
plt.axvline(df.Resolution_Minutes.median(),linestyle=":",label=f"Median = {df.Resolution_Minutes.median():.1f} min")
plt.title("Resolution Time Distribution"); plt.xlabel("Minutes"); plt.ylabel("Conversations"); plt.legend()
savefig("04_resolution_distribution.png")

ct=pd.crosstab(df.Customer_Issue,df.Issue_Status)
ct.plot(kind="bar",figsize=(11,6))
plt.title("Issue Volume by Status"); plt.xlabel(""); plt.ylabel("Conversations"); plt.xticks(rotation=30,ha="right")
savefig("05_issue_status.png")

plt.figure(figsize=(9,5))
issue_summary["escalation_rate"].sort_values().plot(kind="barh")
plt.title("Escalation Rate by Customer Issue"); plt.xlabel("Escalation rate (%)"); plt.ylabel("")
savefig("06_issue_escalation_rate.png")

plt.figure(figsize=(9,5))
response_summary["avg_resolution_min"].sort_values().plot(kind="barh")
plt.title("Average Resolution Time by Tech Response"); plt.xlabel("Minutes"); plt.ylabel("")
savefig("07_response_resolution.png")

# Category x status heatmap
pivot=pd.crosstab(df.Issue_Category,df.Issue_Status,normalize="index")*100
plt.figure(figsize=(10,5))
plt.imshow(pivot.values,aspect="auto")
plt.xticks(range(len(pivot.columns)),pivot.columns,rotation=25,ha="right")
plt.yticks(range(len(pivot.index)),pivot.index)
plt.colorbar(label="% of category")
plt.title("Status Mix Within Each Issue Category")
savefig("08_category_status_heatmap.png")

print("Analysis complete.")
print(kpis)
print("\nTop volume issue:\n", issue_summary.head(1))
print("\nHighest escalation issue:\n", issue_summary.sort_values("escalation_rate",ascending=False).head(1))
print("\nSlowest category:\n", category_summary.head(1))
