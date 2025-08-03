import os
import vt
import time
import tempfile

from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv('VIRUSTOTAL_API_KEY')
vt_url = 'https://www.virustotal.com/api/v3'

def send_url_vt(link):
    client = vt.Client(api_key)
    analysis = client.scan_url(link)

    while True:
        analysis = client.get_object("/analyses/{}", analysis.id)
        if analysis.status == "completed":
            analysis_results = analysis.stats
            break
        time.sleep(10)

    client.close()

    if analysis_results:
        return analysis_results
    return {}

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

    while True:
        analysis = client.get_object("/analyses/{}", analysis.id)
        if analysis.status == "completed":
            analysis_results = analysis.stats
            break
        time.sleep(10)

    client.close()

    if analysis_results:
        return analysis_results
    return {}