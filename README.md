# 🩹 Wound Healing Estimation System

An AI-powered web application that analyzes wound images and estimates the healing progress using deep learning and image processing techniques. The system provides healing percentage, recovery insights, and a simulated healing visualization.

---

## 📌 Project Overview

The **Wound Healing Estimator** is designed to assist in monitoring wound recovery by analyzing uploaded images. It uses a deep learning model (ResNet18) along with a fallback heuristic approach to predict healing progress and provide medical guidance.

---

## 🛠️ Technologies Used

* Python (Flask)
* PyTorch (Deep Learning)
* OpenCV (Image Processing)
* NumPy & Pandas
* HTML, CSS, JavaScript
* Plotly (Data Visualization)

---

## ✨ Features

### 🧠 AI-Based Prediction

* Uses **ResNet18 CNN model** for wound healing estimation
* Outputs healing percentage (0–100%)
* Automatically falls back to heuristic estimation if model is unavailable

---

### 🖼️ Image Processing

* Upload and analyze wound images
* Resize, zoom, and adjust image before prediction
* Detect wound regions using HSV color filtering

---

### 📊 Healing Insights

* Displays:

  * Healing percentage
  * Estimated recovery time
  * Wound severity (Mild, Moderate, Severe)
* Provides dynamic medical advice

---

### 🧪 Healing Simulation

* Generates a **visual simulation of wound healing**
* Uses OpenCV warping to mimic natural skin closure

---

### 📈 History Dashboard

* Stores healing progress in CSV
* Displays healing trends over time
* Interactive graph using Plotly

---

## 📁 Project Structure

```bash
├── app.py                  # Flask backend
├── models/                 # Trained model file (.pt)
├── static/
│   ├── styles.css
│   ├── script.js
│   └── healed_preview.jpg
├── templates/
│   ├── index.html
│   ├── history.html
│   └── base.html
├── data/
│   └── healing_log.csv
└── README.md
```

---

## 🚀 How to Run the Project

### 🔹 Step 1: Clone the Repository

```bash
git clone https://github.com/shilpaa14/wound-healing-project.git
cd wound-healing-project
```

---

### 🔹 Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 🔹 Step 3: Run the Application

```bash
python app.py
```

---

### 🔹 Step 4: Open in Browser

```bash
http://localhost:5000
```

---

## 🧠 Model Details

* Architecture: ResNet18
* Output: Single regression value (0–1)
* Activation: Sigmoid
* Converted to healing percentage

---

## ⚠️ Fallback Mechanism

If the trained model is not available:

* Uses heuristic approach based on:

  * Redness detection
  * Darkness intensity
* Ensures system always provides output

---

## 📊 Healing Status Logic

| Healing % | Status   |
| --------- | -------- |
| 85–100    | Healed   |
| 60–84     | Mild     |
| 30–59     | Moderate |
| <30       | Severe   |

---

## 🎯 Purpose

* Assist in wound monitoring
* Provide early insights into healing progress
* Demonstrate AI + healthcare integration
* Showcase full-stack + ML capabilities

---

## 🤝 Contributing

Contributions are welcome! 🎉

If you'd like to improve this project, feel free to:

* 🍴 Fork the repository
* 🌿 Create a new branch (`git checkout -b feature-name`)
* 💡 Make your changes or add new features
* ✅ Commit your changes (`git commit -m "Add feature"`)
* 🚀 Push to your fork (`git push origin feature-name`)
* 🔁 Open a Pull Request

---

### 💡 Ideas for Contributions

* Improve model accuracy
* Add new datasets
* Enhance UI/UX
* Optimize image processing
* Add more medical insights or features

---

### ⚠️ Note

Please ensure your code is clean, well-documented, and tested before submitting a pull request.

---

Together, we can make this project better 🚀


## ⚠️ Disclaimer

This application is for educational and research purposes only.
It is **not a substitute for professional medical advice**.

---

## 👩‍💻 Author

**Shilpa Nayak**

---

## 📄 License

This project is licensed under the MIT License.
