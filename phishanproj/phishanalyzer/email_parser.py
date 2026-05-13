from email.header import decode_header
from email.utils import getaddresses, parseaddr
import eml_parser
import base64

from django.core.files.base import ContentFile
from phishanalyzer.models import Attachment, Link
from phishanalyzer.utils import get_file_hash, get_string_hash, get_links_from_email, get_url_id
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

    from_email, to_users, subject = parse_email_data(msg)

    email_obj.email_from = from_email
    email_obj.email_to = to_users
    email_obj.email_subject = subject
    email_obj.save()

    if links:
        for link in links:
            link_id = get_url_id(link)
            new_link = Link(email=email_obj, url=link, vt_url_id=link_id)
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

def parse_email_data(msg):
    def trim(s, limit=99):
        return s[:limit] if s and len(s) > limit else s

    raw_subject = msg.get("Subject")
    decoded_subject = decode_header(raw_subject)

    subject = ''.join(
        part.decode(enc or 'utf-8') if isinstance(part, bytes) else part
        for part, enc in decoded_subject
    )

    raw_from = msg.get("From")
    from_name, from_email = parseaddr(raw_from)

    to_list = getaddresses(msg.get_all("To", []))

    to_users = ''
    for user, address in to_list:
        to_users += address + ', '

    if to_users:
        to_users = to_users[:-2]

    subject = trim(subject)
    to_users = trim(to_users)
    from_email = trim(from_email)

    return from_email, to_users, subject