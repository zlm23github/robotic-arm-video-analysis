from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from PIL import Image
import os
import cv2
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Gemini API setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
ai = genai.GenerativeModel("gemini-1.5-flash")

router = APIRouter()

# create upload folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@router.post("/upload")
async def upload_video(video: UploadFile = File(...)):
    try:
        # save video to local
        video_path = os.path.join(UPLOAD_FOLDER, video.filename)
        with open(video_path, "wb") as buffer:
            content = await video.read()
            buffer.write(content)

        return {
            "message": "Video uploaded successfully",
            "video_path": video_path,
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/upload-url")
async def upload_video_url(url: str = Body(..., embed=True)):
    try:
        # download video from url
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to download video from url")
        
        # save video to local
        video_path = os.path.join(UPLOAD_FOLDER, url.split("/")[-1])
        with open(video_path, "wb") as buffer:
            buffer.write(response.content)
            
        return {
            "message": "Video uploaded successfully",
            "video_path": video_path,
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/analyze/{filename}")
async def analyze_video(filename: str):
    try:
        # get video path
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        
        if not os.path.exists(video_path):
            return {"error": "Video not found"}
        
        # extract frames
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) # get fps of video
        frame_interval = int(fps / 2) # extract one frame every 0.5 seconds
        frame_idx = 0
        group_size = 10
        timestamps = []
        frames = []
        results = []
        num_cams = 4

        last_analysis = ""

        prompt = """
        You are an labeler for a robotic arm video.
        You are given a sequence of images each group. Every 4 images (one from each angle) separated by 0.5 second.
        The images are from a video for a period of time {start_time} to {end_time}.
        For each moment, there are 4 images from different camera angles (top, front, left, right) that are taken at the same time and shooting the same object.
        
        You task is:
        Analyze all these images together and identify the distinct actions performed by the robotic arm(s). 
        For each action, provide a detailed and structured description including:
        - What the robotic arm is doing (the action itself, e.g., grasp, rotate, open, close, move, slide, etc.)
        - What object is being acted upon (e.g., ziploc bag, box, bottle, etc.)
        - Which part of the object is being acted upon (e.g., the lid, the seal, the handle, the side, etc.)

        Each entry should be as specific as possible. For example:
        - "Grasp the seal of the ziploc bag"
        - "Open the lid of the box"
        - "Move the bag to the right side of the table"
        - "Rotate the cap of the bottle"

        If the object or part is unclear, make a reasonable guess based on the images.
        Please pay special attention to fine-grained actions such as opening, sliding, or pulling apart the seal of a ziploc bag. 
        If you observe the robotic arm interacting with the seal or top edge of the bag, consider whether it is opening or closing the bag, and describe this action specifically (e.g., 'slide open the seal of the ziploc bag').
        For each action, provide:
        - Start time (mm:ss)
        - End time (mm:ss)
        - A concise description of the action

        And I will provide you the analysis of the previous group of images {last_analysis}.
        The last_analysis is the analysis of the previous group of images.
        
        If last_analysis is not empty, you should analyze the current images combining with the last_analysis and update the result accordingly.
        For example, if the last_analysis is:
        [
            {
                "start_time": "00:10",
                "end_time": "00:15",
                "description": "Pick up the item from the table and place it into the box"
            }
        ]
        You should analyze the current images and update the result accordingly. Let's say the current images also show the action of "Pick up the item from the table and place it into the box". You should update the result to:
        [
            {
                "start_time": "00:10",
                "end_time": "00:20",
                "description": "Pick up the item from the table and place it into the box"
            }
        ]

        The start_time represents the start time of the action, and the end_time represents the end time of the action.
        If there are multiple actions in the current group, you should update the result to:
        [
            {
                "start_time": "00:10",
                "end_time": "00:18",
                "description": "Pick up the item from the table and place it into the box"
            },
            {
                "start_time": "00:18",
                "end_time": "00:20",
                "description": "Place the item into the box"
            }
        ]

        If the last_analysis is empty, you should just analyze the current images and output the result.
        
        IMPORTANT TIME CONSTRAINT:
        - The maximum time you can use in your labels is {end_time}
        - You MUST NOT use any time beyond {end_time}
        - If you see an action that seems to continue beyond {end_time}, you must end your label at {end_time}
        - This is a HARD LIMIT - no exceptions
        - Time calculation rules:
            * Every 4 images (one from each angle) represent 1 second
            * The maximum time you can label is {end_time}
            * Do not make up or extrapolate times beyond {end_time}
            * Last end time returned must be {end_time}
                
        ACTION TIMING & COMPLETION RULES:
        - The start_time of an action should be the exact moment when the robotic arm begins to move for that action.
        - The end_time of an action should be the exact moment when the robotic arm has finished all key steps of the action and has stopped all related movements.
        - If the action is still ongoing at the end of the current image group, do NOT end the action in this group. Continue the action in the next group, using the same start_time.
        - Only set the end_time when you are certain the action is truly complete (e.g., the tape is fully applied and the arm has stopped moving away from the box).
        - Do not split a continuous action into multiple segments unless there is a clear change in the main goal or object.
        - If you are unsure, prefer to extend the action until you are certain it is complete.
        
        CRITICAL ACTION DISTINCTION:
        - Pay special attention to OPEN vs CLOSE actions:
        * OPEN: When the robotic arm is separating or pulling apart parts (e.g., opening a ziploc bag seal)
        * CLOSE: When the robotic arm is bringing parts together (e.g., closing a ziploc bag seal)
        - Look carefully at the direction of movement:
        * If the arm is pulling parts apart → OPEN
        * If the arm is pushing parts together → CLOSE
        - For ziploc bags specifically:
        * OPEN: When the seal is being pulled apart or separated
        * CLOSE: When the seal is being pressed together or sealed
        - Do not confuse these actions - they are fundamentally different
        
        ACTION MERGING RULES:
        - If a complex action consists of several small steps (for example: pulling tape, sticking tape to the box, releasing tape), you should merge these steps into a single high-level action (for example: "apply tape to the box").
        - Do not split a continuous process into multiple short actions if they are all part of the same overall goal.
        - Only create a new action entry if the main goal or object of the action changes.
        - For example, for taping a box, regardless of the small steps, label the whole process as "apply tape to the box" with the start time when the process begins and the end time when the process finishes.
        - If you are unsure whether to merge, prefer merging into a single, more general action.
        
        ACTION COMPLETION RULES:
        - An action is only considered complete when all of its key steps are finished and the robotic arm has stopped all related movements.
        - If the action (such as applying tape to a box) is still ongoing at the end of the current image group, do NOT end the action in this group. Instead, continue the action in the next group, using the same start_time.
        - Only set the end_time when you see that the action is truly finished (e.g., the tape is fully applied and the arm has stopped moving away from the box).
        - Do not split a continuous action into multiple segments unless there is a clear change in the main goal or object.
        - If you are unsure, prefer to extend the action until you are certain it is complete.

        Note: The actions may start before the first moment or end after the last moment in this group. 
        

        Output ONLY the JSON array. Do not include any explanations or commentary. Just describe the action no need for subject like "the robotic arm".
        """

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % frame_interval == 0:
                seconds = int(frame_idx / fps)
                mm = seconds // 60
                ss = seconds % 60
                frames.append(frame)
                timestamps.append(f"{mm:02d}:{ss:02d}")
                
                if len(frames) == group_size:
                    start_time = timestamps[-group_size]  # Get the timestamp of the first frame in current 5-frame segment
                    end_time = timestamps[-1]  # Get the timestamp of the last frame in current 5-frame segment
                    images = []
                    for frame in frames:
                        h, w, _ = frame.shape
                        sub_width = w // num_cams
                        # cut image
                        top_img = frame[:, :sub_width, :]
                        front_img = frame[:, sub_width:2*sub_width, :]
                        front_img = cv2.rotate(front_img, cv2.ROTATE_90_CLOCKWISE)
                        left_img = frame[:, 2*sub_width:3*sub_width, :]
                        right_img = frame[:, 3*sub_width:4*sub_width, :]
                        
                        # convert to PIL image
                        images.extend([
                            Image.fromarray(cv2.cvtColor(top_img, cv2.COLOR_BGR2RGB)),
                            Image.fromarray(cv2.cvtColor(front_img, cv2.COLOR_BGR2RGB)),
                            Image.fromarray(cv2.cvtColor(left_img, cv2.COLOR_BGR2RGB)),
                            Image.fromarray(cv2.cvtColor(right_img, cv2.COLOR_BGR2RGB)),
                        ])                    
                    print("start_time: ", start_time, "end_time: ", end_time)
                    print("images: ", len(images))
                    
                    response = ai.generate_content([prompt, *images, last_analysis])
                    last_analysis = response.text
                    # Reset frames and timestamps after processing
                    frames = []

            frame_idx += 1

        # Process remaining frames if any
        if len(frames) > 0:
            start_time = timestamps[-len(frames)]  # Get the timestamp of the first frame in remaining frames
            end_time = timestamps[-1]  # Get the timestamp of the last frame in remaining frames
            images = []
            for frame in frames:
                h, w, _ = frame.shape
                sub_width = w // num_cams
                # cut image
                top_img = frame[:, :sub_width, :]
                front_img = frame[:, sub_width:2*sub_width, :]
                front_img = cv2.rotate(front_img, cv2.ROTATE_90_CLOCKWISE)
                left_img = frame[:, 2*sub_width:3*sub_width, :]
                right_img = frame[:, 3*sub_width:4*sub_width, :]
                
                # convert to PIL image
                images.extend([
                    Image.fromarray(cv2.cvtColor(top_img, cv2.COLOR_BGR2RGB)),
                    Image.fromarray(cv2.cvtColor(front_img, cv2.COLOR_BGR2RGB)),
                    Image.fromarray(cv2.cvtColor(left_img, cv2.COLOR_BGR2RGB)),
                    Image.fromarray(cv2.cvtColor(right_img, cv2.COLOR_BGR2RGB)),
                ])                    
            print("start_time: ", start_time, "end_time: ", end_time)
            print("images: ", len(images))

            response = ai.generate_content([prompt, *images, last_analysis])
            last_analysis = response.text

        cap.release()
        results.append({
            "description": last_analysis
        })

        return {
            "results": results
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/files")
async def get_video_files():
    try:
        files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.mp4')]
        return {"files": files}
    except Exception as e:
        return {"error": str(e)} 