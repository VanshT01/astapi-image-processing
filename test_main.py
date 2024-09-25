import pytest
from fastapi.testclient import TestClient
from main import app1  # Make sure you're importing the FastAPI instance from main.py
from io import BytesIO
from PIL import Image

client = TestClient(app1)

# Helper function to create an in-memory image file for testing
def create_test_image():
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))  # Create a 100x100 red image
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes

# Test the upload image functionality
def test_upload_image():
    img_bytes = create_test_image()
    response = client.post(
        "/upload/",
        files={"image": ("test_image.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    assert "Image 'test_image.jpg' uploaded successfully" in response.json()["info"]

# Test rotating an uploaded image
def test_rotate_image():
    img_bytes = create_test_image()
    client.post("/upload/", files={"image": ("test_image.jpg", img_bytes, "image/jpeg")})
    response = client.get("/rotate/test_image.jpg?degrees=90")
    
    assert response.status_code == 200
    assert response.headers["content-disposition"] == 'attachment; filename="rotated_90_test_image.jpg"'

# Test grayscale conversion of an uploaded image
def test_grayscale_image():
    img_bytes = create_test_image()
    client.post("/upload/", files={"image": ("test_image.jpg", img_bytes, "image/jpeg")})
    response = client.get("/grayscale/test_image.jpg")
    
    assert response.status_code == 200
    assert response.headers["content-disposition"] == 'attachment; filename="grayscale_test_image.jpg"'

# Test invalid file upload (non-image file)
def test_invalid_image_upload():
    response = client.post("/upload/", files={"image": ("test.txt", BytesIO(b"Not an image"), "text/plain")})
    
    assert response.status_code == 200
    assert response.json()["error"] == "Invalid image format. Only JPEG and PNG are supported."

# Test image not found for rotation
def test_image_not_found_rotate():
    response = client.get("/rotate/non_existent_image.jpg?degrees=90")
    
    assert response.status_code == 200
    assert response.json()["error"] == "Image not found"

# Test image not found for grayscale conversion
def test_image_not_found_grayscale():
    response = client.get("/grayscale/non_existent_image.jpg")
    
    assert response.status_code == 200
    assert response.json()["error"] == "Image not found"
