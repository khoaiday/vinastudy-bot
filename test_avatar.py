import os
import base64
from app.auth.avatar import generate_avatar_pipeline

# Ensure REPLICATE_API_TOKEN is set
if not os.getenv("REPLICATE_API_TOKEN"):
    print("Please set REPLICATE_API_TOKEN")

with open("test.jpg", "rb") as f:
    img_b64 = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode("utf-8")

print("Starting avatar pipeline...")
result = generate_avatar_pipeline(img_b64, "chien_binh", "nam")
if result["ok"]:
    print("Success! Final b64 length:", len(result["final_b64"]))
else:
    print("Error:", result.get("error"))
