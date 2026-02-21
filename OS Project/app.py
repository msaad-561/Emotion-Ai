import cv2
from flask import Flask, render_template, redirect, url_for, request, Response, session, jsonify
import time
from music_recommender import get_song_recommendation
from database import save_emotion, get_user_history, get_user_counts, get_mood_scores

app = Flask(__name__)
# In production, use a secure secret key
app.secret_key = 'dev_secret_key'

# Global variable for camera
camera = None
# Global variable for emotion data
latest_emotion_data = {
    "dominant_emotion": "Neutral",
    "emotions": {"angry": 0, "disgust": 0, "fear": 0, "happy": 0, "sad": 0, "surprise": 0, "neutral": 0},
    "quick_reset": "",
    "benefits": "",
    "joke": None
}

# Emotion Detector Setup
try:
    # Fix for FER 25.1: Import explicitly from fer.fer
    from fer.fer import FER
    import tensorflow as tf
    # Optional: Check if GPU is available, but FER handles this.
    # We initialize the detector with MTCNN for better face detection if possible, or default.
    # For speed, let's stick to default opencv face detection inside FER if mtcnn is too slow, 
    # but mtcnn is more accurate. Let's try default first for speed on laptop.
    # ERROR FIX: mtcnn=True requires 'facenet-pytorch'. usage of mtcnn=False uses built-in OpenCV (safer).
    detector = FER(mtcnn=False) 
    print("FER Library Loaded Successfully!")
except ImportError as e:
    print(f"FER Import Error: {e}")
    detector = None
except Exception as e:
    print(f"FER Init Error: {e}")
    detector = None

# Mock Fallback (Only used if FER fails)
class MockDetector:
    def __init__(self):
        self.last_update = 0
        self.current_emotion_idx = 0
        # Custom emotions as requested: Neutral -> Relaxed/Stressed
        self.emotions = ['Happy', 'Sad', 'Angry', 'Relaxed', 'Stressed']
        
    def detect_emotions(self, frame):
        # 10 Seconds Locking Mechanism
        now = time.time()
        if now - self.last_update > 10:
            # Time to switch emotion
            self.current_emotion_idx = (self.current_emotion_idx + 1) % len(self.emotions)
            self.last_update = now
        
        curr = self.emotions[self.current_emotion_idx]
        
        # Helper to return a variable score to test aggregation
        val = {e.lower(): 0.1 for e in self.emotions}
        val[curr.lower()] = 0.6 # Dominant
        
        return [{
            'box': (200, 150, 200, 200),
            'emotions': val
        }]

if detector is None:
    print("Using MockDetector due to missing FER/Tensorflow")
    detector = MockDetector()

def get_camera():
    global camera
    if camera is None:
        camera = cv2.VideoCapture(0)
    return camera

# Map emotions to custom formatting
def map_emotion(emotion_name):
    e = emotion_name.lower()
    if e == 'neutral':
        return 'Relaxed'
    elif e in ['fear', 'disgust', 'surprise']:
        return 'Stressed'
    return e.capitalize()

# History Storage
emotion_history = []

class SessionAggregator:
    def __init__(self):
        self.buffer = []
        self.start_time = time.time()
        self.last_committed_emotion = "Relaxed" # Default

    def add_detection(self, emotions_dict):
        # emotions_dict: {'happy': 0.1, ...}
        self.buffer.append(emotions_dict)
        
        # Check if 3 seconds have passed (Faster updates for testing)
        if time.time() - self.start_time >= 3:
            return self.commit_batch()
        return None

    def commit_batch(self):
        if not self.buffer:
            self.start_time = time.time()
            return None
            
        # Aggregation Logic: Sum all scores
        totals = {}
        for entry in self.buffer:
            for emo, score in entry.items():
                # Map keys to our target groups if needed, 
                # but better to sum raw FER output (happy, sad, neutral...) then map result.
                
                # FER returns: happy, sad, angry, fear, surprise, disgust, neutral
                # We simply sum them.
                totals[emo] = totals.get(emo, 0) + score
                
        # Find dominant
        if totals:
            dominant = max(totals, key=totals.get)
            mapped_dominant = map_emotion(dominant)
            
            # Save to History
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            # Calculate average confidence of the dominant raw emotion
            avg_conf = round(totals[dominant] / len(self.buffer), 2)
            
            record = {
                "timestamp": timestamp,
                "emotion": mapped_dominant,
                "confidence": avg_conf
            }
            emotion_history.insert(0, record)  # Keep in-memory copy
            # Persist to MongoDB Atlas
            username = 'guest'
            try:
                from flask import g
                import flask
                ctx = flask.globals.request_ctx._get_current_object()
                username = ctx.session.get('user', 'guest')
            except Exception:
                pass
            save_emotion(username, mapped_dominant)
            self.last_committed_emotion = mapped_dominant
        
        # Reset
        self.buffer = []
        self.start_time = time.time()
        return self.last_committed_emotion

# Initialize Aggregator
aggregator = SessionAggregator()

# Benefits and Jokes Logic
import random
import sys
import os

# Import jokes module from Jokes folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Jokes'))
try:
    from jokes import get_programming_joke
    JOKES_AVAILABLE = True
    print("Jokes module loaded successfully!")
except ImportError as e:
    print(f"Could not load jokes module: {e}")
    JOKES_AVAILABLE = False

def get_content_data(emotion):
    """Return dict with Quick Reset, Benefits, and Joke status."""
    emotion = emotion.lower()
    
    data = {
        "quick_reset": "",
        "benefit": "",
        "joke_allowed": False
    }

    if emotion == 'sad':
        data["quick_reset"] = "Take one slow breath in… and a longer breath out. Now relax your shoulders and let your face soften for a moment."
        data["benefit"] = "This helps reduce emotional heaviness and gives your brain a small feeling of relief. It can gently lift your mood without ignoring what you’re feeling."
        data["joke_allowed"] = True # Mild/Moderate
        
    elif emotion == 'stressed':
        data["quick_reset"] = "Inhale slowly for 4 seconds… now exhale for 6 seconds. Repeat once and drop your shoulders as you breathe out."
        data["benefit"] = "This helps your body calm down quickly so your thoughts stop feeling crowded. It reduces mental pressure and makes it easier to focus on the next step."
        data["joke_allowed"] = False # Assume moderate/high for safety
        
    elif emotion == 'angry':
        data["quick_reset"] = "Breathe out slowly like you’re cooling hot tea. Unclench your jaw and press your feet into the floor for a few seconds."
        data["benefit"] = "This lowers the intensity of anger so you feel more control over your reactions. It helps prevent impulsive responses and makes it easier to think clearly."
        data["joke_allowed"] = False
        
    elif emotion == 'anxious' or emotion == 'fear':
        data["quick_reset"] = "Look around and name 3 things you can see. Now take one slow breath out longer than your breath in."
        data["benefit"] = "This brings your mind back to the present and reduces panic signals in your body. It helps restore a small sense of safety and control."
        data["joke_allowed"] = False
        
    elif emotion == 'disgust':
        data["quick_reset"] = "Take one slow breath and shift your focus to something neutral on the screen. Let your eyes relax and reset."
        data["benefit"] = "This gives your brain a quick reset and reduces the intensity of discomfort. It helps you return to a cleaner, calmer emotional state."
        data["joke_allowed"] = True # Optional
        
    elif emotion == 'neutral' or emotion == 'relaxed':
        data["quick_reset"] = "Take one calm breath in and out, and sit up slightly straighter. Let’s reset your focus."
        data["benefit"] = "This keeps your mood stable while boosting motivation and attention. It helps you stay productive without forcing any emotional shift."
        data["joke_allowed"] = True
        
    elif emotion == 'happy':
        data["quick_reset"] = "Take a confident breath in, smile slightly, and hold that energy for a moment."
        data["benefit"] = "This reinforces your positive mood and helps you keep momentum. It boosts confidence and makes it easier to carry the good energy forward."
        data["joke_allowed"] = True
        
    return data

def get_joke():
    """Return a joke — from pyjokes if available, else fallback."""
    if JOKES_AVAILABLE:
        return get_programming_joke()
    # Fallback jokes if pyjokes isn't installed
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Parallel lines have so much in common. It's a shame they'll never meet.",
        "Why don't scientists trust atoms? Because they make up everything!",
        "My fake plants died because I did not pretend to water them."
    ]
    return random.choice(jokes)

# Global state for current text to ensure it stays stable
current_text_state = {
    "emotion": None,
    "quick_reset": "",
    "benefit": "",
    "joke": None
}

def update_text_state(emotion):
    """Update text content only when emotion changes."""
    global current_text_state
    
    # Check if emotion changed or if it's the first time
    if emotion != current_text_state['emotion']:
        content = get_content_data(emotion)
        
        current_text_state['emotion'] = emotion
        current_text_state['quick_reset'] = content['quick_reset']
        current_text_state['benefit'] = content['benefit']
        
        # Determine Joke
        if content['joke_allowed']:
            current_text_state['joke'] = get_joke()
        else:
            current_text_state['joke'] = None
    
    return current_text_state

def gen_frames():
    cam = get_camera()
    frame_count = 0
    global latest_emotion_data
    
    while True:
        success, frame = cam.read()
        if not success:
            break
        else:
            # Mirror the frame (selfie view)
            frame = cv2.flip(frame, 1)
            
            # Emotion Detection Logic (Every 5th frame to save resources)
            frame_count += 1
            if frame_count % 5 == 0:
                # Detect emotions
                analysis = detector.detect_emotions(frame)
                if analysis:
                    top_face = analysis[0]
                    emotions = top_face['emotions']
                    
                    # Feed to Aggregator
                    committed_result = aggregator.add_detection(emotions)
                    
                    # Lock result
                    display_emotion = aggregator.last_committed_emotion
                    
                    # Update Text State (Stable)
                    text_data = update_text_state(display_emotion)
                    
                    # Update global state
                    latest_emotion_data = {
                        "dominant_emotion": display_emotion,
                        "emotions": emotions,
                        "quick_reset": text_data['quick_reset'],
                        "benefits": text_data['benefit'],
                        "joke": text_data['joke']
                    }
                    
                    # Optional: Draw box on frame
                    (x, y, w, h) = top_face['box']
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (79, 70, 229), 2)
                    cv2.putText(frame, display_emotion, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (79, 70, 229), 2)
            
            # Encode frame
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def root():
    # Redirect to login by default
    return redirect(url_for('login'))

@app.route('/emotion_status')
def emotion_status():
    # Inject User Name here
    user_name = session.get('user', 'Friend') # Default to Friend if not logged in
    data = latest_emotion_data.copy()
    data['user_name'] = user_name
    return jsonify(data)

@app.route('/get_joke')
def get_joke_endpoint():
    """Return a fresh joke on demand."""
    return jsonify({"joke": get_joke()})

@app.route('/get_music')
def get_music():
    """Return 3 song recommendations based on ?emotion= query param."""
    emotion = request.args.get('emotion', 'neutral')
    songs = get_song_recommendation(emotion, count=3)
    return jsonify({"emotion": emotion, "songs": songs})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get username from form
        username = request.form.get('username')
        if username:
            session['user'] = username
        else:
            session['user'] = 'Demo User'
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get username from form
        username = request.form.get('username')
        if username:
            session['user'] = username
        else:
            session['user'] = 'New User'
        return redirect(url_for('home'))
    return redirect(url_for('login')) 

@app.route('/app')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    username = session['user']

    # ── Pull data from MongoDB (falls back to in-memory if DB unavailable) ──
    counts      = get_user_counts(username)
    history     = get_user_history(username, limit=50)
    mood_scores = get_mood_scores(username, limit=20)

    # Fallback: if MongoDB returned nothing, use in-memory emotion_history
    if not history:
        counts = {"Happy": 0, "Sad": 0, "Angry": 0, "Relaxed": 0, "Stressed": 0}
        for record in emotion_history:
            emo = record['emotion']
            if emo in counts:
                counts[emo] += 1
        score_map = {'Happy': 100, 'Relaxed': 80, 'Neutral': 60, 'Stressed': 40, 'Sad': 20, 'Angry': 0}
        history     = emotion_history[:50]
        mood_scores = [score_map.get(r['emotion'], 50) for r in reversed(history[:20])]

    return render_template('dashboard.html', history=history, counts=counts, mood_scores=mood_scores)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        if camera:
            camera.release()
