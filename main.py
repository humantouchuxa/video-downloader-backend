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
        'format': 'best/bestvideo+bestaudio',
        'noplaylist': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android_vr'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Quest 2) AppleWebKit/537.36 (KHTML, like Gecko) OculusBrowser/20.0.0 SamsungBrowser/4.0 Chrome/107.0.5304.141 Mobile Safari/537.36',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = []
            for f in info.get('formats', []):
                if f.get('url') and f.get('ext') in ['mp4', 'webm', 'mp3']:
                    formats.append({
                        'quality': str(f.get('format_note', f.get('height', 'standard'))),
                        'ext': f.get('ext', 'mp4'),
                        'url': f.get('url', '')
                    })
            return jsonify({
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail', ''),
                'platform': info.get('extractor', ''),
                'download_url': info.get('url', ''),
                'formats': formats[-6:]
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
