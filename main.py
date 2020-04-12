#!/bin/usr/python3 *
#-*- coding: utf-8 -*-
import os
import sys
import json
import logging
import requests
from datetime import datetime


# Global const.
LOGGING_PATH = "/scripts/wmIP_v2/wmip_v2.log"   # Logs are stored here.
STORAGE_PATH = "/scripts/wmIP_v2/storage.json"  # Track all the changes.
ENDPOINT = "https://api.ipify.org/?format=text" # API Endpoint.


def panic(err_msg, err_code):
    """
        This funciton gets called to terminate the program properly.
        It writes error logs and exits the program in the correct way.
        :param err_msg: the passed error
        :param err_code: the error code
        :return: None
    """
    if err_code == 0:
        # Not an error, more like an info.
        logger.info(str(err_msg))
    elif err_code == 2:
        logger.critical(str(err_msg))
    else:
        logger.error(str(err_msg))
    try:
        # Check if error code is an integer.
        int(err_code)
        sys.exit(err_code)
    except:
        sys.exit(1)


class Address:
    def __init__(self, url, storage):
        self.url = url
        self.storage = storage
        self.public_ip = ""
        self.latest_ip = ""
        self.latest_id = ""
        self.first_run = False

    def createStore(self):
        """
            Create the store.json file if not exists.
            :param self: self.storage
            :return: Boolean
        """
        if not os.path.exists(self.storage):
            try:
                f = open(self.storage, 'w')
                f.close()
            except IOError as io:
                # Could not create the file.
                logger.error(f"Couldn't create file ({self.storage}). Error: {str(io)}")
                return False
            except Exception as ex:
                logger.critical(f"Something unexpected happened. Error: {str(io)}")
                return False
        return True

    def getPublicAddress(self):
        """
            Make an API request and retrieve the public ip address.
            When the log level is set to DEBUG, the requests pack logs too.
            :param self: self.publicIp
            :return: None
        """
        try:
            data = requests.get(url = self.url)
        except:
            panic("Something went wrong with gathering the public IP, please check your internet connection and try again.", 1)
        if data.status_code == 200: # Check if response is ok (200).
            self.public_ip = data.text
            logger.debug(f"[{data.status_code}] - {data.text}")
        else:
            panic(f"Could not get public ip. Status code: {data.status_code}", 1)

    def getLatestEntry(self):
        """
            Loads the storage.json and retrieves the latest entry (eg. latest ip).
            :param self: self.storage
            :param self: self.latest_ip
            :return: None
        """
        if os.path.exists(self.storage):
            if os.stat(self.storage).st_size != 0:  # Check if the file is empty.
                try:
                    with open(self.storage, "r") as file:
                        data = json.load(file)
                except IOError as io:
                    logger.error(f"File is currently busy, please close the storage file and try it again. (Path: {self.storage})")
                    panic(io, 1)
                except Exception as ex:
                    panic(f"Something bad happened, please try again. error: {ex}", 1)
            else:
                self.first_run = True
        else:
            self.first_run = True   # Identify the programs first run.
            i = 0
            tries = 3
            success = False
            while i < tries:    # Try to create the file n times.
                if Address.createStore(self):
                    i = 3
                    success = True
                    logger.info("Data storage successfully created.")
                else:
                    i = i+1
                    logger.info(f"[{i}/{tries}] - couldn't create storage file.")
            if not success:
                panic(f"Something went wrong while gathering information, please check the logs and try again.", 1)
        if not self.first_run:  # Check if it's the first run.
            latest_id = "0"
            for d in data:  # Check latest_id based on id value and not based on order.
                try:
                    if d > latest_id:
                        latest_id = d
                except:
                    logger.error(f"Something is wrong with the storage.json file. Could not load '{str(d)}', please fix the data and try again. This problem is beeing ignored.")
            try:
                self.latest_ip = data[latest_id]['ip']
            except TypeError as te: 
                # This error occurs when the storage.json index type is modified. (str -> int)
                panic(f"TypeError occured. Please check the storage.json if the file is formatted correctly. error: {te}", 1)
            self.latest_id = latest_id
            logger.debug(f"Latest entry: {data[latest_id]}")
        else:   # If the program is executed the first time, the program needs "dummy data" for further instructions.
            self.latest_ip = "1.1.1.1"
            self.latest_id = "0"

    def addNewEntry(self):
        """
            Create a new entry with the new public ip.
            :para self: self.latest_ip
            :para self: self.public_ip
            :para self: self.storage
            :return: None
        """
        _id = int(self.latest_id) + 1   # Up the id by 1.
        now = datetime.now()    # Get the NOW datetime.
        newEntry = {
            str(_id): {
                '_id': _id,
                '_date': now.strftime("%d.%m.%Y, %H:%M:%S"),
                '_timestamp': datetime.timestamp(now),
                'ip': self.public_ip
            }
        }
        if not self.first_run:
            try:
                with open(self.storage, 'r') as file:
                    data = json.load(file)
            except:
                panic("Could not read storage.json. Make sure the file exists and isn't open.", 1)
            data.update(newEntry)   # Update (append) the storage content.
        else:
            data = newEntry
        try:
            with open(self.storage, 'w') as file:
                json.dump(data, file)
        except IOError as io:
            panic(io, 1)
        except Exception as ex:
            panic(ex, 1)
        logger.info(f"New entry: {newEntry}")

def main():
    addr = Address(ENDPOINT, STORAGE_PATH)
    addr.getPublicAddress()
    addr.getLatestEntry()

    # DEBUG - dump all class assigned values
    logger.debug(f"Init values:\n-> url: {addr.url}\n-> storage: {addr.storage}\n-> public_ip: {addr.public_ip}\n-> latest_ip: {addr.latest_ip}\n-> first_run: {addr.first_run}")
    
    if addr.public_ip != addr.latest_ip:
        addr.addNewEntry()
    else:
        logger.info("Nothing has changed.")
    logger.info("Done. Program exits.")
    sys.exit(0)


if __name__ == '__main__':
    try:
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(filename=LOGGING_PATH, level=logging.INFO, format=log_format)
        logger = logging.getLogger()
    except:
        print("Could not setup the logger, exiting the program.")
        sys.exit(1)
    main()
