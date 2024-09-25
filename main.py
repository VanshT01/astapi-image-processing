from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import FileResponse
from PIL import Image, ImageFilter, UnidentifiedImageError
import os
import aiofiles

app1 = FastAPI()

# Define folder to store images
IMAGE_FOLDER = "images"
PROCESSED_FOLDER = "processed"

# Create folders if they do not exist
os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# Helper function to save the image
def save_image(image: Image.Image, output_path: str):
    image.save(output_path)

# Upload an image
@app1.post("/upload/")
async def upload_image(image: UploadFile = File(...)):
    # Validate content type
    if image.content_type not in ["image/jpeg", "image/png"]:
        return {"error": "Invalid image format. Only JPEG and PNG are supported."}

    # Get secure file name
    file_location = os.path.join(IMAGE_FOLDER, os.path.basename(image.filename))
    
    try:
        # Save the uploaded image asynchronously
        async with aiofiles.open(file_location, "wb") as f:
            content = await image.read()
            await f.write(content)
        
        # Check if it's a valid image using PIL
        with Image.open(file_location) as img:
            img.verify()

        return {"info": f"Image '{image.filename}' uploaded successfully"}
    
    except UnidentifiedImageError:
        # Remove invalid files
        os.remove(file_location)
        return {"error": "Uploaded file is not a valid image"}
    except Exception as e:
        return {"error": f"Failed to upload image: {str(e)}"}

# Rotate image endpoint
@app1.get("/rotate/{image_name}")
async def rotate_image(image_name: str, degrees: int = 90):
    input_image_path = os.path.join(IMAGE_FOLDER, os.path.basename(image_name))
    
    if not os.path.exists(input_image_path):
        return {"error": "Image not found"}
    
    # Rotate the image by the specified degrees
    with Image.open(input_image_path) as img:
        rotated_img = img.rotate(degrees, expand=True)
        output_image_path = os.path.join(PROCESSED_FOLDER, f"rotated_{degrees}_{os.path.basename(image_name)}")
        save_image(rotated_img, output_image_path)
    
    return FileResponse(output_image_path, media_type="image/jpeg", filename=f"rotated_{degrees}_{image_name}")

# Grayscale conversion endpoint
@app1.get("/grayscale/{image_name}")
async def grayscale_image(image_name: str):
    input_image_path = os.path.join(IMAGE_FOLDER, os.path.basename(image_name))
    
    if not os.path.exists(input_image_path):
        return {"error": "Image not found"}
    
    # Convert the image to grayscale
    with Image.open(input_image_path) as img:
        grayscale_img = img.convert("L")
        output_image_path = os.path.join(PROCESSED_FOLDER, f"grayscale_{os.path.basename(image_name)}")
        save_image(grayscale_img, output_image_path)
    
    return FileResponse(output_image_path, media_type="image/jpeg", filename=f"grayscale_{image_name}")

# Resize image endpoint
@app1.get("/resize/{image_name}")
async def resize_image(image_name: str, width: int, height: int):
    input_image_path = os.path.join(IMAGE_FOLDER, os.path.basename(image_name))
    
    if not os.path.exists(input_image_path):
        return {"error": "Image not found"}
    
    # Resize the image to the specified width and height
    with Image.open(input_image_path) as img:
        resized_img = img.resize((width, height))
        output_image_path = os.path.join(PROCESSED_FOLDER, f"resized_{width}x{height}_{os.path.basename(image_name)}")
        save_image(resized_img, output_image_path)
    
    return FileResponse(output_image_path, media_type="image/jpeg", filename=f"resized_{width}x{height}_{image_name}")

# Crop image endpoint
@app1.get("/crop/{image_name}")
async def crop_image(image_name: str, left: int, top: int, right: int, bottom: int):
    input_image_path = os.path.join(IMAGE_FOLDER, os.path.basename(image_name))
    
    if not os.path.exists(input_image_path):
        return {"error": "Image not found"}
    
    # Crop the image to the specified box
    with Image.open(input_image_path) as img:
        cropped_img = img.crop((left, top, right, bottom))
        output_image_path = os.path.join(PROCESSED_FOLDER, f"cropped_{os.path.basename(image_name)}")
        save_image(cropped_img, output_image_path)
    
    return FileResponse(output_image_path, media_type="image/jpeg", filename=f"cropped_{image_name}")

# Apply filter (blur/sharpen) endpoint
@app1.get("/filter/{image_name}")
async def filter_image(image_name: str, filter_type: str = "blur"):
    input_image_path = os.path.join(IMAGE_FOLDER, os.path.basename(image_name))
    
    if not os.path.exists(input_image_path):
        return {"error": "Image not found"}
    
    # Apply filter to the image
    with Image.open(input_image_path) as img:
        if filter_type.lower() == "blur":
            filtered_img = img.filter(ImageFilter.BLUR)
        elif filter_type.lower() == "sharpen":
            filtered_img = img.filter(ImageFilter.SHARPEN)
        else:
            return {"error": f"Unsupported filter type: {filter_type}"}
        
        output_image_path = os.path.join(PROCESSED_FOLDER, f"{filter_type}_{os.path.basename(image_name)}")
        save_image(filtered_img, output_image_path)
    
    return FileResponse(output_image_path, media_type="image/jpeg", filename=f"{filter_type}_{image_name}")
