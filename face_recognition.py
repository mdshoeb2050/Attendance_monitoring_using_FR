import face_recognition 
import cv2
import numpy as np
import os
import pandas as pd
from datetime import date
import re

video_capture = cv2.VideoCapture(0)

face_locations = []

face_names = []

present_student_list = set()

known_face_encodings = []

known_face_names = []

frame_gap = True

patt = r"(.+)\."

#Encoding known images
print("Encoding Given Images.....")
for image in os.listdir("known img"):
    
    img = face_recognition.load_image_file(f"known img/{image}")

    img_encoding = face_recognition.face_encodings(img)[0]
    
    known_face_encodings.append(img_encoding)
    
    image_name = re.search(patt, image)
    
    known_face_names.append(image_name.group(1))

print("Encoding Done..")

while True:
    _ , frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if frame_gap:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            #identifying nearest face in multiple faces
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)
            if name != "Unknown":
                present_student_list.add(name)

    frame_gap = not frame_gap


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

#Creating Data frame and putting into csv


df = pd.read_csv("./attendence lists/student_list.csv")

student_list = list(df["Total Students"])

df = pd.DataFrame({
    "Total Students" : student_list , 
    "Attendance" : ["Absent"]*len(student_list)
})

for student in present_student_list:
        df.loc[df["Total Students"] == student , "Attendance"] = "Present"

today_date = date.today()

today_date = today_date.strftime("%Y-%m-%d")

#For not conflicting the file name
def is_file_exist(file_name):
    for file in os.listdir("./attendence lists"):
        if f"{file_name}.csv" == file:
            return True
    return False

def unqiue_file_name(today_date):
    current_date = today_date
    num = 1
    while True:
        if not is_file_exist(today_date):
            return today_date
        else:
            today_date = f"{current_date}({num})"
            num += 1

today_date = unqiue_file_name(today_date)

df.to_csv(f"./attendence lists/{today_date}.csv" , index=False)

print("attendence file is created")
