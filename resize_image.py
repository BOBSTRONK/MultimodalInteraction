import os
from PIL import Image

def crop_images(input_folder, output_folder, crop_box):
    """
    Crops all images in the input_folder and saves the cropped images to the output_folder.
    
    Parameters:
    - input_folder (str): The path to the folder containing the images to be cropped.
    - output_folder (str): The path to the folder where the cropped images will be saved.
    - crop_box (tuple): A tuple of four integers specifying the left, upper, right, and lower pixel coordinate.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    for filename in os.listdir(input_folder):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')):
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            cropped_img = img.crop(crop_box)
            cropped_img.save(os.path.join(output_folder, filename))
            print(f"Cropped {filename} and saved to {output_folder}")

# Example usage
input_folder = '/Users/jngelena/Desktop/dataset/carlo/previous2'
output_folder = '/Users/jngelena/Desktop/dataset/carlo_cropped/previous2'
crop_box = (100, 0, 1600, 700)  # (left, upper, right, lower)

crop_images(input_folder, output_folder, crop_box)
