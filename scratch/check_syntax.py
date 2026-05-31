import re
import subprocess
import os

def check():
    html_path = r"c:\Users\Nam\OneDrive\Desktop\vinastudy-bot\tower_defense.html"
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the main <script> tag content (after the SoundFX or near the end)
    # Let's extract all content inside <script>...</script>
    scripts = re.findall(r"<script>(.*?)</script>", content, re.DOTALL)
    if not scripts:
        print("No script tags found!")
        return

    # Write each script block to a temporary file and check it
    os.makedirs("scratch", exist_ok=True)
    for idx, script_content in enumerate(scripts):
        temp_js = f"scratch/temp_check_{idx}.js"
        with open(temp_js, "w", encoding="utf-8") as f_out:
            f_out.write(script_content)

        print(f"Checking script block {idx}...")
        result = subprocess.run(["node", "--check", temp_js], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Syntax Error found in script block {idx}!")
            print(result.stderr)
            # Map temp JS line numbers back to original HTML line numbers
            # Find the start line of the script tag in the HTML
            lines = content.splitlines()
            script_start_line = 0
            # A simple search for the idx-th <script> tag
            script_count = 0
            for line_idx, line in enumerate(lines):
                if "<script>" in line:
                    if script_count == idx:
                        script_start_line = line_idx + 1
                        break
                    script_count += 1
            
            print(f"Original <script> tag starts at line: {script_start_line}")
            # Parse line number from error
            err_line_match = re.search(r"temp_check_\d+\.js:(\d+)", result.stderr)
            if err_line_match:
                js_err_line = int(err_line_match.group(1))
                html_err_line = script_start_line + js_err_line
                print(f"Approximate HTML line of error: {html_err_line}")
        else:
            print(f"✅ Script block {idx} is syntactically correct!")

if __name__ == "__main__":
    check()
