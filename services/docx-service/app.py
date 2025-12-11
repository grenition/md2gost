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


def docx_to_pdf(docx_path):
    import subprocess
    import base64
    
    pdf_path = docx_path.replace('.docx', '.pdf')
    
    env = os.environ.copy()
    env['HOME'] = '/tmp'
    env['SAL_USE_VCLPLUGIN'] = 'headless'
    env['USER'] = 'root'
    
    try:
        result = subprocess.run(
            [
                'libreoffice',
                '--headless',
                '--nodefault',
                '--nolockcheck',
                '--nologo',
                '--norestore',
                '--convert-to', 'pdf',
                '--outdir', os.path.dirname(docx_path),
                docx_path
            ],
            env=env,
            check=True,
            timeout=60,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(docx_path)
        )
        
        if not os.path.exists(pdf_path):
            stderr_output = result.stderr.decode('utf-8') if result.stderr else 'No stderr'
            raise Exception(f"PDF file was not created. LibreOffice stderr: {stderr_output}")
        
        with open(pdf_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
        
        if len(pdf_data) == 0:
            raise Exception("Generated PDF file is empty")
        
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
        
        try:
            os.unlink(pdf_path)
        except:
            pass
        
        return pdf_base64
    except subprocess.TimeoutExpired:
        raise Exception("PDF conversion timeout")
    except subprocess.CalledProcessError as e:
        stderr_output = e.stderr.decode('utf-8') if e.stderr else str(e)
        stdout_output = e.stdout.decode('utf-8') if e.stdout else ''
        raise Exception(f"PDF conversion failed. Return code: {e.returncode}. Stderr: {stderr_output}. Stdout: {stdout_output}")
    except Exception as e:
        raise Exception(f"PDF conversion error: {str(e)}")


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
            
            pdf_base64 = docx_to_pdf(docx_file_path)
            
            return jsonify({'pdf': pdf_base64})
        finally:
            try:
                os.unlink(md_file_path)
                if os.path.exists(docx_file_path):
                    os.unlink(docx_file_path)
            except:
                pass
                
    except Exception as e:
        import traceback
        error_msg = str(e)
        error_traceback = traceback.format_exc()
        app.logger.error(f"Preview error: {error_msg}\n{error_traceback}")
        return jsonify({'error': error_msg, 'traceback': error_traceback}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

