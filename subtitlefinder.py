#!/usr/bin/env python3

from xmlrpc.client import ServerProxy
from sys import argv

import os
import utils
import search
import re
import requests
import logging
import string
import time

import gzip
import shutil

import tkinter as tk
from tkinter import *
from tkinter import Checkbutton, Event, Variable, ttk
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showinfo


logging.basicConfig(filename='subtitlefinder.log', format="%(asctime)s : %(levelname)s : %(message)s", encoding='utf-8', level=logging.INFO)

def get_download_link(file_name):
    os_user = os.environ["OS_USER_NAME"]
    os_password = os.environ["OS_USER_PASSWORD"]
    os_client_user_agent = os.environ["OS_CLIENT_USER_AGENT"]

    with ServerProxy("https://api.opensubtitles.org/xml-rpc") as client:
        login_data = client.LogIn(os_user, os_password, "nl", os_client_user_agent)
        user_token = login_data["token"]
        exact_search_results = search.exactSearch(client, file_name, user_token, login_data["data"])

        if (exact_search_results == "NO_SUBTITLES"):
            return search.textSearch(client, file_name, user_token, login_data["data"], selbox, selkind)
        else:
            return exact_search_results

def save_file(download_link, movie_file_name):
    file_data = requests.get(download_link)    
    match_result = re.search('(?<=attachment; filename=\").+(?=\")', file_data.headers["Content-Disposition"])
    file_name = match_result.group(0)    
    target_file_path = os.path.join(os.path.dirname(movie_file_name), file_name)    
    with open(target_file_path, 'wb') as fd:
        for chunk in file_data.iter_content(chunk_size=128):
            fd.write(chunk)
    return target_file_path

def get_subtitle_ext(saved_file):
    # TODO: Improve this
    d = os.path.dirname(saved_file)
    f = os.path.splitext(os.path.basename(saved_file))[0]
    df = os.path.join(d,f)
    return os.path.splitext(os.path.basename(df))[1]

def extract_file(saved_file, movie_file_name):
    subtitle_file_ext = get_subtitle_ext(saved_file)
    subtitle_file_name = os.path.splitext(os.path.basename(movie_file_name))[0]
    target_subtitle_name = subtitle_file_name + subtitle_file_ext
    with gzip.open(saved_file, 'rb') as f_in:
        with open(os.path.join(os.path.dirname(movie_file_name), target_subtitle_name), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def start_prog():
    your_path = 'D://testmap//'
    files = os.listdir(your_path)
    for file in files:
        if file.endswith(".mkv" or ".mp4"):
            if file.startswith(sellet):    
                file_name = (your_path + file)
                logging.info("-----------------------------")
                logging.info( file)
                print("Getting subtitle download link...")
                download_link = get_download_link(file_name)
                logging.info(download_link)
                if (download_link == "NO_SUBTITLES"):
                    print("No subtitles found for this file","\n")
                    print("-----------------------------------------------","\n")
                    print()
                    time.sleep(1)
                else:
                    print("Downloading subtitle...")
                    saved_file = save_file(download_link, file_name)
                    print("Extracting subtitle...")
                    extract_file(saved_file, file_name)
                    print("Removing zipped file")
                    os.remove(saved_file)
                    print("Subtitle successfully downloaded and extracted!")    
                    print()
                    print("-----------------------------------------------")
                    print()
                    time.sleep(1)
  
def gui():
    
    def checkdot(dot):
        if (dot == "ALL"):
            dot = ""
        return dot
    
    def check_all_par():
        
        global selbox
        global sellet
        global selkind
        
        sellet = str(letter.get())
        selkind = str(moviekind.get())
        if (selkind == "Movies"):
            selkind = "movie"
        elif (selkind == "Series"):
            selkind = "episode"
            
        selbox = int(cbint.get())
        sellet = checkdot(sellet)
        
        start_prog()
        
        
        
    window = tk.Tk()
    
    letter = tk.StringVar()
    moviekind = tk.StringVar()   
    alphabet_string = string.ascii_uppercase
    abclist = list(alphabet_string)
    abclist.insert(0, "ALL")
    cbint = IntVar()  
    
    window.geometry('475x320')
    window.resizable(False, False)
    window.title("SubtitleFinder")
    window.columnconfigure([0, 1, 2], minsize=150)
    window.rowconfigure([0, 1, 2], minsize=50)
    
    label_Opvolging = tk.Label(text="Kies Beginletter:")
    label_Soort = tk.Label(text="FilmSoort:")
    letter_cb = ttk.Combobox(window , textvariable=letter)
    letter_cb.set("ALL")
    moviekind_cb = ttk.Combobox(window, textvariable=moviekind)
    moviekind_cb.set("Movies")
    
    button_Opzoeken = ttk.Button(window, text='Zoeken achter Subtitles', width=25, command=check_all_par)
    checkbox_trusted = Checkbutton(window, text="UnTrusted Subs gebruiken", variable=cbint)
      
    letter_cb['values'] = abclist
    letter_cb['state'] = 'readonly'
    moviekind_cb['values'] = ('Movies', 'Series')
    moviekind_cb['state'] = 'readonly'
    
    label_Opvolging.grid(row=0, column=0, padx=2, pady=10)
    letter_cb.grid(row=0 ,column=1, padx=2, pady=10)
    label_Soort.grid(row=1, column=0, padx=2, pady=10)
    moviekind_cb.grid(row=1, column=1, padx=2, pady=5)
    button_Opzoeken.grid(row=0, column=2, sticky="e", padx=2, pady=10)
    checkbox_trusted.grid(row=2, columnspan=3, padx=2, pady= 10)

    window.mainloop()

gui()