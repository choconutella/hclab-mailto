class Validator:

    def __init__(self, conn:object, lno:str):
        """
        Class to validate current Lab No.
        """

        self.__lno = lno
        self.__conn = conn


    def  save_log(self, email:str, status:str, msg:str):
        """
        Save log to sine_email_log table

        Parameters:
        email  : email address
        status : email delivery status
        msg    : message email delivery
        """

        stmt = {'email' : email, 'msg' : msg, 'status' : status, 'lno' : self.__lno}

        with self.__conn:
            query = """
                update sine_email_log set email_date = sysdate, email_to = :email, email_log = :msg, email_status = :status
                where email_tno = :lno
            """
            self.__conn.cursor.execute(query, stmt)

            query = """
                insert into sine_email_log (emaiL_date, email_tno, email_to, email_log, email_status)
                select sysdate, :lno, :email, :msg, :status from dual
                where not exists (select 1 from sine_email_log where email_tno = :lno)
            """
            self.__conn.cursor.execute(query,stmt)
    

    def is_repetitive(self):
        """
        Check current number already successfully sent email
        """
        query = "select * from sine_email_log where email_tno = :lno and email_status = 'SENT'"
        stmt = {'lno' : self.__lno}
        
        with self.__conn:
            self.__conn.cursor.execute(query, stmt)
            record = self.__conn.cursor.fetchone()
 
        if not record is None:
            return True

        return False

    
    def validate(self)->tuple[bool,str]:
        """
        Check all validation and generate message
        """

        score = 0
        message = ''

        if not self.is_valid_pid():
            score =+ 1
            message = message + 'MR 00, '
        
        if not self.is_valid_authorise():
            score =+ 1
            message = message + 'Not all test validated yet, '

        if not self.is_valid_test():
            score =+ 1
            message = message + 'Exclude Test Available, '
        
        if not self.is_valid_sample():
            score =+ 1
            message = message + 'Rejected specimen available, '

        if not self.is_valid_source():
            score =+ 1
            message = message + 'Excluded clinic available'
        
        if score == 0:
            return True, 'Success'
        
        return False, message


    def is_valid_pid(self):
        """
        Validation to check patient have valid PID
        """
        query = "select oh_pid from ord_hdr where oh_tno = :lno and oh_pid <> '00'"
        stmt = {'lno' : self.__lno}

        with self.__conn:
            self.__conn.cursor.execute(query,stmt)
            record = self.__conn.cursor.fetchone()

        if not record is None:
            return True
        
        return False

    def is_valid_source(self):
        """
        Validation to check patient source
        """

        query = """
            select substr(specialty_code,2,1) 
            from ord_hdr
            join hfclinic on oh_clinic_code = clinic_code
            where oh_tno = :lno and substr(specialty_code,2,1) = 'Y'
        """
        stmt = {'lno' : self.__lno}
        
        with self.__conn:
            self.__conn.cursor.execute(query, stmt)
            record = self.__conn.cursor.fetchone()
        
        if not record is None:
            return True
        
        return False
        
        
    def is_valid_test(self):
        """
        Validation to check exclude test
        """

        query = "select od_testcode from ord_dtl where od_tno = :lno"
        stmt = {'lno' : self.__lno}

        with self.__conn:
            self.__conn.cursor.execute(query, stmt)
            records = self.__conn.cursor.fetchall()
        
        for record in records:
            if record in self.exclude_tests:
                return False

        return True
        

    def is_valid_authorise(self):
        """
        Validation to check all test already authorise
        """

        query = "select od_testcode from ord_dtl where od_tno = :lno and od_ctl_flag2 is null"
        stmt = {'lno' : self.__lno}

        with self.__conn:
            self.__conn.cursor.execute(query,stmt)
            records = self.__conn.cursor.fetchone()

        if records is None:
            return True
        
        return False


    def is_valid_sample(self):
        """
        Validation to check reject specimen
        """

        query = "select os_spl_type from ord_spl where os_tno = :lno and os_spl_rj_flag = 'Y'"
        stmt = {'lno' : self.__lno}

        with self.__conn:
            self.__conn.cursor.execute(query, stmt)
            records = self.__conn.cursor.fetchone()
        
        if records is None:
            return True
        
        return False
