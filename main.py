from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import yt_dlp
import requests

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


@app.route('/proxy-download', methods=['GET'])
def proxy_download():
    video_url = request.args.get('url', '')
    filename = request.args.get('filename', 'video.mp4')
    ext = request.args.get('ext', 'mp4')

    if not video_url:
        return jsonify({'error': 'No URL'}), 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.google.com/',
    }

    try:
        r = requests.get(video_url, headers=headers, stream=True, timeout=30)

        response_headers = {
            'Content-Disposition': f'attachment; filename="{filename}.{ext}"',
            'Content-Type': r.headers.get('Content-Type', f'video/{ext}'),
            'Access-Control-Allow-Origin': '*',
        }

        if 'Content-Length' in r.headers:
            response_headers['Content-Length'] = r.headers['Content-Length']

        return Response(
            stream_with_context(r.iter_content(chunk_size=1024 * 1024)),
            headers=response_headers,
            status=200
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
