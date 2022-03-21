from tkinter import Tk, Label, W, E
import os
import threading
import logging
import time

import application as config
from hclab.autoemail.validator import Validator
from hclab.demography.patient import Patient
from hclab.autoemail.mailto import Mailto
from hclab.connection.oracle import Connection as OraConnect

logging.basicConfig(filename=os.path.join(os.getcwd(),f"logs\\email.log"), level=logging.WARNING, format="%(asctime)s - %(levelname)s : %(message)s")

class AutoMail:

  def __init__(self):
    self.__root = Tk()
    self.__root.title('HCLAB Auto-email')
    self.__root.geometry("570x200")
    self.__root.resizable(0,0)

    self.__label = Label(self.root,anchor="e",font=("Courier",11))
    self.__label.grid(row=1,column=1,padx=2,pady=5,sticky=W+E)
    self.__label.config(text="Starting...")

    self.__start_thread = True
    self.__conn = OraConnect(config.HCLAB_USER, config.HCLAB_PASS, config.HCLAB_HOST)


    try:
      self.__thread = threading.Thread(target=self.process)
      self.__thread.start()
      self.__root.mainloop()
      self.__start_thread = False

    except Exception as e:
      logging.warning(f"Cannot start Thread. {e}")

  
  def process(self):
    
    while True:

      self.__label.config(text="Wait for PDF...")

      for filename in os.listdir(config.PDF_PATH):

        file = os.path.join(config.PDF_PATH,filename)
        if not os.path.isdir(file):

          if file.endswith('.pdf'):

            # adjust lno based filename here
            lno = os.path.splitext(filename)[0].split('_')[3]
            patname = os.path.splitext(filename)[0].split('_')[1]

            # assign default value of variables
            email = ''
            birth_dt = ''
            is_repetitive = False
            is_valid = False
            msg = ''

            self.__label.config(text=f"Processing {lno}")
            print(f"""
------- BEGIN -------
Processing....
File = {file}
To   = {patient.email}
-------  END  -------
            """)

            # get patient data
            try:
              patient = Patient(self.__conn, lno)
            except Exception as e:
              logging.error(e)
              print(e)
              continue
            
            # get validate data
            try:
              validator = Validator(self.__conn, lno)
            except Exception as e:
              logging.error(e)
              print(e)
              continue

            # validating
            if email != '' and email is not None and email.lower() != 'noemail@none.com' and email.lower() != 'tidaktercantum@none.com':
              
              if validator.is_repetitive():
                # same pdf already success sent email
                self.__move_pdf(file, os.path.join(config.PDF_BACKUP,filename))
                break

              is_valid, msg = validator.validate()

              if is_valid:
                # send email here
                subject = 'Hasil Laboratorium ' + patname
                try:
                  self.__send(email, file, birth_dt, lno, subject)
                  validator.save_log(email, 'SENT', msg)
                except Exception as e:
                  logging.error(e)
                  print(e)

              else:
                # insert message email processing with status NOT SENT to sine_email_log here
                try:
                  validator.save_log(email, 'NOT SENT', msg)
                except Exception as e:
                  logging.error(e)
                  print(e)
                  continue
            
            else:
              # insert message email processing with status FAIL to sine_email_log here
              try:
                validator.save_log(email, 'FAIL', 'Email recipient empty')
              except Exception as e:
                logging.error(e)
                print(e)
                continue

          # backup pdf that already processed to temp_pdf folder
          self.__move_pdf(file, os.path.join(config.PDF_BACKUP,filename))
      
        time.sleep(1)

      if self.__start_thread == False:
        break  


  def __move_pdf(self, file:str, dest:str):
    
    try:
        os.remove(dest) # os.rename only cannot overwrite file
    except Exception as e:
        logging.debug(e)
    os.rename(file, dest)


  def __send(self, email:str, file:str, password:str, filename:str, subject:str):

    mail = Mailto(config.EMAIL_HOST, config.EMAIL_PORT, config.EMAIL_NAME, config.EMAIL_ADDRESS, config.EMAIL_PASSWORD)
    mail.send(email, filename, file, password, subject)


