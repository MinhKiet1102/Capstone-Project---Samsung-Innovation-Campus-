from flask import Flask, request, render_template
import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import os

app = Flask(__name__)

# Đọc dữ liệu từ file Excel
file_path = "D:/SIC/dataset.xlsx"
data = pd.read_excel(file_path, engine='openpyxl')

# Chuẩn bị văn bản và nhãn
texts = data['Comment'].astype(str)
texts = [text if pd.notna(text) else '' for text in texts]
labels = data['Label_new']
labels = [star if pd.notna(star) else '' for star in labels]


vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

# Chia tập dữ liệu thành tập huấn luyện và tập kiểm tra
X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.3, random_state=42)

# Huấn luyện mô hình RandomForest
clf = RandomForestClassifier(n_estimators=300, random_state=42, max_depth=100)
clf.fit(X_train, y_train)


clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

# with open('scaler.pkl', 'wb') as f:
#     pickle.dump(scaler, f)

with open('classifier.pkl', 'wb') as f:
    pickle.dump(clf, f)

print("Đã lưu các tệp vectorizer.pkl, scaler.pkl và classifier.pkl")

with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)
# with open('scaler.pkl', 'rb') as f:
#     scaler = pickle.load(f)
with open('classifier.pkl', 'rb') as f:
    clf = pickle.load(f)

@app.route('/')
def home():
    return render_template('testapp.html')

@app.route('/predict', methods=['POST'])
def predict():
    user_input = request.form.get('comment')
    if not user_input and not 'file' in request.files:
        return render_template('testapp.html', prediction="Vui lòng nhập bình luận.")

    # Tiến hành phân tích bình luận
    user_vector = vectorizer.transform([user_input])
    user_prediction = clf.predict(user_vector)[0]

    prediction_mapping = {1: "Chưa tốt", 2: "Trunng bình", 3: "Tốt"}
    prediction_text = prediction_mapping.get(user_prediction, "Không xác định")

    prediction = f"Kết quả phân tích sản phẩm: {prediction_text}"

    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            file_path = os.path.join(app.root_path, file.filename)
            data = pd.read_excel(file, engine='openpyxl')

            comments = data.astype(str)
            comments = data['user_input']
            comments = [text if pd.notna(text) else '' for text in comments]
            vectors = vectorizer.transform(comments)
            predictions = clf.predict(vectors)
            print(predictions)
            average_score = sum(predictions) / len(predictions)
            print(average_score)
            if average_score <= 1.5:
                prediction_text = "Chưa tốt"
            elif average_score <= 2.5:
                prediction_text = "Trung bình"
            else:
                prediction_text = "Tốt"

    prediction = f"Kết quả phân tích sản phẩm: {prediction_text}"
    return render_template('testapp.html', user_input=user_input, prediction=prediction)


if __name__ == '__main__':
    app.run(debug=True)

