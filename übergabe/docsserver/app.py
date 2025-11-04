from flask import Flask, render_template, request
from pathlib import Path
import markdown
import os

app = Flask(__name__)

# Directory to read files from
DOCS_PATH = Path(r"C:\Users\bearb\Desktop\micro\übergabe\documentation")  # adjust this to your folder

@app.route("/docs")
def index():
    # List all .md and .txt files
    files = [f.relative_to(DOCS_PATH) for f in DOCS_PATH.rglob("*") if f.suffix in [".md", ".txt"]]

    # Get selected file from query parameter
    file_name = request.args.get("file")
    content_html = ""
    if file_name:
        file_path = DOCS_PATH / file_name
        if file_path.exists() and file_path.is_file():
            text = file_path.read_text(encoding="utf-8")
            if file_path.suffix == ".md":
                content_html = markdown.markdown(text)
            else:
                # raw txt files
                content_html = "<pre>" + text + "</pre>"

    return render_template("index.html", files=files, content=content_html, selected=file_name)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
