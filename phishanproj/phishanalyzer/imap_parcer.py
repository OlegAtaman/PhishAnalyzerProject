import hashlib, email

from email.header import decode_header
from django.core.files.base import ContentFile

from phishanalyzer.models import Email
from phishanalyzer.utils import generate_string


MARKERS = (
   'Fw:',
   'Fwd:',
    'Analyze email'
)

def scrap_mailbox(boxname, mail_imap_obj):
    found_mail = {}
    mail_imap_obj.select(boxname)

    status, messages = mail_imap_obj.search(None, 'UNSEEN')

    email_ids = messages[0].split()

    print(f"Непрочитаних листів: {len(email_ids)}")

        

    for email_inst in email_ids:
        typ, data = mail_imap_obj.fetch(email_inst, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                msg_bytes = response_part[1]
                msg = email.message_from_bytes(msg_bytes)
                # print(msg.keys())

                subject = decode_header(msg["subject"])
                subject_str = ''.join(
                    part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part
                    for part, encoding in subject
                )



                from_ = msg["from"]
                print('GOT EMAIL:')
                print(f'SUBJECT: {subject_str}')
                print(f'FROM: {from_}')
                if any(marker in subject_str for marker in MARKERS):
                    print(44)
                    new_email_sid = generate_string(30)
                    new_email_hash_sha256 = hashlib.sha256(msg_bytes).hexdigest()
                    
                    new_obj = Email(
                        analys_sid=new_email_sid,
                        hash_sha256=new_email_hash_sha256
                    )

                    new_obj.file.save(
                        f"{new_email_sid}.eml",
                        ContentFile(msg_bytes),
                        save=True
                    )

                found_mail.update({new_obj.id:msg})

    return found_mail