import os
import vt
import time
import tempfile

from dotenv import load_dotenv
from phishanalyzer.models import Link, Attachment


load_dotenv()

api_key = os.getenv('VIRUSTOTAL_API_KEY')
vt_url = 'https://www.virustotal.com/api/v3'

def send_url_vt(link):
    client = vt.Client(api_key)
    analysis = client.scan_url(link)

    client.close()

    return analysis.id

def send_file_vt(file):
    client = vt.Client(api_key)
    file.open('rb')
    bytes = file.read()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        
        temp_file.write(bytes)
        tmp_path = temp_file.name


    with open(tmp_path, 'rb') as f:
        analysis = client.scan_file(f)

    os.remove(tmp_path)

    client.close()

    return analysis.id

def get_url_vt(analysis_id):
    client = vt.Client(api_key)

    while True:
        analysis = client.get_object("/analyses/{}", analysis_id)
        if analysis.status == "completed":
            analysis_results = analysis.stats
            break
        time.sleep(5)

    client.close()

    return analysis_results

def get_file_vt(analysis_id):
    client = vt.Client(api_key)

    while True:
        analysis = client.get_object("/analyses/{}", analysis_id)
        if analysis.status == "completed":
            analysis_results = analysis.stats
            break
        time.sleep(5)

    client.close()

    return analysis_results
