# QUESTION 3: Real-Time Webcam Image Classification using Streamlit & PyTorch

# Step 1: Import required libraries
import streamlit as st
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from PIL import Image
import pandas as pd
import requests
import torch.nn.functional as F

# Page configuration
st.set_page_config(
    page_title="Real-Time Webcam Image Classification",
    layout="centered"
)

st.title("📷 Real-Time Webcam Image Classification")
st.write("This web app captures a webcam image and classifies it using a pretrained ResNet-18 model.")

# Step 2: Download ImageNet class labels
LABELS_URL = "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt"
labels = requests.get(LABELS_URL).text.splitlines()

# Step 3: Load pretrained ResNet-18 model
device = torch.device("cpu")
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
model.to(device)
model.eval()

# Step 4: Define image preprocessing pipeline
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# Step 5: Capture image from webcam
captured_image = st.camera_input("Capture an image")

if captured_image is not None:
    image = Image.open(captured_image).convert("RGB")
    st.image(image, caption="Captured Image", use_column_width=True)

    # Preprocess image
    input_tensor = preprocess(image).unsqueeze(0).to(device)

    # Step 6: Model inference
    with torch.no_grad():
        outputs = model(input_tensor)

    probabilities = F.softmax(outputs[0], dim=0)
    top5_prob, top5_idx = torch.topk(probabilities, 5)

    # Display results
    results = {
        "Label": [labels[i] for i in top5_idx],
        "Probability": [float(p) for p in top5_prob]
    }

    df = pd.DataFrame(results)

    st.subheader("🔍 Top 5 Predictions")
    st.table(df)

    st.subheader("📊 Prediction Confidence")
    st.bar_chart(df.set_index("Label"))
