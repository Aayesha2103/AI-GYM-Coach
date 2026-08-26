import streamlit as st
import os
import time
import pandas as pd

from services.auth.login_wall import render_login_wall
from services.state.session_defaults import initial_session_defaults
from services.config.workout_config import EXERCISE_OPTIONS
from services.ui.style_loader import (
    load_css,
    inject_local_font,
    inject_webrtc_styles
)
from services.persistence.exercise_repository import init_db
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from services.vision.exercise_video_processor import VideoProcessorClass
from services.tracking.metrics import sync_metrics_update
from services.persistence.exercise_repository import get_users_exercises
from groq import Groq
from services.coaching.llm import LLMCoach
from services.coaching.tts import TextToSpeech
from services.coaching.voice_pipeline import VoicePipeline, autoplay_audio


def main():

    st.set_page_config(
        page_icon="🏋️‍♀️",
        page_title="AI Real-time GYM Coach",
        initial_sidebar_state="expanded",
        layout="centered"
    )

    load_css(
        os.path.join(os.getcwd(), "static", "style.css")
    )

    inject_local_font(
        os.path.join(os.getcwd(), "static", "AdobeClean.otf"),
        "AdobeClean"
    )

    init_db()

    if not render_login_wall():
        return

    initial_session_defaults()

    # ============================================================
    # GROQ INITIALIZATION + DEPLOYMENT DIAGNOSTIC
    # ============================================================

    if "voice_pipeline" not in st.session_state:

        try:

            # ----------------------------------------------------
            # 1. Get Groq API key
            # ----------------------------------------------------

            api_key = os.environ.get("GROQ_API_KEY", "")

            if api_key:

                st.info(
                    "Groq key loaded from environment variable."
                )

            elif (
                hasattr(st, "secrets")
                and "GROQ_API_KEY" in st.secrets
            ):

                api_key = st.secrets["GROQ_API_KEY"]

                st.info(
                    "Groq key loaded from Streamlit secrets."
                )

            else:

                st.error(
                    "GROQ_API_KEY was not found."
                )

                st.stop()

            # ----------------------------------------------------
            # 2. Create Groq client
            # ----------------------------------------------------

            groq_client = Groq(
                api_key=api_key
            )

            # ----------------------------------------------------
            # 3. Test Groq model access
            # ----------------------------------------------------

            try:

                test_model = groq_client.models.retrieve(
                    "llama-3.1-8b-instant"
                )

                st.success(
                    f"Groq connection OK: {test_model.id}"
                )

            except Exception as e:

                st.error(
                    f"Groq connection failed: "
                    f"{type(e).__name__}: {e}"
                )

                st.stop()

            # ----------------------------------------------------
            # 4. Create LLM coach
            # ----------------------------------------------------

            llm_coach = LLMCoach(
                groq_client
            )

            # ----------------------------------------------------
            # 5. Create text-to-speech
            # ----------------------------------------------------

            tts = TextToSpeech()

            # ----------------------------------------------------
            # 6. Create voice pipeline
            # ----------------------------------------------------

            st.session_state.voice_pipeline = VoicePipeline(
                llm_coach,
                tts
            )

        except Exception as e:

            st.error(
                f"Voice pipeline initialization failed: "
                f"{type(e).__name__}: {e}"
            )

            st.session_state.voice_pipeline = None

    # ============================================================
    # WORKOUT STATE
    # ============================================================

    workout_started = st.session_state.get(
        "workout_started",
        False
    )

    # ============================================================
    # SIDEBAR
    # ============================================================

    with st.sidebar:

        st.title("🏋️‍♂️ Apna AI Coach")

        if st.session_state.username:
            st.caption(
                f"👤 Login as {st.session_state.username}"
            )

        st.divider()

        st.subheader("Workout Plan")

        # --------------------------------------------------------
        # Workout has NOT started
        # --------------------------------------------------------

        if not workout_started:

            plan_exercise = st.selectbox(
                "Exercise",
                options=EXERCISE_OPTIONS,
                key="plan_exercise"
            )

            plan_sets = st.number_input(
                "Sets",
                min_value=0,
                max_value=50,
                key="plan_sets",
                step=1
            )

            plan_reps = st.number_input(
                "Reps per Set",
                min_value=0,
                max_value=50,
                key="plan_reps",
                step=1
            )

            st.markdown("")

            start_session_button = st.button(
                "Start Workout",
                width="stretch",
                key="start_session_button"
            )

            if start_session_button:

                st.session_state.exercise_type = plan_exercise
                st.session_state.target_sets = int(plan_sets)
                st.session_state.reps_per_set = int(plan_reps)

                st.session_state.reps = 0

                st.session_state.workout_started = True

                st.session_state.set_cycle_started_at = time.time()

                st.session_state.last_saved_sets_completed = 0

                # ------------------------------------------------
                # Start AI coaching
                # ------------------------------------------------

                if st.session_state.voice_pipeline:

                    result = (
                        st.session_state.voice_pipeline.process_event(
                            event="workout_started",
                            exercise=plan_exercise,
                            metrics={}
                        )
                    )

                    if result:

                        (
                            st.session_state.audio_to_play,
                            st.session_state.coach_feedback
                        ) = result

                st.session_state.last_notified_sets_completed = 0

                st.session_state.last_notified_workout_complete = False

                st.rerun()

        # --------------------------------------------------------
        # Workout HAS started
        # --------------------------------------------------------

        else:

            exercise = st.session_state.get(
                "exercise_type"
            )

            sets = st.session_state.get(
                "target_sets"
            )

            reps = st.session_state.get(
                "reps_per_set"
            )

            st.info(
                f"**{exercise}** -- {sets} Sets / {reps} Reps"
            )

            end_session_button = st.button(
                "End Workout",
                key="end_session_button",
                width="stretch"
            )

            if end_session_button:

                st.session_state.workout_started = False

                # ------------------------------------------------
                # Workout completed AI feedback
                # ------------------------------------------------

                if st.session_state.voice_pipeline:

                    result = (
                        st.session_state.voice_pipeline.process_event(
                            event="workout_completed",
                            exercise=exercise,
                            metrics={}
                        )
                    )

                    if result:

                        (
                            st.session_state.audio_to_play,
                            st.session_state.coach_feedback
                        ) = result

                st.rerun()

        # ========================================================
        # WORKOUT PROGRESS
        # ========================================================

        if workout_started:

            st.divider()

            exercise = st.session_state.get(
                "exercise_type"
            )

            total_reps = st.session_state.get(
                "reps"
            )

            current_set_reps = st.session_state.get(
                "current_set_reps"
            )

            reps_per_set = st.session_state.get(
                "reps_per_set"
            )

            sets_completed = st.session_state.get(
                "sets_completed"
            )

            target_sets = st.session_state.get(
                "target_sets"
            )

            st.subheader("Progress")

            st.metric(
                "Total Reps",
                f"{total_reps}"
            )

            st.metric(
                "Current Set Reps",
                f"{current_set_reps} / {reps_per_set}"
            )

            st.metric(
                "Sets Completed",
                f"{sets_completed} / {target_sets}"
            )

            st.divider()

            # ----------------------------------------------------
            # Squats
            # ----------------------------------------------------

            if exercise == "Squats":

                st.subheader("Squat Metrics")

                st.metric(
                    "Knee Angle",
                    f"{st.session_state.knee_angle}°"
                )

                st.metric(
                    "Back Angle",
                    f"{st.session_state.back_angle}°"
                )

                st.metric(
                    "Depth Status",
                    st.session_state.depth_status
                )

            # ----------------------------------------------------
            # Push-ups
            # ----------------------------------------------------

            elif exercise == "Push-ups":

                st.subheader("Push-up Metrics")

                st.metric(
                    "Elbow Angle",
                    f"{st.session_state.elbow_angle}°"
                )

                st.metric(
                    "Body Alignment",
                    st.session_state.body_alignment
                )

                st.metric(
                    "Hip Position",
                    st.session_state.hip_status
                )

            # ----------------------------------------------------
            # Biceps Curls
            # ----------------------------------------------------

            elif exercise == "Biceps Curls (Dumbbell)":

                st.subheader("Curl Metrics")

                st.metric(
                    "Elbow Angle",
                    f"{st.session_state.elbow_angle}°"
                )

                st.metric(
                    "Shoulder Stability",
                    st.session_state.shoulder_status
                )

                st.metric(
                    "Swing Detection",
                    st.session_state.swing_status
                )

            # ----------------------------------------------------
            # Shoulder Press
            # ----------------------------------------------------

            elif exercise == "Shoulder Press":

                st.subheader("Shoulder Press Metrics")

                st.metric(
                    "Elbow Angle",
                    f"{st.session_state.elbow_angle}°"
                )

                st.metric(
                    "Arm Extension",
                    st.session_state.extension_status
                )

                st.metric(
                    "Back Arch",
                    st.session_state.back_arch_status
                )

            # ----------------------------------------------------
            # Lunges
            # ----------------------------------------------------

            elif exercise == "Lunges":

                st.subheader("Lunge Metrics")

                st.metric(
                    "Front Knee Angle",
                    f"{st.session_state.front_knee_angle}°"
                )

                st.metric(
                    "Torso Angle",
                    f"{st.session_state.torso_angle}°"
                )

                st.metric(
                    "Balance Status",
                    st.session_state.balance_status
                )

    # ============================================================
    # MAIN PAGE
    # ============================================================

    st.title("AI Real-time GYM Coach")

    st.markdown(
        "#### Real-time pose detection with proactive AI voice coaching"
    )

    # ============================================================
    # AUDIO
    # ============================================================

    if st.session_state.get("audio_to_play"):

        autoplay_audio(
            st.session_state.audio_to_play
        )

    # ============================================================
    # COACH FEEDBACK
    # ============================================================

    if st.session_state.get("coach_feedback"):

        st.markdown("")

        st.success(
            f"🤖 **Coach:** "
            f"{st.session_state.coach_feedback}"
        )

    # ============================================================
    # CAMERA / WORKOUT AREA
    # ============================================================

    if not workout_started:

        st.markdown(
            """
            <div style="
                border: 10px dashed #444;
                border-radius: 0px;
                padding: 48px 32px;
                text-align: center;
                color: #888;
                margin-top: 32px;
                margin-bottom: 32px;
            ">

                <h2 style="color:#ccc; margin-bottom:8px;">
                    👈 Set your workout plan
                </h2>

                <p style="font-size:1.05rem;">

                    Choose your exercise, sets and reps
                    in the sidebar,<br>

                    then click <strong>Start Workout</strong>
                    to activate the camera and AI coach.

                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        context = webrtc_streamer(

            key="exercise-analysis",

            mode=WebRtcMode.SENDRECV,

            video_processor_factory=VideoProcessorClass,

            rtc_configuration={
                "iceServers": [
                    {
                        "urls": [
                            "stun:stun.l.google.com:19302"
                        ]
                    }
                ]
            },

            media_stream_constraints={
                "video": True,
                "audio": False
            },

            async_processing=True
        )

        sync_metrics_update(context)

        if context.state.playing:

            time.sleep(0.25)

            st.rerun()

        inject_webrtc_styles()

    # ============================================================
    # WORKOUT HISTORY
    # ============================================================

    st.divider()

    st.markdown("#### Workout History")

    user_id = st.session_state.get(
        "user_id",
        0
    )

    if isinstance(user_id, int):

        history_rows = get_users_exercises(
            user_id
        )

        arr = [
            {
                "Exercise": row["exercise_name"],
                "Reps": row["reps"],
                "Sets": row["sets"],
                "Time (sec)": row["time"],
                "Date": row["created_at"]
            }

            for row in history_rows
        ]

        df = pd.DataFrame(arr)

        if not df.empty:

            df["Date"] = pd.to_datetime(
                df["Date"]
            ).dt.date

            agg_df = (
                df.groupby(
                    ["Exercise", "Date"]
                )
                .agg(
                    {
                        "Reps": "sum",
                        "Sets": "sum",
                        "Time (sec)": "sum"
                    }
                )
                .reset_index()
            )

            agg_df.index += 1

            st.table(
                agg_df,
                border="horizontal"
            )

        else:

            st.info(
                "No workout history found."
            )


if __name__ == "__main__":
    main()