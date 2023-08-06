import os
from collecting_faces.preprocess.face_alignment import image_align
from collecting_faces.preprocess.landmarks_detector import LandmarksDetector
import cv2
from tqdm import tqdm

def collect_faces(raw_dir, aligned_dir, output_size=256, x_scale=1, y_scale=1, em_scale=0.1, use_alpha=False):
    """
    Extracts and aligns all faces from images using DLib and a function from original FFHQ dataset preparation step
    python align_images.py /raw_images /aligned_images
    """
    RAW_IMAGES_DIR = raw_dir
    ALIGNED_IMAGES_DIR = aligned_dir
    os.makedirs(ALIGNED_IMAGES_DIR, exist_ok=True)

    landmarks_detector = LandmarksDetector()
    for img_name in tqdm(os.listdir(RAW_IMAGES_DIR)):
        print('Aligning %s ...' % img_name)
        try:
            raw_img_path = os.path.join(RAW_IMAGES_DIR, img_name)
            raw_img = cv2.imread(raw_img_path)
            fn = face_img_name = '%s_%02d.png' % (os.path.splitext(img_name)[0], 1)

            if os.path.isfile(fn):
                continue
            print('Getting landmarks...')
            # for i, face_landmarks in enumerate(landmarks_detector.get_landmarks(raw_img_path), start=1):
            for i, face_landmarks in enumerate(landmarks_detector.get_landmarks(raw_img), start=1):
                try:
                    print('Starting face alignment...')
                    face_img_name = '%s_%02d.png' % (os.path.splitext(img_name)[0], i)
                    aligned_face_path = os.path.join(ALIGNED_IMAGES_DIR, face_img_name)
                    image_align(raw_img_path, aligned_face_path, face_landmarks, output_size=output_size,
                                x_scale=x_scale, y_scale=y_scale, em_scale=em_scale,
                                alpha=use_alpha)
                    print('Wrote result %s' % aligned_face_path)
                except Exception as e:
                    print("Exception in face alignment!\n", e)
        except Exception as e:
            print("Exception in landmark detection!\n", e)
