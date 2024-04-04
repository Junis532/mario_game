import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# 웹캠 화면 크기 설정
new_width = 330  # 원하는 너비
new_height = 240  # 원하는 높이

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
cap.set(3, new_width)  # 너비 설정
cap.set(4, new_height)  # 높이 설정

above_line_color = (0, 0, 255)
below_line_color = (0, 0, 255)
eye_line_color = (0, 255, 0)  # Color for eye line
above_line_detected = False
below_line_detected = False
eye_line_detected = False
shift_detected = False

# "space.txt" 파일 열기
try:
    with open("space.txt", "w") as file:
        file.write("")
except PermissionError as e:
    print(f"Permission denied: {e}")

# "shift.txt" 파일 열기
try:
    with open("shift.txt", "w") as file:
        file.write("")
except PermissionError as e:
    print(f"Permission denied: {e}")

with mp_pose.Pose(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("웹캠을 찾을 수 없습니다.")
            continue

        image = cv2.flip(image, 1)  # 1 means horizontal flip

        h, w, _ = image.shape
        cv2.line(image, (0, h // 3), (w, h // 3), above_line_color, 2)
        cv2.line(image, (0, 4 * h // 6), (w, 4 * h // 6), below_line_color, 2)
        cv2.putText(image, f"Jump", (130, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, above_line_color, 2)
        cv2.putText(image, f"Slide", (130, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, below_line_color, 2)

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Define the landmark indices for the left and right eyes
        left_eye_index = mp_pose.PoseLandmark.LEFT_EYE
        right_eye_index = mp_pose.PoseLandmark.RIGHT_EYE

        # Access the coordinates of the left and right eyes
        if results.pose_landmarks:
            left_eye_landmark = results.pose_landmarks.landmark[left_eye_index]
            right_eye_landmark = results.pose_landmarks.landmark[right_eye_index]

            left_eye_x = int(left_eye_landmark.x * image.shape[1])
            left_eye_y = int(left_eye_landmark.y * image.shape[0])

            right_eye_x = int(right_eye_landmark.x * image.shape[1])
            right_eye_y = int(right_eye_landmark.y * image.shape[0])

            # 포즈 점 그리기
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # 한쪽 눈 점이 위에 있는 빨간 가로선 위로 올라갔을 때 빨간 가로선을 파란색으로 변경
            if left_eye_y < h // 3 and not above_line_detected:
                above_line_detected = True
                below_line_detected = False

                # "space.txt" 파일 열고 "space" 단어 추가
                try:
                    with open("space.txt", "a") as file:
                        file.write("space\n")
                except PermissionError as e:
                    print(f"Permission denied: {e}")
            elif left_eye_y < 4 * h // 6 and left_eye_y > h // 4:
                below_line_detected = True
                above_line_detected = False

                # "space.txt" 파일 열고 "space" 단어 삭제
                try:
                    with open("space.txt", "r") as file:
                        lines = file.readlines()
                    with open("space.txt", "w") as file:
                        for line in lines:
                            if line.strip() != "space":
                                file.write(line)
                except PermissionError as e:
                    print(f"Permission denied: {e}")

            # 한쪽 눈 점이 위에 있는 빨간 가로선 위로 올라갔을 때 빨간 가로선을 파란색으로 변경
            if left_eye_y < h // 3:
                above_line_color = (0, 0, 255)
            # 한쪽 눈 점이 밑에 있는 빨간 가로선 아래로 내려갔을 때 빨간 가로선을 파란색으로 변경
            elif left_eye_y > 4 * h // 6 and not shift_detected:
                below_line_color = (0, 0, 255)

                # "shift.txt" 파일 열고 "shift" 단어 추가
                try:
                    with open("shift.txt", "a") as file:
                        file.write("shift\n")
                except PermissionError as e:
                    print(f"Permission denied: {e}")
                shift_detected = True  # Shift 키 누름 감지 변수 설정

            elif left_eye_y < 4 * h // 6 and left_eye_y > h // 3:
                above_line_color = (0, 255, 0)
                below_line_color = (0, 255, 0)
                shift_detected = False
                # "shift.txt" 파일 열고 "shift" 단어 삭제
                try:
                    with open("shift.txt", "r") as file:
                        lines = file.readlines()
                    with open("shift.txt", "w") as file:
                        for line in lines:
                            if line.strip() != "shift":
                                file.write(line)
                except PermissionError as e:
                    print(f"Permission denied: {e}")

        cv2.imshow('Pose Detection', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
