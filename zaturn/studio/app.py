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
    app.config['state']['reasoning_effort'] = request.form.get('reasoning_effort', 'none')
    app.config['state']['system_prompt'] = request.form.get('system_prompt').strip('\n')
    
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
    elif url.startswith("bigquery://"):
        app.config['state']['sources'][f'{name}-bigquery'] = {
            'source_type': 'bigquery',
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
    
    for message in chat['messages']:
        for part in message['parts']:
            if part['part_kind']=='text' and message['kind']=='response':
                part['html_content'] = mistune.html(part['content'])
            elif part['part_kind']=='tool-call':
                fn_calls[part['tool_call_id']] = part
                fn_calls[part['tool_call_id']]['timestamp'] = message['timestamp']
            elif part['part_kind']=='tool-return':
                fn_call = fn_calls[part['tool_call_id']]
                part['call_details'] = {}
                part['call_details']['name'] = fn_call['tool_name']

                t1 = datetime.fromisoformat(fn_call['timestamp'])
                t2 = datetime.fromisoformat(part['timestamp'])
                part['call_details']['exec_time'] = (t2 - t1).seconds

                part['call_details']['args_html'] = tomli_w.dumps(
                    json.loads(fn_call['args'])
                ).replace('\n', '<br>')

                if type(part['content']) is str:
                    part['html_content'] = mistune.html(part['content'])
                elif type(part['content']) is dict and part['content']['type']=='image':
                    data_url = f"data:{part['content']['mimeType']};base64,{part['content']['data']}"
                    part['html_content'] = f'<img src="{data_url}">'
                    

    return chat


@app.route('/create_new_chat', methods=['POST'])
def create_new_chat():
    question = request.form['question']
    slug = storage.create_chat(question)
    chat = storage.load_chat(slug)

    state = app.config['state']
    agent = agent_wrapper.ZaturnAgent(
        endpoint = state['api_endpoint'],
        api_key = state['api_key'],
        model_name = state['api_model'],
        tools = ZaturnTools(get_active_sources()).tools,
        image_input = state['api_image_input'],
        reasoning_effort = state['reasoning_effort'],
        system_prompt = state['system_prompt'],
    )
    chat['messages'] = agent.run(question)
    storage.save_chat(slug, chat)
    
    return boost(
        ''.join([
            render_template('nav.html', slugs=storage.list_chats()),
            '<main id="main">',
            render_template('chat.html', chat=prepare_chat_for_render(chat)),
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
    
    state = app.config['state']
    agent = agent_wrapper.ZaturnAgent(
        endpoint = state['api_endpoint'],
        api_key = state['api_key'],
        model_name = state['api_model'],
        tools = ZaturnTools(get_active_sources()).tools,
        image_input = state['api_image_input'],
        reasoning_effort = state['reasoning_effort'],
        system_prompt = state['system_prompt'],
    )
    
    chat['messages'] = agent.run(
        prompt = request.form['question'],
        message_history = chat['messages'],
    )
    storage.save_chat(slug, chat)
    
    return boost(
        render_template('chat.html', chat=prepare_chat_for_render(chat)),
        push_url = 'false',
        reswap = 'innerHTML scroll:bottom',
    )
