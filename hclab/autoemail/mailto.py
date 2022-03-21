import smtplib 
import os 
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase

from email.mime.multipart import MIMEMultipart
from PyPDF2 import PdfFileReader, PdfFileWriter


class Mailto:


    def __init__(self, host, port, name, addr, pswd):

        self.__mymail_host = host
        self.__mymail_port = port
        self.__mymail_name = name
        self.__mymail_addr = addr
        self.__mymail_pswd = pswd
        self.encrypt_dir = 'd:\\hcini\\pdf\\encrypt'
        self.body_html = 'body.html'


    def __encrypt_attachment(self, filename:str, file:str, password:str):
        """
        Encrypt email attachment
        """

        if password == '':
            password = 'M3na12345'


        with open(file, "rb") as in_file:
            input_pdf = PdfFileReader(in_file)
            output_pdf = PdfFileWriter()
            output_pdf.appendPagesFromReader(input_pdf)
            
            output_pdf.encrypt(password,'M3na12345')

            with open(os.path.join(self.encrypt_dir,filename), 'wb') as out_file:
                    output_pdf.write(out_file)


    def send(self, mailaddr, atch_name='', file:str='', atch_password='',  subject=''):
        """
        Send email function
        """
        
        # setup mail header
        msg = MIMEMultipart()
        msg['From'] = self.__mymail_name
        msg['To'] = mailaddr
        msg['Cc'] = self.__mymail_addr
        msg['Subject'] = subject

        # setup mail body
        with open(self.body_html,'r') as f:
            body = f.read()
        msg.attach(MIMEText(body, 'html'))

        # check whether email attachment available
        if file != '':

            self.__encrypt_attachment(atch_name, file, atch_password) 

            attachment = open(os.path.join(self.encrypt_dir,atch_name),'rb')
            p = MIMEBase('application','octet-stream')
            p.set_payload(attachment.read())

            encoders.encode_base64(p)
            p.add_header('Content-Disposition',f'attachment; filename={atch_name}')
            msg.attach(p)

        # warped email message & attachment
        content = msg.as_string()

        # send email
        server = smtplib.SMTP(self.__mymail_host,self.__mymail_port)
        server.starttls()
        server.login(self.__mymail_addr,self.__mymail_pswd)
        server.sendmail(from_addr=self.__mymail_addr,to_addrs=mailaddr,msg=content)

if __name__ == '__main__':
    m = Mailto('adhil.nvndr@gmail.com',attachment='d:\\hcini\\pdf\\20050118.pdf',atch_password='12345678',atch_name='Testing')
    m.send_email()