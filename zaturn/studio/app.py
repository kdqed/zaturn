from datetime import datetime
import json

from flask import Flask, make_response, redirect, request, render_template
import httpx
import mistune
import tomli_w
from werkzeug.utils import secure_filename

from zaturn.studio import storage, agent_wrapper
from zaturn.tools import ZaturnTools


app = Flask(__name__)
app.config['state'] = storage.load_state()


def boost(content: str, fallback=None, retarget=None, reswap=None, push_url=None) -> str:
    if request.headers.get('hx-boosted'):
        response = make_response(content)
        if retarget:
            response.headers['hx-retarget'] = retarget
        if reswap:
            response.headers['hx-reswap'] = reswap
        if push_url:
            response.headers['hx-push-url'] = push_url
        return response
    else:
        if fallback:
            return fallback 
        else:
            slugs = storage.list_chats()
            return render_template('_shell.html', content=content, slugs=slugs)


@app.route('/')
def home() -> str:
    state = app.config['state']
    if state.get('api_key') and state.get('sources'):
        return boost(render_template('new_conversation.html'))
    elif state.get('api_key'):
        return boost(render_template('manage_sources.html'))
    else:
        return boost(render_template('setup_prompt.html'))


@app.route('/settings')
def settings() -> str:
    return boost(render_template(
        'settings.html', 
        current = app.config['state'],
        updated = request.args.get('updated'),
    ))


@app.route('/save_settings', methods=['POST'])
def save_settings() -> str:
    app.config['state']['api_key'] = request.form.get('api_key')

    api_model = request.form.get('api_model').strip('/')
    api_endpoint = request.form.get('api_endpoint').strip('/')
    app.config['state']['api_model'] = api_model
    app.config['state']['api_endpoint'] = api_endpoint
    app.config['state']['api_image_input'] = False
    
    try:
        model_info = httpx.get(
            url = f'{api_endpoint}/models/{api_model}/endpoints'
        ).json()
        input_modalities = model_info['data']['architecture']['input_modalities']
        if 'image' in input_modalities:
            app.config['state']['api_image_input'] = True
    except:
        pass
    storage.save_state(app.config['state'])
    return redirect(f'/settings?updated={datetime.now().isoformat().split(".")[0]}')


@app.route('/sources/manage')
def manage_sources() -> str:
    return boost(render_template(
        'manage_sources.html',
        sources = app.config['state'].get('sources', {})
    ))


@app.route('/source/toggle/', methods=['POST'])
def source_toggle_active():
    key = request.form['key']
    new_active = request.form['new_status']=='active'
    app.config['state']['sources'][key]['active'] = new_active
    storage.save_state(app.config['state'])
    
    return boost(
        render_template('c_source_card.html', key=key, active=new_active),
        fallback = redirect('/sources/manage'),
        retarget = f'#source-card-{key}',
        reswap = 'outerHTML',
        push_url = 'false',
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


def get_active_sources():
    sources = {}
    for key in app.config['state']['sources']:
        source = app.config['state']['sources'][key]
        if source['active']:
            sources[key] = source
    return sources


def prepare_chat_for_render(chat):
    fn_calls = {}
    for msg in chat['messages']:
        if msg.get('role')=='assistant':
            if msg.get('tool_calls'):
                msg['is_tool_call'] = True
                for tool_call in msg['tool_calls']:
                    fn_call = tool_call['function']
                    fn_call['arguments'] = tomli_w.dumps(
                        json.loads(fn_call['arguments'])
                    ).replace('\n', '<br>')
                    fn_calls[tool_call['id']] = fn_call
            else:
                msg['html'] = mistune.html(msg['content'])
        if msg.get('role')=='tool':
            msg['call_details'] = fn_calls[msg['tool_call_id']]
            if type(msg['content']) is str:
                msg['html'] = mistune.html(json.loads(msg['text']))
            elif type(msg['content']) is list:
                msg['html'] = ''
                for content in msg['content']:
                    if content['type'] == 'image_url':
                        data_url = content['image_url']['url']
                        msg['html'] += f'<img src="{data_url}">'
                    else:
                        msg['html'] += mistune.html(json.loads(content['text']))
                
    return chat


@app.route('/create_new_chat', methods=['POST'])
def create_new_chat():
    question = request.form['question']
    slug = storage.create_chat(question)
    chat = storage.load_chat(slug)

    state = app.config['state']
    agent = agent_wrapper.Agent(
        endpoint = state['api_endpoint'],
        api_key = state['api_key'],
        model = state['api_model'],
        tools = ZaturnTools(get_active_sources()).tools,
        image_input = state['api_image_input'],
    )
    chat['messages'] = agent.run(chat['messages'])
    storage.save_chat(slug, chat)
    chat = prepare_chat_for_render(chat)
    
    return boost(
        ''.join([
            render_template('nav.html', slugs=storage.list_chats()),
            '<main id="main">',
            render_template('chat.html', chat=chat),
            '</main>'
        ]),
        reswap = 'multi:#sidebar,#main',
        push_url = f'/c/{slug}',
        fallback = redirect(f'/c/{slug}'),
    )


@app.route('/c/<slug>')
def show_chat(slug: str):
    chat = prepare_chat_for_render(storage.load_chat(slug))
    return boost(render_template('chat.html', chat=chat))


@app.route('/follow_up_message', methods=['POST'])
def follow_up_message():
    slug = request.form['slug']
    chat = storage.load_chat(slug)
    chat['messages'].append({
        'role': 'user', 
        'content': request.form['question'],
    })

    state = app.config['state']
    agent = agent_wrapper.Agent(
        endpoint = state['api_endpoint'],
        api_key = state['api_key'],
        model = state['api_model'],
        tools = ZaturnTools(get_active_sources()).tools,
        image_input = state['api_image_input'],
    )
    chat['messages'] = agent.run(chat['messages'])
    storage.save_chat(slug, chat)
    chat = prepare_chat_for_render(chat)

    return boost(
        render_template('chat.html', chat=chat),
        push_url = 'false',
        reswap = 'innerHTML scroll:bottom',
    )
