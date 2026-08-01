from flask import Flask, render_template
import sys
import os

# 测试模板路径
template_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
print(f'Template folder: {template_folder}')
print(f'Exists: {os.path.exists(template_folder)}')

app = Flask(__name__, template_folder=template_folder)

with app.app_context():
    try:
        html = render_template('index.html')
        print('Template rendered successfully!')
        print(f'Length: {len(html)}')
    except Exception as e:
        import traceback
        print(f'Error: {e}')
        traceback.print_exc()