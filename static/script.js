

const canvas = document.getElementById('woundCanvas');
const ctx = canvas.getContext('2d');
const fileInput = document.getElementById('imageUpload');
const predictBtn = document.getElementById('predictBtn');
const resultDiv = document.getElementById('result');

const moveBtn = document.getElementById('moveBtn');
const resizeBtn = document.getElementById('resizeBtn');
const zoomInBtn = document.getElementById('zoomInBtn');
const zoomOutBtn = document.getElementById('zoomOutBtn');

let img = new Image();
let imageLoaded = false;

// Default image parameters
let imgX = 50, imgY = 50, imgW = 300, imgH = 300;
let dragging = false;
let resizing = false;
let startX, startY;

fileInput.addEventListener('change', e => {
  const file = e.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    img.src = ev.target.result;
  };
  reader.readAsDataURL(file);
});

img.onload = () => {
  imageLoaded = true;
  drawImage();
};

function drawImage() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  if (imageLoaded) ctx.drawImage(img, imgX, imgY, imgW, imgH);
}

canvas.addEventListener('mousedown', e => {
  if (!imageLoaded) return;
  startX = e.offsetX;
  startY = e.offsetY;

  if (currentMode === 'move') dragging = true;
  if (currentMode === 'resize') resizing = true;
});

canvas.addEventListener('mousemove', e => {
  if (!imageLoaded) return;

  if (dragging) {
    const dx = e.offsetX - startX;
    const dy = e.offsetY - startY;
    imgX += dx;
    imgY += dy;
    startX = e.offsetX;
    startY = e.offsetY;
    drawImage();
  } else if (resizing) {
    const dx = e.offsetX - startX;
    const dy = e.offsetY - startY;
    imgW += dx;
    imgH += dy;
    startX = e.offsetX;
    startY = e.offsetY;
    drawImage();
  }
});

canvas.addEventListener('mouseup', () => {
  dragging = false;
  resizing = false;
});

let currentMode = 'move';
moveBtn.onclick = () => currentMode = 'move';
resizeBtn.onclick = () => currentMode = 'resize';
zoomInBtn.onclick = () => { imgW *= 1.1; imgH *= 1.1; drawImage(); };
zoomOutBtn.onclick = () => { imgW *= 0.9; imgH *= 0.9; drawImage(); };

predictBtn.addEventListener('click', async () => {
  if (!imageLoaded) {
    resultDiv.innerHTML = "⚠️ Please upload an image first.";
    return;
  }

  // Always use the original uploaded image, not the modified canvas
  const tempCanvas = document.createElement('canvas');
  const tempCtx = tempCanvas.getContext('2d');
  tempCanvas.width = img.naturalWidth;
  tempCanvas.height = img.naturalHeight;
  tempCtx.drawImage(img, 0, 0);
  const imageData = tempCanvas.toDataURL('image/png');

  resultDiv.innerHTML = "⏳ Analyzing wound...";

  try {
    const response = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image: imageData })
    });

    const data = await response.json();
    if (data.error) {
    resultDiv.innerHTML = "❌ Error: " + data.error;
    } else {
    // Show healing percent and days
    resultDiv.innerHTML = `
        ✅ <b>Healing Percent:</b> ${data.healing_percent}%<br>
        ⏱️ <b>Estimated Days Remaining:</b> ${data.days_remaining}
    `;

    // Show wound status and advice
    document.getElementById('statusText').innerText = data.status;
    document.getElementById('adviceText').innerText = data.advice;

    // Display healed image preview
    const healedImg = document.getElementById('healedImage');
    healedImg.src = data.healed_image + '?t=' + new Date().getTime(); // prevent cache
    healedImg.style.display = 'block';
    }

  } catch (err) {
    resultDiv.innerHTML = "❌ Could not connect to backend.";
    console.error(err);
  }
});





