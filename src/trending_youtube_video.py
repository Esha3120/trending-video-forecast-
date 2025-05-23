# -*- coding: utf-8 -*-
"""trending_youtube_video.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1FrehKITTRGgwRqDQ_7m3zQYsqqW94sOk

# 📈 Predicting Trending YouTube Videos

Welcome to this machine learning project aimed at forecasting trending YouTube videos!  
This notebook walks through data loading, exploration, feature engineering, model training, and evaluation.

**Goal**: To analyze and predict the factors contributing to YouTube video popularity and trending status.

---

## 📦 Import Libraries

Import necessary libraries for data manipulation, visualization, and modeling.

### 🔧 Setting Up
Essential libraries are imported to handle data processing, visualization, and modeling.
"""

import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime

API_KEY = "AIzaSyDdwP2h9VY2c5TxtOpYGz1X9FabDlGdLuw"  # Replace with your key
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_trending_videos(region_code="IN", max_results=50):
    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        chart="mostPopular",
        regionCode=region_code,
        maxResults=max_results
    )
    return request.execute()

# Define regions and today's date
regions = ["IN", "US", "GB", "JP", "CA", "DE", "FR"]
today = datetime.now().strftime("%Y-%m-%d")
all_data = []

for region in regions:
    try:
        data = get_trending_videos(region)
        for item in data["items"]:
            all_data.append({
                "Region": region,
                "Title": item["snippet"]["title"],
                "Channel": item["snippet"]["channelTitle"],
                "Views": int(item["statistics"].get("viewCount", 0)),
                "Likes": int(item["statistics"].get("likeCount", 0)),
                "Comments": int(item["statistics"].get("commentCount", 0)),
                "Published At": item["snippet"]["publishedAt"]
            })
    except Exception as e:
        print(f"Error for region {region}: {e}")

# Convert to DataFrame and save
df = pd.DataFrame(all_data)
df["Published At"] = pd.to_datetime(df["Published At"])
filename = f"youtube_trending_{today}.csv"
df.to_csv(filename, index=False)
print(f"Saved {len(df)} rows to {filename}")

"""## 🧹 Missing Values

Check for any missing data in the dataset.

### 🕳️ Missing Data Check
Check if there are any null values that need handling.
"""

print(df.isnull().sum())  # Check missing values
df.dropna(inplace=True)   # Remove rows with missing data (if any)

"""## 📊 Summary Statistics

Generate summary statistics to understand feature distributions.

### 📊 Understand Distributions
Use descriptive statistics to get a basic feel for numeric features.
"""

print(df.describe())  # Summary stats for numerical columns

df['Engagement_Rate'] = (df['Likes'] + df['Comments']) / df['Views'] * 100
df_sorted = df.sort_values('Engagement_Rate', ascending=False)
print(df_sorted[['Title', 'Engagement_Rate']])

df['Published At'] = pd.to_datetime(df['Published At'])
df['Upload_Hour'] = df['Published At'].dt.hour
hourly_views = df.groupby('Upload_Hour')['Views'].mean()
print(hourly_views)

# Add a column for 12-hour format + AM/PM
df['Upload_Time'] = df['Upload_Hour'].map(
    lambda x: f"{x % 12 or 12}:00 {'AM' if x < 12 else 'PM'}"
)

"""## 📦 Import Libraries

Import necessary libraries for data manipulation, visualization, and modeling.

### 🔧 Setting Up
Essential libraries are imported to handle data processing, visualization, and modeling.
"""

import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='Views', y='Likes', hue='Channel', s=100)
plt.title("Trending Videos: Views vs. Likes (India)")
plt.show()

"""## 📦 Import Libraries

Import necessary libraries for data manipulation, visualization, and modeling.

### 🔧 Setting Up
Essential libraries are imported to handle data processing, visualization, and modeling.
"""

import seaborn as sns
import matplotlib.pyplot as plt

# Get the top 10 channels by views
top_10_channels = df.groupby('Channel')['Views'].sum().nlargest(10).index

# Filter the DataFrame to include only the top 10 channels
df_top_10 = df[df['Channel'].isin(top_10_channels)]

plt.figure(figsize=(20, 10))
sns.barplot(data=df_top_10, x='Channel', y='Views', palette='viridis')  # Plot for top 10
plt.xticks(rotation=90)
plt.title("Top Trending Channels in India")
plt.show()

# Add a column for 12-hour format + AM/PM within the 'df' DataFrame
df['Upload_Time'] = df['Upload_Hour'].map( # Use the existing 'Upload_Hour' column in 'df'
    lambda x: f"{x}:00 {'AM' if x < 12 else 'PM'}"
)

# Now, group by 'Upload_Time' to get hourly statistics
hourly_stats = df.groupby('Upload_Time').agg({'Views': 'mean', 'Likes': 'mean'})

# Proceed with the rest of your analysis (heatmap)
sns.heatmap(hourly_stats, annot=True, cmap='YlOrRd')
plt.title("Best Time to Upload for Maximum Engagement")
plt.show()

"""## 📦 Import Libraries

Import necessary libraries for data manipulation, visualization, and modeling.

### 🔧 Setting Up
Essential libraries are imported to handle data processing, visualization, and modeling.
"""

from textblob import TextBlob

def get_sentiment(title):
    return TextBlob(title).sentiment.polarity

df['Sentiment'] = df['Title'].apply(get_sentiment)
print(df[['Title', 'Sentiment']])

"""## 📦 Import Libraries

Import necessary libraries for data manipulation, visualization, and modeling.

### 🔧 Setting Up
Essential libraries are imported to handle data processing, visualization, and modeling.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
from textblob import TextBlob
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier

# 1. Data Preparation Function (with timezone fixes)
def prepare_data(df):
    """Prepare raw YouTube data for modeling with proper timezone handling"""
    # Convert to datetime - ensure timezone awareness
    df['Published At'] = pd.to_datetime(df['Published At']).dt.tz_convert(None)  # Remove timezone for compatibility

    # Basic features
    df['Upload_Hour'] = df['Published At'].dt.hour
    df['Upload_Weekday'] = df['Published At'].dt.weekday  # Monday=0
    df['Title_Length'] = df['Title'].apply(len)

    # Engagement ratios
    df['Like_View_Ratio'] = df['Likes'] / df['Views']
    df['Comment_View_Ratio'] = df['Comments'] / df['Views']
    df['Like_Comment_Ratio'] = df['Likes'] / (df['Comments'] + 1)  # Avoid division by zero

    # Target variable (top 20% by views)
    view_threshold = df['Views'].quantile(0.80)
    df['Is_Trending'] = (df['Views'] >= view_threshold).astype(int)

    return df

# 2. Feature Engineering Function (with timezone fixes)
def enhance_features(df):
    """Create additional predictive features with proper time handling"""
    # Title analysis
    df['Title_Has_Emoji'] = df['Title'].str.contains(r'[^\w\s]').astype(int)
    df['Title_Sentiment_Score'] = df['Title'].apply(lambda x: TextBlob(x).sentiment.polarity)
    df['Title_Word_Count'] = df['Title'].apply(lambda x: len(x.split()))
    df['Title_Caps_Ratio'] = df['Title'].apply(lambda x: sum(1 for c in x if c.isupper()) / len(x))
    df['Has_Official'] = df['Title'].str.contains('official', case=False).astype(int)

    # Channel popularity
    df['Channel_Frequency'] = df.groupby('Channel')['Channel'].transform('count')

    # Temporal features - ensure both datetimes are timezone-naive
    now = datetime.now().replace(tzinfo=None)  # Make timezone-naive
    df['Hours_Since_Upload'] = (now - df['Published At']).dt.total_seconds() / 3600

    # Combined engagement metrics
    df['Engagement_Score'] = (df['Likes'] * 0.6 + df['Comments'] * 0.4) / df['Views']

    return df

"""## ✂️ Train-Test Split

Split the dataset into training and testing subsets.

### 🧪 Train/Test Split
Split the dataset to evaluate the model on unseen data.
"""

# 3. Model Training Function (unchanged)
def train_trending_model(df):
    """Train and tune the XGBoost model"""
    # Get all features except metadata and target
    features = [col for col in df.columns if col not in [
        'Title', 'Channel', 'Views', 'Likes', 'Comments',
        'Published At', 'Is_Trending', 'Region'
    ]]

    X = df[features]
    y = df['Is_Trending']

    # Handle class imbalance
    smote = SMOTE(random_state=42)
    X_res, y_res = smote.fit_resample(X, y)

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_res, y_res, test_size=0.2, random_state=42
    )

    # Hyperparameter tuning
    param_grid = {
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2],
        'n_estimators': [50, 100, 200],
        'subsample': [0.8, 1.0]
    }

    grid_search = GridSearchCV(
        XGBClassifier(random_state=42),
        param_grid,
        cv=5,
        scoring='f1',
        n_jobs=-1
    )
    grid_search.fit(X_train, y_train)

    # Get best model
    best_model = grid_search.best_estimator_

    # Evaluate
    y_pred = best_model.predict(X_test)
    print("Model Evaluation:")
    print(classification_report(y_test, y_pred))
    print(f"Best Parameters: {grid_search.best_params_}")

    return best_model, features

# 4. Prediction Service Class (with timezone fixes)
class TrendingPredictor:
    def __init__(self, model, feature_columns):
        self.model = model
        self.feature_columns = feature_columns
        self.scaler = StandardScaler()

    def preprocess_input(self, video_data):
        """Prepare single video data for prediction with timezone handling"""
        # Convert to DataFrame if needed
        if isinstance(video_data, dict):
            video_df = pd.DataFrame([video_data])
        else:
            video_df = video_data.copy()

        # Handle timezone - make naive if necessary
        if pd.api.types.is_datetime64_any_dtype(video_df['Published At']):
            video_df['Published At'] = video_df['Published At'].dt.tz_localize(None)
        else:
            video_df['Published At'] = pd.to_datetime(video_df['Published At']).dt.tz_localize(None)

        # Calculate all required features
        video_df['Upload_Hour'] = video_df['Published At'].dt.hour
        video_df['Upload_Weekday'] = video_df['Published At'].dt.weekday
        video_df['Title_Length'] = video_df['Title'].apply(len)
        video_df['Like_View_Ratio'] = video_df['Likes'] / video_df['Views']
        video_df['Comment_View_Ratio'] = video_df['Comments'] / video_df['Views']
        video_df['Like_Comment_Ratio'] = video_df['Likes'] / (video_df['Comments'] + 1)

        # Add enhanced features
        video_df = enhance_features(video_df)

        # Ensure all features exist
        for feature in self.feature_columns:
            if feature not in video_df.columns:
                video_df[feature] = 0  # Default value if missing

        return video_df[self.feature_columns]

    def predict_probability(self, video_data):
        """Predict trending probability (0-1)"""
        features_df = self.preprocess_input(video_data)
        return float(self.model.predict_proba(features_df)[0][1])

"""## 📁 Load Dataset

Read the dataset containing YouTube video statistics.

### 📂 Load Data
Load the YouTube trending video dataset into a DataFrame.
"""

# 5. Complete System Implementation (with timezone fixes)
def build_trending_prediction_system(csv_path):
    """End-to-end system builder with proper timezone handling"""
    # Load and prepare data
    df = pd.read_csv(csv_path)
    df = prepare_data(df)
    df = enhance_features(df)

    # Train model
    model, features = train_trending_model(df)

    # Create predictor
    predictor = TrendingPredictor(model, features)

    return predictor

# Initialize the prediction system (run this first)
predictor = build_trending_prediction_system('youtube_trending_2025-05-05.csv')
print("Trending video predictor initialized successfully!")

# Predict for US video
us_video = {
    'Title': 'OFFICIAL: Summer Hits 2025 ',
    'Channel': 'Music Channel',
    'Views': 150000,
    'Likes': 7500,
    'Comments': 1200,
    'Published At': '2025-05-05T08:00:00Z',
    'Region': 'US'
}

prob = predictor.predict_probability(us_video)
print(f"\nUS Video Prediction:")
print(f"Title: {us_video['Title']}")
print(f"Channel: {us_video['Channel']}")
print(f"Published At: {us_video['Published At']}")
print(f"\nPredicted Trending Probability: {prob:.1%}")
print(f"Trending Status: {'Very likely' if prob > 0.7 else 'Possible' if prob > 0.4 else 'Unlikely'}")

# Predict for UK video
uk_video = {
    'Title': 'Behind the Scenes: Making of the Video',
    'Channel': 'Film Channel',
    'Views': 80000,
    'Likes': 4000,
    'Comments': 600,
    'Published At': '2025-05-05 14:30:00',
    'Region': 'UK'
}

prob = predictor.predict_probability(uk_video)
print(f"\nUK Video Prediction:")
print(f"Title: {uk_video['Title']}")
print(f"Channel: {uk_video['Channel']}")
print(f"Published At: {uk_video['Published At']}")
print(f"\nPredicted Trending Probability: {prob:.1%}")
print(f"Trending Status: {'Very likely' if prob > 0.7 else 'Possible' if prob > 0.4 else 'Unlikely'}")

# Predict for Indian street food video
indian_food_video = {
    'Title': 'Daily Vlog: Delhi Street Food Tour!',
    'Channel': 'Delhi Foodie',
    'Views': 850000,
    'Likes': 65000,
    'Comments': 8000,
    'Published At': '2025-05-05T12:30:00+05:30',  # 12:30 PM IST
    'Region': 'IN'
}

prob = predictor.predict_probability(indian_food_video)
print(f"\nIndian Street Food Video Prediction:")
print(f"Title: {indian_food_video['Title']}")
print(f"Channel: {indian_food_video['Channel']}")
print(f"Published At (IST): {indian_food_video['Published At']}")
print(f"\nPredicted Trending Probability: {prob:.1%}")
print(f"Trending Status: {'Very likely' if prob > 0.7 else 'Possible' if prob > 0.4 else 'Unlikely'}")

# Predict for Bollywood video
bollywood_video = {
    'Title': 'T-Series Presents: Bollywood Hits 2025 🎬',
    'Channel': 'T-Series',
    'Views': 2500000,
    'Likes': 125000,
    'Comments': 18000,
    'Published At': '2025-05-05T18:30:00+05:30',  # 6:30 PM IST
    'Region': 'IN'
}

prob = predictor.predict_probability(bollywood_video)
print(f"\nBollywood Video Prediction:")
print(f"Title: {bollywood_video['Title']}")
print(f"Channel: {bollywood_video['Channel']}")
print(f"Published At (IST): {bollywood_video['Published At']}")
print(f"\nPredicted Trending Probability: {prob:.1%}")
print(f"Trending Status: {'Very likely' if prob > 0.7 else 'Possible' if prob > 0.4 else 'Unlikely'}")

# Example Usage with Timezone Handling
if __name__ == "__main__":
    # Initialize system
    predictor = build_trending_prediction_system('youtube_trending_2025-05-05.csv')

    # New video to predict - with timezone handling examples
    new_videos = [
        {   # Timezone-aware format
            'Title': 'OFFICIAL: Summer Hits 2025 🔥',
            'Channel': 'Music Channel',
            'Views': 150000,
            'Likes': 7500,
            'Comments': 1200,
            'Published At': '2025-05-05T08:00:00Z',
            'Region': 'US'
        },
        {   # Timezone-naive format
            'Title': 'Behind the Scenes: Making of the Video',
            'Channel': 'Film Channel',
            'Views': 80000,
            'Likes': 4000,
            'Comments': 600,
            'Published At': '2025-05-05 14:30:00',
            'Region': 'UK'
        },
         {   # Indian video (YouTube creator)
            'Title': 'Daily Vlog: Delhi Street Food Tour!',
            'Channel': 'Delhi Foodie',
            'Views': 850000,
            'Likes': 65000,
            'Comments': 8000,
            'Published At': '2025-05-05T12:30:00+05:30',  # 12:30 PM IST
            'Region': 'IN'
        },
         {
        'Title': 'T-Series Presents: Bollywood Hits 2025 🎬',
        'Channel': 'T-Series',
        'Views': 2500000,
        'Likes': 125000,
        'Comments': 18000,
        'Published At': '2025-05-05T18:30:00+05:30',  # 6:30 PM IST
        'Region': 'IN'
    }
    ]

    # Make predictions
    for video in new_videos:
        prob = predictor.predict_probability(video)
        print(f"\nVideo: {video['Title']}")
        print(f"Predicted Trending Probability: {prob:.1%}")
        status = ('High chance' if prob > 0.7 else
                 'Moderate chance' if prob > 0.4 else
                 'Low chance')
        print(f"Trending Status: {status}")

"""## ✅ Conclusion

This notebook demonstrates a basic ML pipeline for predicting trending YouTube videos.  
Key takeaways:
- Feature engineering is crucial to boost model accuracy.
- Simple models like Random Forest or Logistic Regression can offer decent performance with the right features.
- Further improvements can be achieved with deep learning or NLP on video titles and descriptions.

---

**Next Steps**:
- Fine-tune hyperparameters
- Integrate video title/description text features
- Try temporal analysis or sentiment-based features

Feel free to fork and build on this project! 🚀

"""