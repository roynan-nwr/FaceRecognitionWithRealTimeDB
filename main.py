import os
import pickle
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime
import numpy as np


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    # for realtime database which is in JSON format
    'databaseURL':"https://faceattendencerealtime-a551e-default-rtdb.firebaseio.com/",
    'storageBucket':"faceattendencerealtime-a551e.appspot.com"
})

bucket = storage.bucket()


# using opencv to open own camera of laptop which is 0
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread("Resources/background.png")

# creating path
# importing the mode images into a list
folderModePath = 'Resources/Modes'
# using loop to list the imgs of modes
modePathList = os.listdir(folderModePath)
# holds images
imgModeList = []


# os.path.join(folderPath, path): This constructs the full path to the image.
# cv2.imread(fullPath): This reads the image at the specified path.
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))

# Load the encoding file
print("Loading Encode File.....")
file = open('EncodeFile.p','rb') # rb for reading permission
encodeListKnownWithIds = pickle.load(file) # this will load all the file in encodeListKnownWithIds
file.close()
encodeListKnown, studentsIds = encodeListKnownWithIds
# print(studentsIds)
print("Encode File Loaded")


modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)  # because face recognition uses RGB and cv2 uses BGR

    # for faces and encoding in the current frame
    faceCurFrame = face_recognition.face_locations(imgS)
    # for new faces
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # for img overlay
    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType] #taking images from modes that holds images(4 images)

    if faceCurFrame:

        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            print("matches", matches)
            print("faceDis", faceDis)

            matchIndex = np.argmin(faceDis)
            # print("Match Index", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentsIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = 55+x1, 162+y1, x2-x1, y2-y1
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentsIds[matchIndex]
                # print(id)

                # if the counter is equal to 0 make it 1
                if counter == 0:
                    cvzone.putTextRect(imgBackground,"Loading", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1

            # if counter not equal 0
            if counter!=0:

                if counter == 1:
                    # Get the Data
                    studentInfo = db.reference(f'Students/{id}').get()
                    print(studentInfo)

                    # Get the Image from the storage
                    blob = bucket.get_blob(f'Images/{id}.png')
                    array = np.frombuffer(blob.download_as_string(), np.uint8)
                    imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

                    # Update data of attendance
                    datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],"%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                    print(secondsElapsed)
                    if secondsElapsed>30:
                        ref = db.reference(f'Students/{id}')
                        studentInfo['total_attendance'] +=1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        modeType = 3
                        counter = 0
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]


                if modeType!= 3:

                    if 10<counter<20:
                        modeType = 2


                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                    if counter<=10:

                        cv2.putText(imgBackground,str(studentInfo['total_attendance']),(861,125),
                                    cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                        cv2.putText(imgBackground,str(studentInfo['major']),(1006,550),
                                    cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                        cv2.putText(imgBackground,str(id),(1006,493),
                                    cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                        cv2.putText(imgBackground,str(studentInfo['standing']),(910,625),
                                    cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                        cv2.putText(imgBackground,str(studentInfo['year']),(1025,625),
                                    cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                        cv2.putText(imgBackground,str(studentInfo['starting_year']),(1125,625),
                                    cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)

                        (w, h), _ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                        offset = (414-w)//2
                        cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                        # person registered image will show up when the real person comes infront camera
                        imgBackground[175:175+216, 909:909+216] = imgStudent

                counter += 1

                # updating the attendance continuously
                if counter>=20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
