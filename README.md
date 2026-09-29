# 🏋️ AI Real-time GYM Coach

> **Real-time pose detection • Rep & set tracking • Exercise form
> analysis • AI voice coaching**

AI Real-time GYM Coach is a computer-vision fitness application that
turns a webcam into an interactive personal trainer. It detects body
landmarks in real time, understands exercise movements, counts
repetitions and sets, checks exercise form, and provides AI-powered
coaching feedback.

------------------------------------------------------------------------

## ✨ Key Features

-   🎥 **Real-time pose detection** using MediaPipe Pose Landmarker
-   🔢 **Automatic rep and set counting** based on exercise movement
    stages
-   🏋️ Supports **Squats, Push-ups, Biceps Curls, Shoulder Press and
    Lunges**
-   📐 **Exercise-specific form analysis** using joint angles and pose
    landmarks
-   🗣️ **AI coaching feedback** powered by the Groq API
-   🎙️ Coaching events for form checks, completed sets, completed
    workouts, and missing poses
-   📹 **Live webcam processing** using Streamlit-WebRTC
-   📊 **Workout history and performance tracking**
-   🌐 Interactive browser-based interface built with Streamlit

------------------------------------------------------------------------

## 🛠️ Tech Stack

  Technology                       Purpose
  -------------------------------- ---------------------------------------------
  **Python**                       Core application and exercise logic
  **MediaPipe**                    Real-time human pose and landmark detection
  **OpenCV**                       Image/video processing and visualization
  **NumPy**                        Numerical and landmark calculations
  **Streamlit**                    Interactive web application
  **Streamlit-WebRTC**             Real-time webcam/video streaming
  **PyAV**                         Video frame handling
  **Groq API**                     AI-powered coaching responses
  **SQLite / Persistence Layer**   Workout and exercise history

------------------------------------------------------------------------

## 🧠 How It Works

``` text
Webcam
   ↓
Streamlit-WebRTC
   ↓
Video Frame Processing
   ↓
MediaPipe Pose Landmarker
   ↓
Body Landmarks
   ↓
Exercise Detector
   ↓
Rep / Set Counting + Form Analysis
   ↓
Workout Metrics
   ↓
Groq AI Coaching
   ↓
Real-time Feedback
```

Each exercise has its own detector. The detector uses relevant body
landmarks and movement thresholds to determine the user's current
exercise stage and increment repetitions when a complete movement is
detected.

------------------------------------------------------------------------

## 🏋️ Supported Exercises

**Squats** - Knee-angle based depth detection - Rep counting -
Back-angle monitoring

**Push-ups** - Body alignment analysis - Hip position monitoring - Rep
counting

**Biceps Curls** - Arm movement analysis - Swing detection - Rep
counting

**Shoulder Press** - Arm extension analysis - Back arch monitoring - Rep
counting

**Lunges** - Leg movement analysis - Balance monitoring - Rep counting

------------------------------------------------------------------------

## 🤖 AI Coaching

The application connects exercise events and detected metrics to the
**Groq API** to generate contextual coaching feedback.

Examples include:

-   Ongoing form checks
-   Set completion feedback
-   Workout completion feedback
-   No-pose warnings

The AI layer is therefore used alongside computer vision rather than
replacing the pose-detection system.

------------------------------------------------------------------------

## 🚀 Live Demo

### 👉 [Try AI Real-time GYM Coach](https://ai-gym-coach-aayesha.streamlit.app/)

> Allow camera access in your browser before starting a workout.

------------------------------------------------------------------------

## 📸 Project Preview

The repository also contains screenshots and a demo video showing the
application's interface and functionality.

------------------------------------------------------------------------

## 🎯 Project Focus

**Computer Vision + Generative AI + Real-time Video Processing**

This project demonstrates the integration of **pose estimation, computer
vision, real-time streaming, exercise-specific algorithms, persistent
workout tracking, and LLM-powered coaching** into a practical AI
application.

------------------------------------------------------------------------

### 👩‍💻 Built with Python

**AI Real-time GYM Coach --- Turning a webcam into an AI fitness
coach.**
