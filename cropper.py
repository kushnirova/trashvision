import os
from PIL import Image

def crop_center_sq(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.JPG'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            try:
                with Image.open(input_path) as img:
                    width, height = img.size
                    min_side = min(width, height)
                    left = (width - min_side) // 2
                    top = 0
                    right = left + min_side
                    bottom = min_side
                    cropped_img = img.crop((left, top, right, bottom))
                    cropped_img.save(output_path)

                    print(f"Cropped to square: {filename}")

            except Exception as e:
                print(f"Error on file: {filename}: {e}")

if __name__ == "__main__":
    input_folder = "images_before_crop"
    output_folder = "crop_sq"

    crop_center_sq(input_folder, output_folder)

    print("Finished cropping photos to square!")
