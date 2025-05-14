# 🎬 YouTube Trending Video Forecasting

This project predicts the likelihood of YouTube videos trending based on metadata such as views, likes, comments, upload time, and title content using machine learning.

---

## 🚀 Features

- 🔍 Data collection via YouTube Data API  
- 📊 Exploratory Data Analysis (EDA)  
- 🧠 Feature engineering  
- 🤖 Model training using XGBoost  
- 📈 Prediction of trending probability  

---

## 📁 Project Structure

trending-video-forecast/
├── notebooks/
│ └── trending_youtube_video.ipynb # Interactive analysis and modeling
├── src/
│ ├── trending_youtube_video.py # Main script for training and prediction
│ └── utils/
│ └── init.py # Utility functions (if any)
├── data/ # (Optional) CSV data files
├── visuals/ # Plots, graphs, or output visuals
├── .gitignore # Files and folders ignored by Git
├── requirements.txt # Project dependencies
└── README.md # This file


## ▶️ How to Use

1. Place your dataset CSV file inside the `data/` folder.  
2. Run the script from terminal:

```bash
python src/trending_youtube_video.py --file data/your_dataset.csv
Or open the notebook in Jupyter:

jupyter notebook notebooks/trending_youtube_video.ipynb

💾 Setup Instructions
Install the required dependencies:

pip install -r requirements.txt
Make sure you have Python 3.7+ installed.

📊 Sample Visuals
(You can add screenshots or saved visualizations in the visuals/ folder and display them here)








