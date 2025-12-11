import os
import tempfile
import io
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from md2gost.converter import Converter

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

TEMPLATE_PATH = os.getenv('TEMPLATE_PATH', os.path.join(parent_dir, 'md2gost', 'Template.docx'))
if not os.path.exists(TEMPLATE_PATH):
    TEMPLATE_PATH = os.path.join('/app', 'md2gost', 'Template.docx')


def docx_to_html(docx_path):
    import mammoth
    
    with open(docx_path, "rb") as docx_file:
        result = mammoth.convert_to_html(docx_file)
        html_content = result.value
        
    css_style = '''<style>
        body { 
            font-family: 'Times New Roman', 'Liberation Serif', serif; 
            font-size: 14pt; 
            line-height: 1.5; 
            margin: 2cm 3cm 2cm 1.5cm;
            text-align: justify;
        }
        h1, h2, h3, h4, h5, h6 { 
            font-weight: bold; 
            margin-top: 1em; 
            margin-bottom: 0.5em;
        }
        h1 { font-size: 16pt; }
        h2 { font-size: 15pt; }
        h3 { font-size: 14pt; }
        p { margin: 0.5em 0; text-indent: 1.25cm; }
        table { border-collapse: collapse; width: 100%; margin: 1em 0; }
        table td, table th { border: 1px solid black; padding: 4pt; }
        img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
    </style>'''
    
    return f'<html><head><meta charset="UTF-8">{css_style}</head><body>{html_content}</body></html>'


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'docx-service'}), 200


@app.route('/api/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json()
        markdown_content = data.get('markdown', '')
        syntax_highlighting = data.get('syntax_highlighting', True)
        
        if not markdown_content:
            return jsonify({'error': 'Markdown content is required'}), 400
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as md_file:
            md_file.write(markdown_content)
            md_file_path = md_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as docx_file:
            docx_file_path = docx_file.name
        
        try:
            working_dir = os.path.dirname(md_file_path)
            os.environ['WORKING_DIR'] = working_dir
            if syntax_highlighting:
                os.environ['SYNTAX_HIGHLIGHTING'] = '1'
            else:
                os.environ.pop('SYNTAX_HIGHLIGHTING', None)
            
            converter = Converter(md_file_path, docx_file_path, TEMPLATE_PATH, debug=False)
            converter.convert()
            
            doc = converter.document
            from getpass import getuser
            try:
                doc.core_properties.author = getuser()
            except:
                doc.core_properties.author = "md2gost"
            doc.core_properties.comments = "Created with md2gost web service"
            
            doc.save(docx_file_path)
            
            with open(docx_file_path, 'rb') as f:
                output = io.BytesIO(f.read())
            output.seek(0)
            
            response = send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                as_attachment=True,
                download_name='document.docx'
            )
            response.headers['Content-Disposition'] = 'attachment; filename=document.docx'
            return response
        finally:
            try:
                os.unlink(md_file_path)
                if os.path.exists(docx_file_path):
                    os.unlink(docx_file_path)
            except:
                pass
                
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/preview', methods=['POST'])
def preview():
    try:
        data = request.get_json()
        markdown_content = data.get('markdown', '')
        syntax_highlighting = data.get('syntax_highlighting', True)
        
        if not markdown_content:
            return jsonify({'error': 'Markdown content is required'}), 400
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as md_file:
            md_file.write(markdown_content)
            md_file_path = md_file.name
        
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as docx_file:
            docx_file_path = docx_file.name
        
        try:
            working_dir = os.path.dirname(md_file_path)
            os.environ['WORKING_DIR'] = working_dir
            if syntax_highlighting:
                os.environ['SYNTAX_HIGHLIGHTING'] = '1'
            else:
                os.environ.pop('SYNTAX_HIGHLIGHTING', None)
            
            converter = Converter(md_file_path, docx_file_path, TEMPLATE_PATH, debug=False)
            converter.convert()
            
            doc = converter.document
            from getpass import getuser
            try:
                doc.core_properties.author = getuser()
            except:
                doc.core_properties.author = "md2gost"
            doc.core_properties.comments = "Created with md2gost web service"
            
            doc.save(docx_file_path)
            
            html_content = docx_to_html(docx_file_path)
            
            return jsonify({'html': html_content})
        finally:
            try:
                os.unlink(md_file_path)
                if os.path.exists(docx_file_path):
                    os.unlink(docx_file_path)
            except:
                pass
                
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

