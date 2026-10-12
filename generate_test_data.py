import os
import random
import tomllib
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# --- Retrieve DB Connection from secrets.toml ---
secrets_path = os.path.join(".streamlit", "secrets.toml")
if os.path.exists(secrets_path):
    with open(secrets_path, "rb") as f:
        secrets = tomllib.load(f)
        db_url = secrets.get("postgres", {}).get("url")
else:
    raise FileNotFoundError("Could not locate .streamlit/secrets.toml")

engine = create_engine(db_url, pool_pre_ping=True)
Base = declarative_base()

# --- Model Definition Target: activity_logs_business ---
class ActivityLog(Base):
    __tablename__ = "activity_logs_business"  # <--- Isolated Business Table

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    subject = Column(Text, nullable=False)
    level = Column(Text, nullable=False)
    unit = Column(Text, nullable=False)
    subtopic = Column(Text, nullable=False)
    app_mode = Column(Text, nullable=False)
    score_pct = Column(Float, nullable=False)
    keywords_used = Column(Text, nullable=True)
    keywords_missed = Column(Text, nullable=True)
    misconception_flag = Column(Integer, default=0)

Base.metadata.create_all(engine)

# --- Sample Business Data Setup ---
COURSE_TITLE = "Pearson Edexcel Level 3 Advanced GCE in Business"
LEVEL = "A-Level"

THEMES_AND_SUBTOPICS = {
    "Theme 1: Marketing and people": [
        "1.1.1 The market", "1.1.2 Market research", "1.2.4 Price elasticity of demand", "1.3.3 Pricing strategies"
    ],
    "Theme 2: Managing business activities": [
        "2.1.1 Internal finance", "2.2.3 Break-even", "2.3.2 Liquidity", "2.4.1 Production, productivity and efficiency"
    ],
    "Theme 3: Business decisions and strategy": [
        "3.1.1 Corporate objectives", "3.1.3 SWOT analysis", "3.3.2 Investment appraisal", "3.5.2 Ratio analysis"
    ],
    "Theme 4: Global business": [
        "4.1.1 Growing economies", "4.1.3 Factors contributing to increased globalisation", "4.1.4 Protectionism"
    ]
}

MODES = ["socratic", "quiz", "extended", "rewrite"]

SAMPLE_KEYWORDS_USED = [
    "Margin of Safety", "Contribution", "Operating Profit", "Demand Elasticity", 
    "Working Capital", "Acid Test Ratio", "Market Segmentation", "SWOT Matrix"
]

SAMPLE_KEYWORDS_MISSED = [
    "Opportunity Cost", "Capacity Utilisation", "Gearing Ratio", "Ansoff Matrix",
    "JIT Inventory", "Diseconomies of Scale", "Kaizen", "Non-Current Liabilities"
]

# --- Generate 1,000 Mock Telemetry Records ---
print("🚀 Generating test records for 'activity_logs_business'...")

Session = sessionmaker(bind=engine)
session = Session()

records = []
now = datetime.utcnow()

for _ in range(1000):
    theme = random.choice(list(THEMES_AND_SUBTOPICS.keys()))
    subtopic = random.choice(THEMES_AND_SUBTOPICS[theme])
    mode = random.choice(MODES)
    
    score = round(random.triangular(30.0, 100.0, 75.0), 1)
    misconception = 1 if score < 45.0 else 0
    
    random_days = random.randint(0, 30)
    random_hours = random.randint(0, 23)
    record_time = now - timedelta(days=random_days, hours=random_hours)
    
    kw_used = random.sample(SAMPLE_KEYWORDS_USED, k=random.randint(1, 3))
    kw_missed = random.sample(SAMPLE_KEYWORDS_MISSED, k=random.randint(1, 3))

    entry = ActivityLog(
        timestamp=record_time,
        subject=COURSE_TITLE,
        level=LEVEL,
        unit=theme,
        subtopic=subtopic,
        app_mode=mode,
        score_pct=score,
        keywords_used=", ".join(kw_used),
        keywords_missed=", ".join(kw_missed),
        misconception_flag=misconception
    )
    records.append(entry)

session.bulk_save_objects(records)
session.commit()
session.close()

print(f"✅ Successfully seeded 1,000 Edexcel Business records into 'activity_logs_business'!")