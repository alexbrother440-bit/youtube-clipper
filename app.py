from flask import Flask, render_template, request, send_file
import os, uuid, subprocess

app = Flask(__name__)
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    message = None
    output = None
    if request.method == "POST":
        url = request.form.get("url", "").strip()
        start = request.form.get("start", "0").strip()
        end = request.form.get("end", "30").strip()

        if not url:
            message = "Masukkan URL YouTube."
        else:
            try:
                clip_id = str(uuid.uuid4())
                source = os.path.join(DOWNLOAD_DIR, clip_id + ".mp4")
                output = os.path.join(DOWNLOAD_DIR, clip_id + "_clip.mp4")

                # Download video. Use only videos you have permission to download/edit.
                subprocess.run([
                    "yt-dlp", "-f", "bv*[height<=1080]+ba/b[height<=1080]",
                    "--merge-output-format", "mp4", "-o", source, url
                ], check=True)

                # Crop to 9:16 and clip selected time range.
                subprocess.run([
                    "ffmpeg", "-y", "-ss", start, "-to", end, "-i", source,
                    "-vf", "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920",
                    "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac",
                    output
                ], check=True)

                os.remove(source)
                message = "Clip berhasil dibuat."
            except Exception as e:
                message = "Gagal memproses video. Pastikan yt-dlp dan FFmpeg terpasang."
                output = None

    return render_template("index.html", message=message, output=output)

@app.route("/download/<path:filename>")
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
