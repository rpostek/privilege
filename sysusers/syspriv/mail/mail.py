import smtplib
from .. import models
from email.message import EmailMessage
from email.headerregistry import Address


def send_commision(html_content=''):
    try:
        from_addr = models.Config.objects.get(key='commission_mail_from')
        from1, from2 = from_addr.value.split('@')
    except:
        return({'type': 'danger', 'text': "wniosek nie został wysłany\nbrak adresu zwrotnego 'commission_mail_from' w konfiguracji"})

    try:
        to_addr = models.Config.objects.get(key='commission_mail_to')
        to1, to2 = to_addr.value.split('@')
    except:
        return({'type': 'danger', 'text': "wniosek nie został wysłany\nbrak adresu adresata 'commission_mail_to' w konfiguracji"})

    try:
        smtp_server_name = models.Config.objects.get(key='smtp_server').value
    except:
        return({'type': 'danger', 'text': "wniosek nie został wysłany\nbrak adresu serwera SMTP 'smtp_server' w konfiguracji"})

    msg = EmailMessage()
    msg['Subject'] = "Test"
    msg['From'] = Address("IT", from1, from2)
    msg['To'] = (Address("Zatwierdzajacy", to1, to2),)
    msg.set_content("""do odczytania wiadmości potrzeba klienta z HTML\n""")
    msg.add_alternative(html_content, subtype='html')
    # note that we needed to peel the <> off the msgid for use in the html.
    try:
        with smtplib.SMTP(smtp_server_name) as s:
            s.send_message(msg)
        return({'type': 'success', 'text': "wniosek został wysłany na adres " + to_addr.value})
    except:
        return({'type': 'danger', 'text': "wniosek nie został wysłany mailem"})

