#!/bin/usr/python3 *
#-*- coding: utf-8 -*-
import requests


def getPublicIpAddress(url):
    data = requests.get(url = url) 
    return data.text

def main():
    # API endpoint, responds the global ip in plaintext
    url = "https://api.ipify.org/?format=text"
    ip_address = getPublicIpAddress(url)


if __name__ == '__main__':
    main()