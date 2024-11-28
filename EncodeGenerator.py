import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    # for realtime database which is in JSON format
    'databaseURL':"https://faceattendencerealtime-a551e-default-rtdb.firebaseio.com/",
    'storageBucket':"faceattendencerealtime-a551e.appspot.com"
})


# importing student images
folderPath = 'Images'
# using loop to list the imgs of modes
PathList = os.listdir(folderPath)
print(PathList)
# holds images
imgList = []
studentsIds = []
for path in PathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentsIds.append(os.path.splitext(path)[0])


    # adding image to the database in the IMAGE folder which can be downloaded later

    # fileName = os.path.join(folderPath, path)
    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)




    # print(path)
    # print(os.path.splitext(path)[0])
    # #seprates  the images and png ----
    # then to select only image name we put 0 because 0 is the first element
    # append is used to add items on end of the list
    # os.path.join(folderPath, path): This constructs the full path to the image.
    # cv2.imread(fullPath): This reads the image at the specified path.



print(studentsIds)



    # creating a function(sending the list in the function)
# to generate encodings which will spit out a list with all the encodings
def findEncodings(imageslist):
    encodeList = []
# looping all the images to encode image
    for img in imageslist:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB) # because face recognition uses RGB and cv2 uses BGR
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode) # it will loop through all the images and save it.

    return encodeList


print("Encoding have Started ....")
encodeListKnown = findEncodings(imgList)
# print(encodeListKnown)
encodeListKnownWithIds = [encodeListKnown, studentsIds]
print("Encoding Complete")

file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithIds, file) # saveing in pickle file for ease to import while using the webcam
file.close()
print("File saved")