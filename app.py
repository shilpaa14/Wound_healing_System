import io
import os
import csv
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from PIL import Image
import base64
import torch
import torch.nn as nn
from torchvision import models, transforms
import numpy as np
import cv2

app = Flask(__name__)
MODEL_PATH = os.path.join("models", "best_wound_cnn.pt")
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --------------------
# Model: ResNet18 -> single output (0-1) -> percent
# --------------------
class WoundRegressor(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = models.resnet18(pretrained=True)
        in_features = self.backbone.fc.in_features
        self.backbone.fc = nn.Linear(in_features, 1)

    def forward(self, x):
        x = self.backbone(x)
        x = torch.sigmoid(x).view(-1)
        return x

# --------------------
# Image transformations
# --------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

# --------------------
# Load model if available
# --------------------
model = None
if os.path.exists(MODEL_PATH):
    try:
        model = WoundRegressor().to(DEVICE)
        model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        model.eval()
        print("✅ Loaded pretrained model from:", MODEL_PATH)
    except Exception as e:
        print("⚠️ Failed to load model:", e)
        model = None
else:
    print("⚠️ No pretrained model found — using heuristic fallback.")

# --------------------
# Heuristic fallback (if model unavailable)
# --------------------
def heuristic_estimate(pil_image: Image.Image) -> float:
    arr = np.array(pil_image.convert("RGB"), dtype=np.float32) / 255.0
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    # red_ratio: how red the image is on average
    red_ratio = np.clip((r - (g + b) / 2), 0, 1).mean()
    # darkness_ratio: proportion of pixels that are fairly dark
    brightness = arr.mean(axis=2)
    darkness_ratio = (brightness < 0.45).mean()
    # combine: more red/dark -> more severe -> lower percent healed
    score = 1.0 - (0.6 * red_ratio + 0.4 * darkness_ratio)
    score = float(np.clip(score, 0.0, 1.0))
    return score * 100.0

# --------------------
# Healing visualization (optional)
# --------------------
def simulate_healing(pil_image):
    """Simulate pulling skin together — natural wound closing"""
    cv_img = np.array(pil_image.convert("RGB"))
    h, w, _ = cv_img.shape

    # Convert to HSV and find red region (wound)
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_RGB2HSV)
    lower_red1 = np.array([0, 80, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 80, 50])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # Find wound center
    moments = cv2.moments(mask)
    if moments["m00"] != 0:
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
    else:
        cx, cy = w // 2, h // 2  # fallback

    # Create mesh grid for warping
    map_x = np.zeros((h, w), np.float32)
    map_y = np.zeros((h, w), np.float32)

    # Parameters controlling pull strength and radius
    radius = min(h, w) // 6
    pull_strength = 0.3  # smaller → gentler pull

    for y in range(h):
        for x in range(w):
            dx = x - cx
            dy = y - cy
            dist = np.sqrt(dx * dx + dy * dy)
            if dist < radius:
                factor = 1 - pull_strength * (1 - dist / radius)
                new_x = cx + dx * factor
                new_y = cy + dy * factor
            else:
                new_x, new_y = x, y
            map_x[y, x] = new_x
            map_y[y, x] = new_y

    # Apply warp to pull skin inward
    healed = cv2.remap(cv_img, map_x, map_y, interpolation=cv2.INTER_LINEAR)

    # Optional light smoothing
    healed = cv2.GaussianBlur(healed, (5, 5), 2)

    healed_path = os.path.join("static", "healed_preview.jpg")
    cv2.imwrite(healed_path, cv2.cvtColor(healed, cv2.COLOR_RGB2BGR))
    return healed_path


# --------------------
# Save healing progress to CSV
# --------------------
def save_progress(healing_percent):
    os.makedirs("data", exist_ok=True)
    csv_path = os.path.join("data", "healing_log.csv")
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), round(healing_percent, 2)])
    return csv_path

@app.route('/')
def index():
    return render_template('index.html')

# --------------------
# Routes
# --------------------
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        image_data = data['image']

        # Decode the base64 image sent from the frontend
        image_bytes = base64.b64decode(image_data.split(',')[1])
        pil_image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

        # If pretrained model is available
        if model:
            tensor = transform(pil_image).unsqueeze(0).to(DEVICE)
            with torch.no_grad():
                pred = model(tensor).cpu().numpy()[0]
            healing_percent = float(pred * 100.0)
        else:
            # Fallback if no model
            healing_percent = heuristic_estimate(pil_image)

        # Estimate days remaining (simple formula)
        days_remaining = round((100 - healing_percent) / 5)

        # --------------------
        # Healing status and advice (dynamic version)
        # --------------------
        if healing_percent >= 85:
            status = "Healed – minimal care needed."
            advice = "The wound appears healed. Continue to monitor for irritation."
        elif healing_percent >= 60:
            status = "Mild wound – almost healing!"
            if days_remaining <= 3:
                advice = f"Continue care for {days_remaining} more day(s); healing is nearly complete."
            else:
                advice = f"Continue care for about {days_remaining} more days; healing progress is steady."
        elif healing_percent >= 30:
            status = "Moderate wound – healing in progress."
            advice = f"Apply antiseptic and maintain dressing for around {days_remaining} more days."
        else:
            status = "Severe wound – needs medical care."
            advice = f"Healing may take over {days_remaining} days. Please consult a medical professional."


        # Save healing progress to CSV
        save_progress(healing_percent)

        # Generate simulated healed image
        healed_path = simulate_healing(pil_image)

        # Send back JSON response
        return jsonify({
            "healing_percent": round(healing_percent, 2),
            "days_remaining": days_remaining,
            "status": status,
            "advice": advice,
            "healed_image": healed_path
        })

    except Exception as e:
        print("Error during prediction:", e)
        return jsonify({"error": str(e)})


@app.route('/history')
def history():
    data = []
    csv_path = os.path.join("data", "healing_log.csv")

    if os.path.exists(csv_path):
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 2:
                    data.append({"timestamp": row[0], "healing_percent": float(row[1])})
    return render_template('history.html', healing_data=data)


# --------------------
# Run Flask App
# --------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
