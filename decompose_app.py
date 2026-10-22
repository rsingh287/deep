import os
import ast
import re

def get_function_lines(filepath, func_names):
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    
    tree = ast.parse(source)
    funcs_to_extract = []
    
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in func_names:
            has_route = any(isinstance(d, ast.Call) and getattr(d.func, 'attr', '') == 'route' for d in node.decorator_list)
            if not has_route:
                has_route = any(isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == 'route' for d in node.decorator_list)
            
            if has_route:
                start_line = node.lineno - 1
                if node.decorator_list:
                    start_line = node.decorator_list[0].lineno - 1
                end_line = node.end_lineno
                funcs_to_extract.append((start_line, end_line, node.name))
                
    funcs_to_extract.sort(key=lambda x: x[0], reverse=True)
    
    lines = source.splitlines()
    extracted_codes = []
    for start, end, name in funcs_to_extract:
        func_lines = lines[start:end]
        extracted_codes.append('\n'.join(func_lines))
        del lines[start:end]
        
    return '\n'.join(lines), extracted_codes

chat_funcs = ['manage_chats', 'chat_detail', 'chat', 'swarm_chat', 'chat_with_image']
vision_funcs = ['webcam_capture', 'api_screen_analyze', 'api_screen_record_start', 'api_screen_record_stop', 'api_screen_record_status', 'take_screenshot', 'api_screen_capture', 'vision_inspect_hardware_api', 'vision_live_stream_frame_api', 'vision_sign_language_api', 'vision_facial_expression_api', 'vision_mediapipe_kinematics_api', 'video_feed', 'set_vision_mode', 'ocr_screen_scan']
system_funcs = ['get_active_window', 'get_weather', 'run_macro', 'get_system_version', 'get_system_metrics', 'volume_control', 'brightness_control', 'kill_process', 'system_open_url', 'get_system_stats']
hardware_funcs = ['detect_pickit3_hardware', 'mplab_inject_code', 'mplab_launch_gui', 'get_hardware_preset_code', 'kasa_toggle_api', 'kasa_status_api']

categories = {
    'chat': chat_funcs,
    'vision': vision_funcs,
    'system': system_funcs,
    'hardware': hardware_funcs
}

app_path = 'app.py'
os.makedirs('routes', exist_ok=True)
with open('routes/__init__.py', 'w') as f:
    f.write('')

for cat, funcs in categories.items():
    new_source, extracted = get_function_lines(app_path, funcs)
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(new_source)
    
    bp_code = f"from flask import Blueprint, request, jsonify, render_template, current_app, Response\nimport os, json, subprocess, requests, base64, time, cv2\n"
    bp_code += "from app import db_engine, DB_PATH, OLLAMA_API\n"
    bp_code += f"\n{cat}_bp = Blueprint('{cat}', __name__)\n\n"
    
    # reverse because they were extracted in reverse order
    for code in reversed(extracted):
        code = code.replace('@app.route', f'@{cat}_bp.route')
        bp_code += code + "\n\n"
        
    with open(f'routes/{cat}.py', 'w', encoding='utf-8') as f:
        f.write(bp_code)

with open(app_path, 'r', encoding='utf-8') as f:
    app_source = f.read()

import_lines = """
from routes.chat import chat_bp
from routes.vision import vision_bp
from routes.system import system_bp
from routes.hardware import hardware_bp
app.register_blueprint(chat_bp)
app.register_blueprint(vision_bp)
app.register_blueprint(system_bp)
app.register_blueprint(hardware_bp)
"""

match = re.search(r'^if __name__ == [\'"]__main__[\'"]:\s*$', app_source, flags=re.MULTILINE)
if match:
    idx = match.start()
    app_source = app_source[:idx] + import_lines + "\n" + app_source[idx:]
    with open(app_path, 'w', encoding='utf-8') as f:
        f.write(app_source)
else:
    with open(app_path, 'a', encoding='utf-8') as f:
        f.write(import_lines)

print("Decomposition completed successfully!")
