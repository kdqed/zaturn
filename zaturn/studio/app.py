from datetime import datetime

from flask import Flask, redirect, request, render_template
from werkzeug.utils import secure_filename

from zaturn.studio import storage


app = Flask(__name__)
app.config['state'] = storage.load_state()


def wrap(content: str) -> str:
    if request.headers.get('hx-request'):
        return content
    else:
        return render_template('_shell.html', content=content)


@app.route('/')
def home() -> str:
    if app.config['state'].get('api_key'):
        return wrap(render_template('manage_sources.html'))
    else:
        return wrap(render_template('setup_prompt.html'))


@app.route('/settings')
def settings() -> str:
    current_state = app.config['state']
    return wrap(render_template('settings.html', current=current_state))


@app.route('/save_settings', methods=['POST'])
def save_settings() -> str:
    app.config['state']['api_key'] = request.form.get('api_key')
    app.config['state']['api_model'] = request.form.get('api_model')
    app.config['state']['api_endpoint'] = request.form.get('api_endpoint')
    storage.save_state(app.config['state'])
    return render_template('c_settings_updated.html', ts=datetime.now())


@app.route('/upload_datafile', methods=['POST'])
def upload_datafile() -> str:
    datafile = request.files.get('datafile')
    filename = secure_filename(datafile.filename)
    
    saved_path = storage.save_datafile(datafile, filename)
    ext = saved_path.suffix.strip('.').lower()

    app.config['state']['sources'] = app.config['state'].get('sources', {})
    if ext=='csv':
        app.config['state']['sources'][f'{saved_path.stem}-csv'] = {
            'source_type': 'csv',
            'url': str(saved_path),
            'active': True,
        }
    else:
        pass

    storage.save_state(app.config['state'])
    print(app.config['state'])
    
    return wrap(render_template('manage_sources.html'))
    
    
        
