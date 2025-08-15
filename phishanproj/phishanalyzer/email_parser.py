import eml_parser
import base64

from django.core.files.base import ContentFile
from phishanalyzer.models import Attachment, Link
from phishanalyzer.utils import get_file_hash, get_string_hash, get_links_from_email
from email import message_from_bytes

def analyze_email(email_file, email_obj):
    with email_file.open('rb') as raw_email:
        new_mail = raw_email.read()

    ep = eml_parser.EmlParser(
        include_attachment_data=True,
        include_raw_body=True
    )
    parsed_eml = ep.decode_email_bytes(new_mail)

    # links = parsed_eml.get("body")[0].get('uri')
    msg = message_from_bytes(new_mail)
    links = get_links_from_email(msg)
    
    print(links)
    if links:
        for link in links:
            link_hash = get_string_hash(link)
            new_link = Link(email=email_obj, url=link, hash_sha256=link_hash)
            new_link.save()

    attachments = []
    for attachment in parsed_eml.get("attachment", []):
        name = attachment.get("filename")
        data = attachment.get("raw")
        if data:
            file_bytes = base64.b64decode(data)
            attachments.append({"filename": name, "data": file_bytes})
        
        attachment_file = ContentFile(file_bytes, name=name)
        attachment_hash = get_file_hash(attachment_file)

        new_attachment = Attachment(email=email_obj, file=attachment_file, hash_sha256=attachment_hash)
        new_attachment.save()