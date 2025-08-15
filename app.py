from flask import Flask, request, render_template, send_file
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import zipfile
import os

app = Flask(__name__)

def fetch_and_zip_images(url, max_width=None, max_height=None):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    images = []
    
    for img_tag in soup.find_all("img"):
        img_url = img_tag.get("src")
        if not img_url:
            continue
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        elif img_url.startswith("/"):
            img_url = url.rstrip("/") + img_url
        
        try:
            img_data = requests.get(img_url, timeout=5).content
            img = Image.open(BytesIO(img_data))
            
            if max_width and img.width > max_width:
                continue
            if max_height and img.height > max_height:
                continue
            
            images.append((img_url.split("/")[-1], img_data))
        except:
            continue
    
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for filename, data in images:
            zip_file.writestr(filename, data)
    zip_buffer.seek(0)
    return zip_buffer

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        max_width = request.form.get("width")
        max_height = request.form.get("height")
        
        max_width = int(max_width) if max_width else None
        max_height = int(max_height) if max_height else None
        
        zip_file = fetch_and_zip_images(url, max_width, max_height)
        return send_file(zip_file, as_attachment=True, download_name="images.zip")
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
