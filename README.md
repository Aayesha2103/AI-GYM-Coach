# 🏋️ AI Real-Time GYM Coach

> **Your webcam. Your workout. Your AI coach.**

An AI-powered real-time fitness coaching application that uses **computer vision, pose estimation, biomechanical analysis, LLM-based coaching, and voice feedback** to help users perform exercises with better form.

The system analyzes your body movement through a webcam, automatically counts repetitions and sets, evaluates exercise form, stores workout history, and provides real-time coaching feedback through both text and voice.

<p align="center">

**🎥 Real-Time Pose Detection · 🔢 Rep & Set Tracking · 🧠 AI Coaching · 🔊 Voice Feedback · 📊 Workout History**

</p>

---

## 🌐 Live Project

### 🚀 Landing Page

👉 **[Visit AI GYM Coach Landing Page](https://ai-gym-coach-landing-page.netlify.app/)**

### 💪 Launch the Application

👉 **[Open AI GYM Coach App](https://ai-gym-coach-aayesha.streamlit.app/)**

> Replace the two URLs above with your actual Netlify and Streamlit deployment URLs.

---

## 📌 Overview

Traditional fitness applications can tell users *what* exercise to perform, but they usually cannot watch the movement itself.

AI Real-Time GYM Coach attempts to solve this problem by turning a normal webcam into a virtual fitness coach.

The application follows this pipeline:

```text
Webcam
   ↓
WebRTC Video Stream
   ↓
OpenCV Frame Processing
   ↓
MediaPipe Pose Landmarker
   ↓
Body Landmarks
   ↓
Exercise-Specific Detector
   ↓
Joint Angles + Movement Stages
   ↓
Rep & Set Tracking
   ↓
Form Analysis
   ↓
AI Coaching
   ↓
Text + Voice Feedback
   ↓
Workout History
```

The project combines **deterministic computer-vision logic** with an **LLM coaching layer** rather than sending raw video directly to an LLM.

---

# ✨ Features

## 🎥 Real-Time Pose Detection

The application uses **MediaPipe Pose Landmarker** to detect human body landmarks from the webcam stream.

The system tracks important joints such as:

* Shoulders
* Elbows
* Hips
* Knees
* Ankles

A live skeleton is drawn over the detected body.

---

## 🔢 Automatic Rep Counting

The application automatically detects exercise movement phases and counts completed repetitions.

Instead of simply counting frames, the detectors use a **state-based movement system**.

For example:

```text
DOWN
  ↓
Movement reaches threshold
  ↓
UP
  ↓
REP + 1
```

This prevents the same movement from being counted multiple times.

---

## 📋 Automatic Set Tracking

The application calculates sets from the total number of repetitions.

```python
sets_completed = reps // reps_per_set
current_set_reps = reps % reps_per_set
```

For example:

```text
Target = 10 reps/set

10 reps → 1 set
20 reps → 2 sets
25 reps → 2 sets + 5 reps
30 reps → 3 sets
```

Completed sets are persisted to the SQLite database.

---

# 🏋️ Supported Exercises

| Exercise       | Rep Tracking | Form Analysis |
| -------------- | -----------: | ------------: |
| Squats         |            ✅ |             ✅ |
| Push-ups       |            ✅ |             ✅ |
| Biceps Curls   |            ✅ |             ✅ |
| Shoulder Press |            ✅ |             ✅ |
| Lunges         |            ✅ |             ✅ |

---

# 🧠 Exercise Analysis

The application does not rely only on the raw position of a landmark.

Instead, it calculates **joint angles** from multiple body landmarks.

For example, a squat uses:

```text
Hip
  \
   Knee
     \
     Ankle
```

The angle around the knee is calculated using vectors.

```text
BA = A - B
BC = C - B

cos(θ) = (BA · BC) / (|BA| × |BC|)

θ = arccos(cos(θ))
```

These angles are then used by the exercise detectors to determine movement stages and form conditions.

---

# 🦵 Exercise Detectors

Each exercise has its own detector class.

```text
detectors/
├── squat.py
├── pushup.py
├── biceps_curl.py
├── shoulder_press.py
└── lunges.py
```

All detectors inherit from:

```text
core/base_exercise.py
```

This provides reusable functionality such as:

* Landmark access
* Point conversion
* Joint-angle calculation
* Shared exercise behavior

---

# 🏋️ Squat Detection Example

The squat detector uses knee angles.

Simplified logic:

```text
Knee angle < 100°
        ↓
     DOWN

Knee angle >= 160°
        ↓
     UP

DOWN → UP
        ↓
    REP + 1
```

The detector also calculates:

* Knee angle
* Back angle
* Squat depth

---

# 💪 Push-Up Detection

Push-up analysis considers:

* Elbow angle
* Body alignment
* Hip position

This allows the system to detect issues such as incorrect body alignment or poor hip positioning.

---

# 💪 Biceps Curl Detection

The curl detector analyzes:

* Elbow angle
* Shoulder stability
* Swinging movement

The goal is to distinguish a controlled curl from excessive body movement.

---

# 🏋️ Shoulder Press Detection

The shoulder press detector analyzes:

* Elbow extension
* Arm position
* Back arch

This helps identify excessive back arching or insufficient extension.

---

# 🦵 Lunge Detection

The lunge detector analyzes:

* Front knee angle
* Torso angle
* Balance

---

# 🤖 AI Coaching

The project contains an LLM coaching layer powered by **Groq**.

Current model:

```text
openai/gpt-oss-20b
```

The important architectural decision is that the LLM does **not** process the raw webcam video.

Instead:

```text
Camera
   ↓
MediaPipe
   ↓
Exercise Detector
   ↓
Structured Metrics
   ↓
Form Issue
   ↓
LLM
```

For example:

```text
Knee angle → 125°
Depth status → TOO HIGH
```

can become a structured coaching issue such as:

```text
Squat is too shallow.
```

The LLM then converts that into a short natural coaching instruction.

---

# 🔊 Voice Coaching

The project uses **gTTS (Google Text-to-Speech)** to convert AI-generated coaching text into speech.

```text
Exercise Metrics
      ↓
Form Issue
      ↓
Groq LLM
      ↓
Coaching Text
      ↓
gTTS
      ↓
MP3 Audio
      ↓
Streamlit Autoplay
```

This allows the application to provide hands-free coaching while the user is exercising.

---

# 🎙️ Coaching Events

The coaching pipeline handles events such as:

* Workout started
* Set completed
* Workout completed
* No pose detected
* Ongoing form check

The system also uses throttling for ongoing coaching so the LLM does not generate feedback continuously on every video frame.

---

# 🗄️ Workout History

Workout data is stored using **SQLite**.

The database tracks information such as:

* User
* Exercise
* Repetitions
* Sets
* Workout duration
* Timestamp

Pandas is then used to aggregate workout information for the history section of the application.

---

# 🔐 Authentication

The application currently uses a lightweight username-based login system.

The user's information is stored in Streamlit session state during the application session.

> **Production note:** This is a prototype authentication system. A production deployment should use a proper authentication provider, secure password handling, authorization and stronger session management.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────┐
                         │   User Webcam    │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ streamlit-webrtc │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │      OpenCV      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     MediaPipe    │
                         │  Pose Landmarker │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Exercise Detector│
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
             Rep / Set Tracking            Form Analysis
                    │                           │
                    ▼                           ▼
              SQLite Database             Coaching Event
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │ Groq LLM    │
                                         └──────┬──────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │    gTTS     │
                                         └──────┬──────┘
                                                │
                                                ▼
                                         Voice Feedback
```

---

# 🛠️ Technology Stack

| Category              | Technology         |
| --------------------- | ------------------ |
| Programming Language  | Python             |
| Web Framework         | Streamlit          |
| Real-Time Video       | streamlit-webrtc   |
| Computer Vision       | OpenCV             |
| Pose Estimation       | MediaPipe          |
| Numerical Processing  | NumPy              |
| Data Analysis         | Pandas             |
| LLM                   | Groq API           |
| LLM Model             | openai/gpt-oss-20b |
| Text-to-Speech        | gTTS               |
| Database              | SQLite             |
| Environment Variables | python-dotenv      |
| Landing Page          | HTML5 + CSS3       |
| Application Hosting   | Streamlit Cloud    |
| Landing Page Hosting  | Netlify            |

---

# 📁 Project Structure

```text
AI-GYM-Coach/
│
├── main.py
│
├── core/
│   └── base_exercise.py
│
├── detectors/
│   ├── squat.py
│   ├── pushup.py
│   ├── biceps_curl.py
│   ├── shoulder_press.py
│   └── lunges.py
│
├── services/
│   │
│   ├── auth/
│   │   └── login_wall.py
│   │
│   ├── coaching/
│   │   ├── llm.py
│   │   ├── voice_pipeline.py
│   │   └── tts.py
│   │
│   ├── config/
│   │   └── workout_config.py
│   │
│   ├── persistence/
│   │   └── exercise_repository.py
│   │
│   ├── state/
│   │   └── session_defaults.py
│   │
│   ├── tracking/
│   │   └── metrics.py
│   │
│   ├── ui/
│   │
│   └── vision/
│       └── exercise_video_processor.py
│
├── ml_models/
│   └── pose_landmarker_full.task
│
├── static/
│
├── .streamlit/
│
├── requirements.txt
├── packages.txt
└── README.md
```

---

# 🔄 Data Flow

The most important part of the project is the real-time data flow.

### Step 1 — Camera Input

The browser provides webcam frames.

### Step 2 — WebRTC

`streamlit-webrtc` sends the frames to the Python video processor.

### Step 3 — Frame Processing

OpenCV flips and prepares the frame.

### Step 4 — Pose Detection

MediaPipe detects body landmarks.

### Step 5 — Exercise Selection

The selected exercise determines which detector processes the landmarks.

### Step 6 — Biomechanical Analysis

The detector calculates relevant angles.

### Step 7 — Movement Detection

The detector determines whether the user is moving through the correct exercise stages.

### Step 8 — Rep Counting

A completed movement cycle increments the repetition counter.

### Step 9 — Set Calculation

The tracking layer converts repetitions into completed sets.

### Step 10 — Form Analysis

Exercise-specific rules identify potential form issues.

### Step 11 — AI Coaching

The structured issue is sent to the Groq LLM.

### Step 12 — Voice

gTTS converts the generated coaching text into speech.

### Step 13 — Persistence

Completed workout information is stored in SQLite.

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/Aayesha2103/AI-GYM-Coach.git

cd AI-GYM-Coach
```

---

## 2. Create a virtual environment

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Groq API Key

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Never commit your `.env` file.

Make sure it is included in `.gitignore`.

---

## 5. Run the application

```bash
streamlit run main.py
```

The application will open in your browser.

---

# 🔑 Environment Variables

| Variable       | Purpose                     |
| -------------- | --------------------------- |
| `GROQ_API_KEY` | Authentication for Groq API |

For Streamlit Cloud, the API key should be added through **Secrets** rather than committed to the repository.

---

# 🎯 How Rep Counting Works

The project uses a simple state machine rather than counting every detected frame.

Example:

```text
             ┌───────────┐
             │           │
             ▼           │
          ┌──────┐       │
          │ DOWN │───────┘
          └──┬───┘
             │
             │ threshold reached
             ▼
          ┌──────┐
          │  UP  │
          └──┬───┘
             │
             │
             ▼
          REP + 1
```

This approach helps prevent a single exercise movement from being counted repeatedly while the user remains in the same position.

---

# ⚡ Performance Considerations

Real-time computer vision is computationally expensive.

The application therefore separates responsibilities:

```text
Video Processing
       ≠
Streamlit UI
       ≠
LLM Requests
       ≠
Database Operations
```

The video processor continuously handles frames while the application periodically synchronizes the latest metrics.

A thread lock protects the shared latest-metrics state.

LLM coaching is also throttled to avoid unnecessary API calls.

---

# 🚀 Deployment

The project uses two separate deployments.

### Landing Page

```text
HTML + CSS
      ↓
GitHub
      ↓
Netlify
```

### Application

```text
Python + Streamlit
        ↓
GitHub
        ↓
Streamlit Cloud
```

The landing page's **Get Started** button connects both systems:

```text
Landing Page
     ↓
Get Started
     ↓
Streamlit Application
```

---

# 🌐 Landing Page Repository

The landing page is maintained separately:

👉 **[AI GYM Coach Landing Page](https://github.com/Aayesha2103/ai-gym-coach-landing_page)**

It contains:

```text
ai-gym-coach-landing_page/
│
├── index.html
├── style.css
│
└── assets/
    ├── images/
    │   ├── screenshot1.png
    │   ├── screenshot2.png
    │   ├── screenshot3.png
    │   ├── screenshot4.png
    │   └── screenshot5.png
    │
    └── video/
        └── demo.mp4
```

---

# 📸 Project Preview

Add your screenshots here:

```markdown
![Real-Time Pose Detection](assets/images/screenshot1.png)

![Exercise Tracking](assets/images/screenshot2.png)

![AI Coaching](assets/images/screenshot3.png)

![Workout Dashboard](assets/images/screenshot4.png)

![Workout History](assets/images/screenshot5.png)
```

---

# 🎥 Demo

The landing page contains the project demonstration video.

```text
assets/video/demo.mp4
```

You can also add a GIF or hosted video preview to the README if desired.

---

# 🧠 What Makes This Project Different?

The project combines several technologies into one real-time pipeline:

```text
Computer Vision
      +
Biomechanical Analysis
      +
Rule-Based Exercise Detection
      +
LLM
      +
Text-to-Speech
      +
Database
      =
AI Real-Time GYM Coach
```

The important architectural choice is the separation between **vision and language**.

MediaPipe and the exercise detectors determine *what is happening physically*.

The LLM determines *how to communicate the coaching feedback naturally*.

---

# ⚠️ Current Limitations

The current system is a prototype and has several limitations:

* Pose accuracy depends on camera position and lighting.
* Occlusion can reduce landmark visibility.
* Angle thresholds may need calibration for different users.
* Rule-based detection is less flexible than a trained exercise-classification model.
* SQLite is better suited to a prototype than a large multi-user production system.
* Username-based login is not production-grade authentication.
* LLM responses introduce network latency.
* gTTS depends on an external service.
* Some exercises are easier to analyze from a side view than a front view.

---

# 🔮 Future Improvements

Potential improvements include:

### Computer Vision

* Temporal landmark smoothing
* Personalized angle calibration
* 3D pose analysis
* Better camera-view detection
* More exercises
* More sophisticated form scoring
* Learned exercise classification

### AI

* More personalized coaching
* Workout-plan generation
* Long-term progress analysis
* Conversational coach
* Multilingual voice coaching
* Personalized feedback based on workout history

### Backend

* PostgreSQL
* Production authentication
* User profiles
* Cloud database
* Scalable session management

### Product

* Mobile application
* Progress graphs
* Workout goals
* Achievements
* Streak tracking
* Personalized training plans

---

# 🧪 Example Coaching Flow

A user performs a squat.

The system detects:

```text
Knee Angle: 124°
Depth Status: TOO HIGH
```

The detector produces a structured issue.

The coaching pipeline sends that information to the LLM.

The LLM generates a short instruction such as:

```text
Go lower on the next rep and reach proper squat depth.
```

gTTS converts it to speech.

The user hears the correction while continuing the workout.

---

# 👨‍💻 Technical Highlights

This project demonstrates practical experience with:

* Python application architecture
* Object-oriented programming
* Computer vision
* Pose estimation
* Biomechanical mathematics
* Real-time video processing
* State machines
* Streamlit
* WebRTC
* REST-style API integration
* LLM integration
* Prompt engineering
* Text-to-speech
* SQLite
* Pandas
* Environment variables
* Git/GitHub
* Cloud deployment
* Static web development

---

# 📚 Key Concepts Demonstrated

### Computer Vision

Using visual information from a webcam to extract meaningful information about a person's movement.

### Pose Estimation

Converting a human image into structured body landmarks.

### Biomechanics

Using mathematical relationships between body joints to analyze movement.

### State Machines

Representing exercise phases such as:

```text
UP → DOWN → UP
```

to identify completed repetitions.

### LLM Integration

Using an LLM to convert structured exercise information into natural coaching language.

### Real-Time Systems

Processing continuously changing data while maintaining synchronization between video processing, UI state, AI requests and persistence.

---

# 👩‍🏫 Explaining the Project in an Interview

### 30-Second Version

> “AI Real-Time GYM Coach is a computer-vision-based virtual fitness coach. It uses a webcam with WebRTC, MediaPipe for pose estimation, and OpenCV for real-time frame processing. I built separate exercise detectors that calculate joint angles and use movement-state rules to count repetitions and analyze form for five exercises. The resulting metrics are passed to a coaching pipeline, where Groq's LLM generates short feedback and gTTS converts it into voice. Workout data is stored in SQLite and displayed through Streamlit. I also built a separate HTML/CSS landing page deployed through Netlify.”

---

# 🎤 5-Minute Explanation

### 1. Problem

Traditional workout applications cannot actually watch whether the user is performing an exercise correctly.

### 2. Solution

This project turns a webcam into a virtual personal trainer.

### 3. Computer Vision

WebRTC captures the camera stream.

OpenCV processes the frames.

MediaPipe detects body landmarks.

### 4. Exercise Analysis

Custom detector classes calculate joint angles and movement stages.

These determine:

* Repetitions
* Sets
* Exercise depth
* Alignment
* Balance
* Other form metrics

### 5. AI Coaching

The structured form information is passed to Groq.

The LLM converts it into a short natural coaching instruction.

gTTS converts that instruction into audio.

### 6. Data

SQLite stores workout information.

Pandas is used to aggregate the workout history.

### 7. Deployment

The application is deployed through Streamlit, while the static landing page is hosted separately.

---

# ❓ Common Interview Questions

### Q: Where is the AI in your project?

**Answer:**

> “There are two important intelligent components. MediaPipe uses machine learning for pose estimation. The exercise analysis itself is primarily deterministic, using joint angles, thresholds and movement states. The second AI component is the Groq LLM, which converts structured form issues into natural coaching feedback.”

---

### Q: Why didn't you send the camera video directly to the LLM?

**Answer:**

> “Real-time raw video would be unnecessarily expensive and would introduce additional latency. Instead, I extract structured pose information first. The LLM only receives the relevant exercise metrics and form issue.”

---

### Q: How do you count repetitions?

**Answer:**

> “I use a state machine. For example, in a squat the detector enters a down state when the knee angle crosses the lower threshold. When the angle returns above the upper threshold and the previous state was down, I increment the repetition.”

---

### Q: How do you calculate sets?

**Answer:**

> “Sets are calculated from total repetitions using integer division, while the remainder gives the repetitions in the current set.”

```python
sets_completed = reps // reps_per_set
current_set_reps = reps % reps_per_set
```

---

### Q: What happens when the camera cannot detect the person?

**Answer:**

> “The processor detects that no pose landmarks are available, displays a no-pose warning, and the coaching pipeline can provide a repositioning instruction.”

---

### Q: What database did you use?

**Answer:**

> “SQLite. It is lightweight and suitable for the current prototype. For a production multi-user system, I would migrate to PostgreSQL or another server database.”

---

### Q: What was the biggest technical challenge?

**Answer:**

> “Real-time synchronization was one of the biggest challenges. Video processing runs continuously while Streamlit reruns the application. I had to separate the video processor from the UI state and use a thread-safe latest-metrics store so the UI could consume the latest result without corrupting shared state.”

---

### Q: What would you improve?

**Answer:**

> “I would add temporal smoothing and personalized calibration to make the form detection more robust, replace the prototype authentication system with proper authentication, move to a production database, improve the exercise models, and add automated testing.”

---

# 📜 License

This project is currently intended as a personal/academic project.

Add an explicit license here if you decide to publish the project under a specific open-source license.

---

# 👤 Author

**Aayesha Singh**

AI / Machine Learning · Computer Vision · Python · Generative AI

### Project Links

* 🚀 [Live Landing Page](https://ai-gym-coach-landing-page.netlify.app/)
* 💪 [Live AI GYM Coach](https://ai-gym-coach-aayesha.streamlit.app/)
* 💻 [Main GitHub Repository](https://github.com/Aayesha2103/AI-GYM-Coach)
* 🌐 [Landing Page Repository](https://github.com/Aayesha2103/ai-gym-coach-landing_page)

---

<p align="center">

### 🏋️ Train Smarter. Move Better. Get Real-Time Coaching.

</p>
