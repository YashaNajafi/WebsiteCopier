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
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                UserIP TEXT NOT NULL,
                UserAgent TEXT NOT NULL,
                EnteredTime TEXT NOT NULL,
                LastVisitTime TEXT NOT NULL,
                VisitCount INTEGER DEFAULT 1,
                UNIQUE(UserIP, UserAgent)
            )
        """)

        Connection.commit()
        Connection.close()

    def AddUser(self, IP: str, Agent: str):
        Connection = sqlite3.connect(self.Path)
        Cursor = Connection.cursor()
        Current_Time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            # Try to insert new user
            Cursor.execute("""
                INSERT INTO Users (UserIP, UserAgent, EnteredTime, LastVisitTime)
                VALUES (?, ?, ?, ?)
            """, (IP, Agent, Current_Time, Current_Time))
            logging.info("New user added!")

        except sqlite3.IntegrityError:
            Cursor.execute("""
                UPDATE Users
                SET LastVisitTime = ?,
                    VisitCount = VisitCount + 1
                WHERE UserIP = ? AND UserAgent = ?
            """, (Current_Time, IP, Agent))
            logging.info("Existing user visit updated!")

        Connection.commit()
        Connection.close()

    def Count_Of_All_Users(self):
        logging.info("Reading DataBase Data...")
        Connection = sqlite3.connect(self.Path)
        Cursor = Connection.cursor()

        Cursor.execute("""
            SELECT id, UserIP, UserAgent, EnteredTime, LastVisitTime, VisitCount
            FROM Users
        """)

        ALL = Cursor.fetchall()
        Connection.close()

        return ALL
