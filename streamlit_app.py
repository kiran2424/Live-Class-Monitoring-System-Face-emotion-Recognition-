import os
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import load_model
import streamlit as st
from tensorflow import keras
from tensorflow.keras.utils import img_to_array
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase, RTCConfiguration, VideoProcessorBase, WebRtcMode

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# Define the emotions.
emotion_labels = ['Angry','Disgust','Fear','Happy','Neutral', 'Sad', 'Surprise']

# Load model.
classifier = load_model('model.h5')

# load weights into new model
classifier.load_weights("model_weights.h5")

# Load face using OpenCV
try:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
except Exception:
    st.write("Error loading cascade classifiers")

class VideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        #image gray
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            image=img_gray, scaleFactor=1.3, minNeighbors=5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img=img, pt1=(x, y), pt2=(
                x + w, y + h), color=(0, 255, 255), thickness=2)
            roi_gray = img_gray[y:y + h, x:x + w]
            roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)
            if np.sum([roi_gray]) != 0:
                roi = roi_gray.astype('float') / 255.0
                roi = img_to_array(roi)
                roi = np.expand_dims(roi, axis=0)
                prediction = classifier.predict(roi)[0]
                maxindex = int(np.argmax(prediction))
                finalout = emotion_labels[maxindex]
                output = str(finalout)
            label_position = (x, y-10)
            cv2.putText(img, output, label_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return img

def main():
    # Face Analysis Application #
    st.title("Real Time Face Emotion Detection Application")
    activiteis = ["Home", "Live Face Emotion Detection"]
    choice = st.sidebar.selectbox("Select Activity", activiteis)

    # Homepage.
    if choice == "Home":
        html_temp_home1 = """<div style="background-color:#FC4C02;padding:0.5px">
                             <h4 style="color:white;text-align:center;">
                            Start Your Real Time Face Emotion Detection.
                             </h4>
                             </div>
                             </br>"""

        st.markdown(html_temp_home1, unsafe_allow_html=True)
        st.write("""
	* You don’t always need words, often your face says it all! Facial expression is a picture of one’s mind. 
	* Sometimes we laugh, sometimes we cry, sometimes we get angry, and sometimes get scared....
	* From unlocking our phones to accessing personal documents on our computers, facial recognition technology has become a part in our day-to-day lives. 
	* But ever wondered; whether the computer that we give all this attention to is even capable of recognizing these emotions?
        
        Let's find out...
        1. Click the dropdown list in the top left corner and select Live Face Emotion Detection.
        2. This takes you to a page which will tell if it recognizes your emotions.
                 """)

    # Live Face Emotion Detection.
    elif choice == "Live Face Emotion Detection":
        st.header("Webcam Live Feed")
        st.subheader('''
        Welcome to the other side of the SCREEN!!!
        * Get ready with all the emotions you can express. 
        ''')
        st.write("1. Click Start to open your camera and give permission by clicking 'Allow' for prediction")
        st.write("2. This will predict your emotion.")
        st.write("3. When you done, click stop to end.")
        webrtc_streamer(key="example", video_processor_factory=VideoTransformer, rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={
            "video": True,
            "audio": True}
        )

    else:
        pass

if __name__ == "__main__":
    main()
