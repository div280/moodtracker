import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Create the SQLite database and table
def create_database():
    conn = sqlite3.connect("mood_tracker.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mood_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood TEXT,
            reason TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Log mood to the database
def log_mood(mood, reason=None):
    conn = sqlite3.connect("mood_tracker.db")
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO mood_entries (mood, reason, timestamp) VALUES (?, ?, ?)", (mood, reason, timestamp))
    conn.commit()
    conn.close()

# Fetch the daily mood report
def fetch_daily_report():
    conn = sqlite3.connect("mood_tracker.db")
    cursor = conn.cursor()
    today_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT mood, reason, timestamp FROM mood_entries WHERE timestamp LIKE ?", (f"{today_date}%",))
    data = cursor.fetchall()
    conn.close()
    return data

# Fetch the overall mood report
def fetch_overall_report():
    conn = sqlite3.connect("mood_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT mood, reason, timestamp FROM mood_entries")
    data = cursor.fetchall()
    conn.close()
    return data

# Calculate streak count
def calculate_streak():
    conn = sqlite3.connect("mood_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT DATE(timestamp) as date FROM mood_entries ORDER BY date")
    dates = [datetime.strptime(row[0], "%Y-%m-%d") for row in cursor.fetchall()]
    conn.close()

    streak = 1
    max_streak = 1

    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 1

    return streak, max_streak

# Generate a line graph for mood distribution
def generate_line_graph(data, title="Mood Distribution"):
    mood_counts = {}
    for mood, _, _ in data:
        mood_counts[mood] = mood_counts.get(mood, 0) + 1

    moods = list(mood_counts.keys())
    counts = list(mood_counts.values())

    plt.figure(figsize=(8, 5))
    plt.plot(moods, counts, marker='o', color='blue', linestyle='-', linewidth=2, markersize=6)
    plt.title(title, fontsize=14, color='darkgreen')
    plt.xlabel('Mood', fontsize=12, color='darkblue')
    plt.ylabel('Count', fontsize=12, color='darkblue')
    plt.xticks(rotation=45, ha='right', fontsize=10, color='brown')
    plt.tight_layout()
    st.pyplot(plt)

# Fun fact function
def fun_fact():
    facts = [
        "Did you know? Smiling can boost your immune system.",
        "Hugs release oxytocin, which makes you feel happier.",
        "Laughter can reduce stress and improve your mood.",
        "Listening to your favorite song can trigger a dopamine release.",
        "Practicing gratitude can significantly improve mental health."
    ]
    return facts[datetime.now().second % len(facts)]  # Rotate through facts dynamically

# Motivational thought function
def motivational_thought():
    return "Tough times never last, but tough people do. Keep going!"

# Streamlit app
def main_app():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(45deg, #ff9a9e, #fad0c4, #fbc2eb, #a1c4fd, #c2e9fb);
            background-size: 400% 400%;
            animation: GradientBG 15s ease infinite;
        }

        @keyframes GradientBG {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }

        h3 {
            color: #ff6f61;
            font-family: 'Comic Sans MS', cursive, sans-serif;
            text-shadow: 2px 2px #ffe4e1;
        }
        
        h4 {
            color: #f8b400;
            font-family: 'Comic Sans MS', cursive, sans-serif;
            text-shadow: 2px 2px #ffe4e1;
        }
        
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("✨Mood Tracker✨")
    st.markdown(
        "<h3>Track your emotions and discover what makes you YOU!</h3>",
        unsafe_allow_html=True,
    )

    create_database()

    # Sidebar setup with background
    st.sidebar.markdown(
        """
        <style>
        .sidebar .sidebar-content {
            background: linear-gradient(to bottom, #ff9a9e, #fad0c4, #fbc2eb);
            color: white;
            font-family: 'Comic Sans MS', cursive, sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True)

    # Show streak information
    current_streak, max_streak = calculate_streak()
    now = datetime.now().strftime("%A, %d %B %Y, %I:%M %p")
    st.markdown(
        f"<h4>🌟 Current Streak: {current_streak} day(s)</h4>"
        f"<h4>🔥 Max Streak: {max_streak} day(s)</h4>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='font-size:18px;'>🕒 Today is <b>{now}</b></p>",
        unsafe_allow_html=True,
    )

    # Fun fact
    st.info(fun_fact())

    menu = ["Log Mood", "Daily Report", "Overall Report", "Mood Statistics", "What Makes People Happy"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Log Mood":
        st.subheader("📝 Log Your Mood")
        mood = st.text_input("How are you feeling today? (e.g., happy, sad, angry, excited, content)")
        reason = st.text_area("Reason (Optional):")
        if st.button("Submit"):
            if mood:
                log_mood(mood, reason)
                if mood.lower() in ["sad", "angry", "frustrated", "anxious"]:
                    st.warning(motivational_thought())
                else:
                    st.success(f"Your mood has been logged! Keep shining 🌟")
            else:
                st.error("Please enter a mood.")

    elif choice == "Daily Report":
        st.subheader("📅 Daily Mood Report")
        data = fetch_daily_report()
        if data:
            generate_line_graph(data, "Mood Distribution for Today")
            df = pd.DataFrame(data, columns=["Mood", "Reason", "Timestamp"])
            st.table(df)
        else:
            st.info("No entries found for today.")

    elif choice == "Overall Report":
        st.subheader("📊 Overall Mood Report")
        data = fetch_overall_report()
        if data:
            generate_line_graph(data, "Overall Mood Distribution")
            df = pd.DataFrame(data, columns=["Mood", "Reason", "Timestamp"])
            st.table(df)
        else:
            st.info("No entries found.")

    elif choice == "Mood Statistics":
        st.subheader("📈 Mood Statistics")
        data = fetch_overall_report()
        if data:
            mood_counts = {}
            for mood, _, _ in data:
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
            st.write(mood_counts)
        else:
            st.info("No data available.")

    elif choice == "What Makes People Happy":
        st.subheader("😊 What Makes People Happy")
        happy_things = [
            "Spending time with loved ones",
            "Listening to music",
            "Traveling and exploring new places",
            "Reading a good book",
            "Watching favorite movies or shows",
            "Helping others",
            "Eating good food",
            "Engaging in hobbies like painting, photography, or gardening",
            "Exercising and staying active",
            "Practicing mindfulness and meditation"
        ]
        for item in happy_things:
            st.markdown(f"- {item}")

if __name__ == "__main__":
    main_app()
