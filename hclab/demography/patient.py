import logging
import os


class Patient:


    def __init__(self, conn:object, lno:str):
        """
        Class to retrieve patient demography
        """

        self.__lno = lno
        self.__conn = conn


    def name(self)->str:
        """Get patient name"""

        query = "select oh_last_name from ord_hdr where oh_tno = :lno"
        stmt = {'lno' : self.__lno}

        with self.__conn:
            self.__conn.cursor.execute(query,stmt)
            record = self.__conn.cursor.fetchone()

        if not record is None:
            return record[0]
        
        return 'N/A'
        

    def email(self)->str:
        """Get email address from dbemail in cust_master table"""

        query = "select dbemail from cust_master where dbcode in (select oh_pid from ord_hdr where oh_tno = :lno)"
        stmt = {'lno' : self.__lno}

        with self.__conn:
            self.__conn.cursor.execute(query,stmt)
            record = self.__conn.cursor.fetchone()
        
        if not record is None:
            return record[0]
        
        return ''

    def sex(self)->str:
        """Get patient sex info"""

        query = "select oh_sex from ord_hdr where oh_tno = :lno"
        stmt = {'lno' : self.__lno}

        with self.__conn:
            self.__conn.cursor.execute(query, stmt)
            record = self.__conn.cursor.fetchone()

        if not record is None:
            return record[0]
        
        return '0'

    def birth_date(self, date_format:str='ddmmyy')->str:
        """Get patient birth_date data"""

        query = "select to_char(oh_bod,'ddmmyy') from ord_hdrwhere oh_tno = :lno"
        stmt = {'lno' : self.__lno, 'date_format' : date_format}

        with self.__conn:
            self.__conn.cursor.execute(query, stmt)
            record = self.__conn.cursor.fetchone()

        if not record is None:
            return record[0]
        
        return '010100'
        

