import replicate
import os
import io
import httpx
import concurrent.futures

# Set token explicitly
os.environ["REPLICATE_API_TOKEN"] = "r8_SnyViTeEsyAE3kP2F2KdMr4ly4fLHln1atZVh"

# Using a reliable test image URL (scikit-image astronaut)
IMAGE_URL = "https://raw.githubusercontent.com/scikit-image/scikit-image/main/skimage/data/astronaut.png"

PROMPTS = {
    "chien_binh": "A cute and heroic male warrior in neon cyberpunk armor, masterpiece, 8k resolution, highly detailed anime art style",
    "phu_thuy": "A mysterious male wizard in dark glowing robes holding a neon magic staff, masterpiece, 8k resolution, highly detailed anime art style",
    "xa_thu": "An agile male archer with a futuristic neon bow and arrow, masterpiece, 8k resolution, highly detailed anime art style",
    "hiep_si": "A noble male knight in shining heavy armor with a glowing shield, masterpiece, 8k resolution, highly detailed anime art style"
}

ARTIFACTS_DIR = r"C:\Users\Nam\.gemini\antigravity\brain\bfbb8ec0-e6a4-4cca-af30-b65e4594f0c3\scratch"
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

def generate_avatar(char_type, prompt):
    print(f"Generating {char_type}...")
    try:
        output = replicate.run(
            "fofr/face-to-many:a07f252abbbd832009640b27f063ea52d87d7a23a185ca165bec23b5adc8deaf",
            input={
                "image": IMAGE_URL,
                "style": "Video game",
                "prompt": prompt,
                "instant_id_strength": 0.8
            }
        )
        url = str(output[0]) if isinstance(output, list) else str(output)
        print(f"[{char_type}] URL: {url}")
        
        # Download
        resp = httpx.get(url, timeout=60)
        resp.raise_for_status()
        
        filepath = os.path.join(ARTIFACTS_DIR, f"{char_type}.png")
        with open(filepath, "wb") as f:
            f.write(resp.content)
            
        print(f"[{char_type}] Saved to {filepath}")
        return filepath
    except Exception as e:
        print(f"[{char_type}] ERROR: {e}")
        return None

def main():
    print("Starting generation of 4 avatars...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(generate_avatar, k, v): k for k, v in PROMPTS.items()}
        for future in concurrent.futures.as_completed(futures):
            char_type = futures[future]
            future.result()
    print("All done!")

if __name__ == "__main__":
    main()
