import win32com.client as win32


class OutlookMessage():
    def __init__(self):
        self.style = '''<head>
        <style>
            table, th, td {
              border: 1px solid black;
              border-collapse: collapse;
              padding: 8px;
              font-family: verdana;
            }
            td {
              text-align: right;
            }
            th {
              background-color: #D6EEEE;
            }
        </style>
        </head>
    '''
        self.recipient =  'rpostek@um.warszawa.pl'
        self.subject = 'wniosek o zmianę uprawnień w systemach informatycznych'

    def send_report(self):
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = self.recipient
        mail.Subject = self.subject
        mail.Body = "wniosek"
        mail.HTMLBody = "<html>" + self.style + "<body>" + self.report + "<br><img src=""cid:BW"">" + "<br><img src=""cid:COLOR"">" \
                        + "<br><img src=""cid:pie"">" + self.counters_table() + "</body></html>"
        #this field is optional
        # To attach a file to the email (optional):
        # attachment  = "Path to the attachment"
        # mail.Attachments.Add(attachment)
        attachment = mail.Attachments.Add(r"C:\Users\rpostek\PycharmProjects\druk\bw.png")
        attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "BW")
        attachment = mail.Attachments.Add(r"C:\Users\rpostek\PycharmProjects\druk\c.png")
        attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "COLOR")
        attachment = mail.Attachments.Add(r"C:\Users\rpostek\PycharmProjects\druk\pie.png")
        attachment.PropertyAccessor.SetProperty("http://schemas.microsoft.com/mapi/proptag/0x3712001F", "pie")
        mail.Send()
