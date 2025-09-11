from flask import Flask, request, render_template_string
#import mysql.connector
import psycopg2

app = Flask(__name__)

# Connect to MySQL

#db = mysql.connector.connect(
  #  host="localhost",
    #user="root",
   # password="1234566",  # Replace with your MySQL root password
    #database="chatdb"
#)

# PostgreSQL connection (Render)
db = psycopg2.connect(
    host="dpg-d313qegdl3ps73e1ec50-a.oregon-postgres.render.com",
    dbname="python_ai_app",
    user="root",
    password="mUfCMX2FSsHM1LiZYt5nYabMdczsa6wQ",
    port=5432
)

cursor = db.cursor()

# Example prohibited words
PROHIBITED_WORDS = ["politics", "bomb", "spam","hacking"]

# Example safe responses
SAFE_RESPONSES = [
    "Got it 👍",
    "That sounds interesting, tell me more!",
    "Hmm, I see what you mean.",
    "Thanks for sharing that.",
    "Cool! What else is on your mind?",
    "I understand. Let's continue..."
]

# Example prohibited response
PROHIBITED_RESPONSE = "⚠️ Your message contains prohibited content."

def generate_reply(user_message):
    """Generate a simple human-like reply."""
    msg = user_message.lower()

    if "hello" in msg or "hi" in msg:
        return "Hey there! How are you doing today?"
    elif "bye" in msg:
        return "Goodbye! Take care 👋"
    elif "how are you" in msg or "how are u" in msg:
        return "I'm doing great, thanks for asking! How about you?"
    else:
        return "That's interesting! Tell me more."



@app.route("/", methods=["GET", "POST"])
def chat():
    response = ""
    category = ""
    if request.method == "POST":
        user_message = request.form["message"]
        # Check if prohibited
        if any(word in user_message.lower() for word in PROHIBITED_WORDS):
            response = PROHIBITED_RESPONSE
            category = "prohibited"
        else:
            response = generate_reply(user_message)
            category = "non-prohibited"
        
        # Store in MySQL using title and content
        #cursor.execute(
         #   "INSERT INTO messages (title, content) VALUES (%s, %s)",
          #  (user_message, category)
        #)
        #db.commit()
        

    # Fetch all messages
    #cursor.execute("SELECT * FROM messages ORDER BY id DESC")
    #messages = cursor.fetchall()

    # Store message safely
        try:
            cursor.execute(
                "INSERT INTO messages (title, content) VALUES (%s, %s)",
                (user_message, category)
            )
            db.commit()
        except Exception as e:
            db.rollback()
            response = f"Database error: {str(e)}"

    # Fetch messages safely
    try:
        cursor.execute("SELECT * FROM messages ORDER BY id DESC")
        messages = cursor.fetchall()
    except Exception as e:
        db.rollback()
        messages = []
        response = f"Database error: {str(e)}"


    # Inline HTML
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Chat Tool</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
</head>
<body>
    <h1>AI Chat Tool</h1>
    <form method="POST">
        <input type="text" name="message" placeholder="Type your message" required>
        <input type="submit" value="Send">
    </form>
    {% if response %}
<div class="response-container">
    <div class="message ai">
        <div class="title">AI</div>
        {{ response }}
    </div>
</div>
{% endif %}
    <h3>Chat History:</h3>
    <table>
        <tr><th>ID</th><th>Title</th><th>Content</th></tr>
        {% for msg in messages %}
        <tr>
            <td>{{ msg[0] }}</td>
            <td>{{ msg[1] }}</td>
            <td>{{ msg[2] }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""

    return render_template_string(html, response=response, messages=messages)

if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
