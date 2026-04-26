# 🏎️ F1 Command Center 2026

**F1 Command Center 2026** is a high-performance Formula 1 analytics and simulation dashboard. Built for enthusiasts and strategists, this application provides dynamic race predictions, qualifying simulations, and detailed insights into the 2026 grid using **Python** and **Streamlit**.

---

## 🚀 Key Features

### 📊 1. Race Probability Engine (ANALYSIS)
- **Dynamic Logic:** Uses a custom algorithm to calculate win probabilities based on circuit characteristics.
- **Track Affinity:** Factors in whether a driver/car is optimized for **Street Circuits**, **High Speed Cornering**, or **Power Tracks**.
- **Real-time Visualization:** Interactive horizontal bar charts powered by **Plotly** to visualize win confidence levels.

### ⏱️ 2. Qualifying Simulator
- **Full Knockout Simulation:** Experience the tension of **Q1, Q2, and Q3**.
- **ML-Driven Lap Times:** Calculates realistic lap times based on driver base stats, track difficulty, and random "on-track" variables (traffic, wind, errors).
- **Pole Position Tracking:** Automatically identifies the pole sitter and qualifying dropouts in a professional F1 layout.

### 👤 3. Driver & Team Profiles
- **2026 Grid Ready:** Includes the complete 2026 lineup, including new entries like **Audi** and **Cadillac**.
- **Premium UI:** Custom dark-themed cards with official team gradients and car renders.
- **Automatic Fallbacks:** Integrated UI avatars and fallback images ensure a smooth visual experience.

### 📅 4. 2026 Season Schedule
- **Interactive Calendar:** A full 24-race calendar for the 2026 season.
- **Visual Circuit Maps:** Dark-mode optimized circuit outlines using Base64 image encoding for lightning-fast loading.

---

## 🛠️ Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/) (High-performance web framework)
- **Data Handling:** [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/)
- **Visuals:** [Plotly Express](https://plotly.com/python/) (Interactive charts)
- **Styling:** Custom CSS & HTML Injection for a premium F1 look.

---
