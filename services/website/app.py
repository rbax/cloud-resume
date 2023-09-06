from flask import Flask, request, send_file, jsonify
try:
    from .utils.aws_s3 import AWSS3
    from .utils.audio import Audio
except:
    from utils.aws_s3 import AWSS3
    from utils.audio import Audio
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
s3 = AWSS3()
audio = Audio()
logging.basicConfig(level=logging.INFO)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)


@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/record', methods=['POST'])
def record():
    audio_file = request.files.get('audio')
    logging.info(f'saved record for {audio_file}')
    if audio_file:
        audio_file.save('recording.wav')
        s3.upload_file('recording.wav', 'asr/recording.wav')
        return '', 200
    else:
        return 'No audio file found', 400

@app.route('/playback', methods=['GET'])
def playback():
    logging.info('playing back audio file.')
    s3.download_file('asr/recording.wav', 'recording.wav')
    length = audio.get_length('recording.wav')
    return {'length': length}, 200

@app.route('/audio', methods=['GET'])
def get_audio():
    return send_file('recording.wav')

@app.route('/test')
def test():
    return {'status': 'working!'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)