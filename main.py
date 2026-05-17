from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Downloader API is running!"

@app.route('/get-info', methods=['POST'])
def get_info():
    data = request.get_json()
    url = data.get('url', '')

    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'format': 'best',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                'title': info.get('title', 'Unknown'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'platform': info.get('extractor', ''),
                'download_url': info.get('url', ''),
                'formats': [
                    {
                        'quality': f.get('format_note', 'unknown'),
                        'ext': f.get('ext', ''),
                        'url': f.get('url', '')
                    }
                    for f in info.get('formats', [])
                    if f.get('url') and f.get('ext') in ['mp4', 'webm', 'mp3']
                ][-5:]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
