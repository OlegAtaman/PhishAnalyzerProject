import os
import vt
import time
import tempfile

from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv('VIRUSTOTAL_API_KEY')
vt_url = 'https://www.virustotal.com/api/v3'

def get_file_result_by_hash(hash, client):
    try:
        analysis = client.get_object("/files/{}", hash)
    except:
        return None
    stats = analysis.last_analysis_stats
    return stats

def get_url_result_by_hash(hash, client):
    try:
        analysis = client.get_object("/urls/{}", hash)
    except:
        return None
    stats = analysis.last_analysis_stats
    return stats


def send_url_vt(link, client):
    analysis = client.scan_url(link)
    return analysis.id

def send_file_vt(file, client):
    file.open('rb')
    bytes = file.read()

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        
        temp_file.write(bytes)
        tmp_path = temp_file.name

    with open(tmp_path, 'rb') as f:
        analysis = client.scan_file(f)

    os.remove(tmp_path)

    return analysis.id

def get_result_vt(analysis_id, client):
    while True:
        analysis = client.get_object("/analyses/{}", analysis_id)
        if analysis.status == "completed":
            analysis_results = analysis.stats
            break
        time.sleep(5)
    return analysis_results
