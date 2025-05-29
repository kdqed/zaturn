from datetime import datetime

from flask import Flask, make_response, redirect, request, render_template
from werkzeug.utils import secure_filename

from zaturn.studio import storage


app = Flask(__name__)
app.config['state'] = storage.load_state()


def wrap(content: str, fallback=None, retarget=None, reswap=None, retain_url=False) -> str:
    if request.headers.get('hx-boosted'):
        response = make_response(content)
        if retarget:
            response.headers['hx-retarget'] = retarget
        if reswap:
            response.headers['hx-reswap'] = reswap
        if retain_url:
            response.headers['hx-push-url'] = 'false'
        return response
    else:
        return fallback or render_template('_shell.html', content=content)


@app.route('/')
def home() -> str:
    state = app.config['state']
    if state.get('api_key') and state.get('sources'):
        return wrap(render_template('new_conversation.html'))
    elif state.get('api_key'):
        return wrap(render_template('manage_sources.html'))
    else:
        return wrap(render_template('setup_prompt.html'))


@app.route('/settings')
def settings() -> str:
    return wrap(render_template(
        'settings.html', 
        current = app.config['state'],
        updated = request.args.get('updated'),
    ))


@app.route('/save_settings', methods=['POST'])
def save_settings() -> str:
    app.config['state']['api_key'] = request.form.get('api_key')
    app.config['state']['api_model'] = request.form.get('api_model')
    app.config['state']['api_endpoint'] = request.form.get('api_endpoint')
    storage.save_state(app.config['state'])
    return redirect(f'/settings?updated={datetime.now().isoformat().split(".")[0]}')


@app.route('/sources/manage')
def manage_sources() -> str:
    return wrap(render_template(
        'manage_sources.html',
        sources = app.config['state'].get('sources', {})
    ))


@app.route('/source/toggle/', methods=['POST'])
def source_toggle_active():
    key = request.form['key']
    new_active = request.form['new_status']=='active'
    app.config['state']['sources'][key]['active'] = new_active
    storage.save_state(app.config['state'])
    
    return wrap(
        render_template('c_source_card.html', key=key, active=new_active),
        fallback = redirect('/sources/manage'),
        retarget = f'#source-card-{key}',
        reswap = 'outerHTML',
        retain_url = True,
    )
    

@app.route('/upload_datafile', methods=['POST'])
def upload_datafile() -> str:
    datafile = request.files.get('datafile')
    filename = secure_filename(datafile.filename)
    
    saved_path = storage.save_datafile(datafile, filename)
    stem = saved_path.stem.replace('.', '_')
    ext = saved_path.suffix.strip('.').lower()

    app.config['state']['sources'] = app.config['state'].get('sources', {})
    if ext in ['csv']:
        app.config['state']['sources'][f'{stem}-csv'] = {
            'source_type': 'csv',
            'url': str(saved_path),
            'active': True,
        }
    elif ext in ['parquet', 'pq']:
        app.config['state']['sources'][f'{stem}-parquet'] = {
            'source_type': 'parquet',
            'url': str(saved_path),
            'active': True,
        }
    elif ext in ['duckdb']:
        app.config['state']['sources'][f'{stem}-duckdb'] = {
            'source_type': 'duckdb',
            'url': str(saved_path),
            'active': True,
        }
    elif ext in ['db', 'sqlite', 'sqlite3']:
        app.config['state']['sources'][f'{stem}-sqlite'] = {
            'source_type': 'sqlite',
            'url': f'sqlite:///{str(saved_path)}',
            'active': True,
        }
    else:
        storage.remove_datafile(saved_path)

    storage.save_state(app.config['state'])
    
    return redirect('/sources/manage')


@app.route('/add_dataurl', methods=['POST'])
def add_dataurl():
    url = request.form['db_url']
    name = url.split('/')[-1].split('?')[0]
    
    if url.startswith("postgresql://"):
        app.config['state']['sources'][f'{name}-postgresql'] = {
            'source_type': 'postgresql',
            'url': url,
            'active': True,
        }
    elif url.startswith("mysql://"):
        app.config['state']['sources'][f'{name}-mysql'] = {
            'source_type': 'mysql',
            'url': url,
            'active': True,
        }
    elif url.startswith("clickhouse://"):
        app.config['state']['sources'][f'{name}-clickhouse'] = {
            'source_type': 'clickhouse',
            'url': url,
            'active': True,
        }
    else:
        pass

    storage.save_state(app.config['state'])
    return redirect('/sources/manage')
    

@app.route('/source/delete', methods=['POST'])
def delete_source():
    key = request.form['key']
    source = app.config['state']['sources'][key]
    if source['source_type'] in ['csv', 'parquet', 'sqlite', 'duckdb']:
        storage.remove_datafile(source['url'])

    del app.config['state']['sources'][key]
    storage.save_state(app.config['state'])
    return redirect('/sources/manage')
        
        
