#----------<Library>----------
import sqlite3
import os
import logging
from datetime import datetime
#----------<Functions>----------
class UserManagement:
    def __init__(self, DataBase_Path: str = "DataBase.sqlite"):
        if "." in DataBase_Path:
            DataBase_Path = os.path.join("DataBase",DataBase_Path) if DataBase_Path.split(".")[1] == "sqlite" else DataBase_Path.replace(DataBase_Path.split(".")[1], "sqlite")
        else:
            DataBase_Path = os.path.join("DataBase",f"{DataBase_Path}.sqlite")

        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.Path = DataBase_Path

        if not os.path.exists(self.Path):
            os.makedirs("DataBase")
            with open(self.Path, "x") as file:
                print("DataBase FILE CREATED!")

        self.__TableManagement()

    def __TableManagement(self):
        logging.info("Checking Tables...")
        Connection = sqlite3.connect(self.Path)
        Cursor = Connection.cursor()

        Cursor.execute("""
            CREATE TABLE IF NOT EXISTS Templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                TemplateLink TEXT,
                RltLink TEXT NOT NULL,
                DownloadedTime TEXT NOT NULL,
                Path TEXT NOT NULL
            )
        """)

        Connection.commit()
        Connection.close()

    def AddTemplates(self, RltLink : str,TemplateLink : str,Path : str):
        Connection = sqlite3.connect(self.Path)
        Cursor = Connection.cursor()
        Current_Time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            # Try to insert new user
            Cursor.execute("""
                INSERT INTO Templates (TemplateLink, RltLink, DownloadedTime, Path)
                VALUES (?, ?, ?, ?)
            """, (TemplateLink,RltLink,Current_Time,Path))
            logging.info("New user added!")

        except sqlite3.IntegrityError:
            Cursor.execute("""
                UPDATE Templates
                SET TemplateLink = ?,
                    RltLink = ?,
                WHERE DownloadedTime = ? AND Path = ?
            """, (TemplateLink,RltLink,Current_Time,Path))
            logging.info("Existing user visit updated!")

        Connection.commit()
        Connection.close()

    def Count_Of_All_Users(self):
        logging.info("Reading DataBase Data...")
        Connection = sqlite3.connect(self.Path)
        Cursor = Connection.cursor()

        Cursor.execute("""
            SELECT id, TemplateLink, RltLink, DownloadedTime, Path
            FROM Templates
        """)

        ALL = Cursor.fetchall()
        Connection.close()

        return ALL
