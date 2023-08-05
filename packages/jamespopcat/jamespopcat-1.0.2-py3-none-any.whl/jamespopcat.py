# ===============================================================
# Copyright © [2023] [ctrcrk]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================
#
# Nama Program: jamespopcat.py
# Deskripsi  : [Auto click Popcat/Jamespopcat]
#
# Pembuat    : [jamess.wee]
# Tanggal    : [12/05/2023]
# Versi      : [v1.0.2]
#
# Copyright © [2023] [ctrcrk]
# ===============================================================


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import os
import time
import psutil
options = Options()
options.add_argument("--mute-audio")
options.add_argument('--disable-web-security')
options.add_argument('--log-level=3')
jumlah_tab = 1
bodies = []
def add_tab():
    driver.execute_script("window.open('https://popcat.click/','_blank');")
    driver.switch_to.window(driver.window_handles[-1])
    body = driver.find_element("tag name", "body")
    bodies.append((driver.current_window_handle, body))
    print("Tab ke-", len(bodies), "dengan ID:", driver.current_window_handle, "berhasil ditambahkan.")
def get_cpu_color(cpu_percent):
    if cpu_percent <= 20:
        return "\033[38;2;0;255;0m"
    elif cpu_percent <= 50:
        return "\033[38;2;255;255;0m"
    elif cpu_percent <= 80:
        return "\033[38;2;255;165;0m"
    else:
        return "\033[38;2;255;0;0m"
def click_all_tabs():
    counts = [0] * len(bodies)
    try:
        while True:
            for i in range(len(bodies)):
                driver.switch_to.window(bodies[i][0])
                bodies[i][1].send_keys(Keys.SPACE)
                counts[i] += 1
                time.sleep(waktu_klik)
            if sum(counts) % 100 == 0:
                total_clicks = sum(counts)
                formatted_total_clicks = format(total_clicks, ",d").replace(",", ".")
                cpu_percent = psutil.cpu_percent()
                cpu_color = get_cpu_color(cpu_percent)
                print(f"\r\033[38;5;208mTotal jumlah klik saat ini:\033[0m \033[37m{formatted_total_clicks}\033[0m | CPU: {cpu_color}{cpu_percent}%\033[0m", end="")
    except KeyboardInterrupt:
        total_clicks = sum(counts)
    formatted_total_clicks = format(total_clicks, ",d").replace(",", ".")
    os.system('clear')
    os.system('cls')
    print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Selamat datang di program auto click Popcat! ┃
┃                                              ┃
┃\033[94m   █ ▄▀█ █▀▄▀█ █▀▀ █▀ █▀█ █▀█ █▀█ █▀▀ ▄▀█ ▀█▀\033[0m ┃
┃\033[94m █▄█ █▀█ █ ▀ █ ██▄ ▄█ █▀▀ █▄█ █▀▀ █▄▄ █▀█  █ \033[0m ┃
┃──────────────────────────────────────────────┃
┃         https://bio.link/ctrcrk              ┃
┃──────────────────────────────────────────────┃
┃ support chrome version 113 (32/64 bit)       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n""")
    print("\nProgram Stopd\033[31m ● \033[0m")
    print("\n\033[32m ● \033[0mTab yang digunakan:", jumlah_tab, "Tab")
    print("\n\033[32m ● \033[0mWaktu klik:", waktu_klik, huruf_waktu) 
    print(f"\n\033[38;5;208mTotal KLIK:\033[0m \033[37m{formatted_total_clicks}\033[0m\n\n\n")
os.system('clear')
os.system('cls')
print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Selamat datang di program auto click Popcat! ┃
┃                                              ┃
┃\033[94m   █ ▄▀█ █▀▄▀█ █▀▀ █▀ █▀█ █▀█ █▀█ █▀▀ ▄▀█ ▀█▀\033[0m ┃
┃\033[94m █▄█ █▀█ █ ▀ █ ██▄ ▄█ █▀▀ █▄█ █▀▀ █▄▄ █▀█  █ \033[0m ┃
┃──────────────────────────────────────────────┃
┃         https://bio.link/ctrcrk              ┃
┃──────────────────────────────────────────────┃
┃ support chrome version 113 (32/64 bit)       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n""")
while True:
    try:
        jumlah_tab = int(input("\n\033[33m ● \033[0mMasukkan jumlah tab yang diinginkan: "))
        os.system('clear')
        os.system('cls')
        if jumlah_tab < 1:
            raise ValueError
        print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Selamat datang di program auto click Popcat! ┃
┃                                              ┃
┃\033[94m   █ ▄▀█ █▀▄▀█ █▀▀ █▀ █▀█ █▀█ █▀█ █▀▀ ▄▀█ ▀█▀\033[0m ┃
┃\033[94m █▄█ █▀█ █ ▀ █ ██▄ ▄█ █▀▀ █▄█ █▀▀ █▄▄ █▀█  █ \033[0m ┃
┃──────────────────────────────────────────────┃
┃         https://bio.link/ctrcrk              ┃
┃──────────────────────────────────────────────┃
┃ support chrome version 113 (32/64 bit)       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n""")
        print("\n\033[32m ● \033[0mMasukkan jumlah tab yang diinginkan:",jumlah_tab, "Tab")
        break
    except ValueError:
        os.system('clear')
        os.system('cls')
        print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Selamat datang di program auto click Popcat! ┃
┃                                              ┃
┃\033[94m   █ ▄▀█ █▀▄▀█ █▀▀ █▀ █▀█ █▀█ █▀█ █▀▀ ▄▀█ ▀█▀\033[0m ┃
┃\033[94m █▄█ █▀█ █ ▀ █ ██▄ ▄█ █▀▀ █▄█ █▀▀ █▄▄ █▀█  █ \033[0m ┃
┃──────────────────────────────────────────────┃
┃         https://bio.link/ctrcrk              ┃
┃──────────────────────────────────────────────┃
┃ support chrome version 113 (32/64 bit)       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n""")      
        print("\033[31mJumlah tab harus berupa bilangan bulat positif!\033[0m")
while True:
    try:
        waktu_klik_input = input("\n\033[33m ● \033[0mMasukkan waktu klik atau 'skip' untuk tidak menggunakan waktu klik: ")
        if waktu_klik_input.lower() == "skip":
            waktu_klik = 0
            huruf_waktu = "Milidetik"
            os.system('clear')
            os.system('cls')
            print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Selamat datang di program auto click Popcat! ┃
┃                                              ┃
┃\033[94m   █ ▄▀█ █▀▄▀█ █▀▀ █▀ █▀█ █▀█ █▀█ █▀▀ ▄▀█ ▀█▀\033[0m ┃
┃\033[94m █▄█ █▀█ █ ▀ █ ██▄ ▄█ █▀▀ █▄█ █▀▀ █▄▄ █▀█  █ \033[0m ┃
┃──────────────────────────────────────────────┃
┃         https://bio.link/ctrcrk              ┃
┃──────────────────────────────────────────────┃
┃ support chrome version 113 (32/64 bit)       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n""")
            print("\n\033[32m ● \033[0mMasukkan jumlah tab yang diinginkan:",jumlah_tab, "Tab")
            print("\n\033[32m ● \033[0mMasukkan waktu klik atau 'skip' untuk tidak menggunakan waktu klik:", waktu_klik, huruf_waktu)
            break
        waktu_klik = float(waktu_klik_input)
        if waktu_klik <= 0.4:
            waktu_klik = 0
            huruf_waktu = "milidetik"
            os.system('clear')
            os.system('cls')
            print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Selamat datang di program auto click Popcat! ┃
┃                                              ┃
┃\033[94m   █ ▄▀█ █▀▄▀█ █▀▀ █▀ █▀█ █▀█ █▀█ █▀▀ ▄▀█ ▀█▀\033[0m ┃
┃\033[94m █▄█ █▀█ █ ▀ █ ██▄ ▄█ █▀▀ █▄█ █▀▀ █▄▄ █▀█  █ \033[0m ┃
┃──────────────────────────────────────────────┃
┃         https://bio.link/ctrcrk              ┃
┃──────────────────────────────────────────────┃
┃ support chrome version 113 (32/64 bit)       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n""")
            print("\n\033[32m ● \033[0mMasukkan jumlah tab yang diinginkan:",jumlah_tab, "Tab")
            print("\n\033[32m ● \033[0mMasukkan waktu klik atau 'skip' untuk tidak menggunakan waktu klik:", waktu_klik, huruf_waktu)
        elif waktu_klik <= 0.9:
            waktu_klik = waktu_klik
            huruf_waktu = "milidetik"
            os.system('clear')
            os.system('cls')
            print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Selamat datang di program auto click Popcat! ┃
┃                                              ┃
┃\033[94m   █ ▄▀█ █▀▄▀█ █▀▀ █▀ █▀█ █▀█ █▀█ █▀▀ ▄▀█ ▀█▀\033[0m ┃
┃\033[94m █▄█ █▀█ █ ▀ █ ██▄ ▄█ █▀▀ █▄█ █▀▀ █▄▄ █▀█  █ \033[0m ┃
┃──────────────────────────────────────────────┃
┃         https://bio.link/ctrcrk              ┃
┃──────────────────────────────────────────────┃
┃ support chrome version 113 (32/64 bit)       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n""")
            print("\n\033[32m ● \033[0mMasukkan jumlah tab yang diinginkan:",jumlah_tab, "Tab")
            print("\n\033[32m ● \033[0mMasukkan waktu klik atau 'skip' untuk tidak menggunakan waktu klik:", waktu_klik, huruf_waktu)
        else:
            waktu_klik = int(waktu_klik) if waktu_klik.is_integer() else waktu_klik
            huruf_waktu = "detik"
            os.system('clear')
            os.system('cls')
            print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Selamat datang di program auto click Popcat! ┃
┃                                              ┃
┃\033[94m   █ ▄▀█ █▀▄▀█ █▀▀ █▀ █▀█ █▀█ █▀█ █▀▀ ▄▀█ ▀█▀\033[0m ┃
┃\033[94m █▄█ █▀█ █ ▀ █ ██▄ ▄█ █▀▀ █▄█ █▀▀ █▄▄ █▀█  █ \033[0m ┃
┃──────────────────────────────────────────────┃
┃         https://bio.link/ctrcrk              ┃
┃──────────────────────────────────────────────┃
┃ support chrome version 113 (32/64 bit)       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n""")
            print("\n\033[32m ● \033[0mMasukkan jumlah tab yang diinginkan:",jumlah_tab, "Tab")
            print("\n\033[32m ● \033[0mMasukkan waktu klik atau 'skip' untuk tidak menggunakan waktu klik:", waktu_klik, huruf_waktu)
        break
    except ValueError:
            os.system('clear')
            os.system('cls')
            print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Selamat datang di program auto click Popcat! ┃
┃                                              ┃
┃\033[94m   █ ▄▀█ █▀▄▀█ █▀▀ █▀ █▀█ █▀█ █▀█ █▀▀ ▄▀█ ▀█▀\033[0m ┃
┃\033[94m █▄█ █▀█ █ ▀ █ ██▄ ▄█ █▀▀ █▄█ █▀▀ █▄▄ █▀█  █ \033[0m ┃
┃──────────────────────────────────────────────┃
┃         https://bio.link/ctrcrk              ┃
┃──────────────────────────────────────────────┃
┃ support chrome version 113 (32/64 bit)       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n""")
            print("\n\033[32m ● \033[0mMasukkan jumlah tab yang diinginkan:",jumlah_tab, "Tab")
            print("\n\033[31mInput harus berupa angka.\033[0m")
headless_input = ''
while True:
    headless_input = input("\n\033[33m ● \033[0mApakah Anda ingin menjalankan klik dalam mode headless? (y/n): ")
    if headless_input.lower() == 'y' or headless_input.lower() == 'n':
        os.system('clear')
        os.system('cls')
        print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Selamat datang di program auto click Popcat! ┃
┃                                              ┃
┃\033[94m   █ ▄▀█ █▀▄▀█ █▀▀ █▀ █▀█ █▀█ █▀█ █▀▀ ▄▀█ ▀█▀\033[0m ┃
┃\033[94m █▄█ █▀█ █ ▀ █ ██▄ ▄█ █▀▀ █▄█ █▀▀ █▄▄ █▀█  █ \033[0m ┃
┃──────────────────────────────────────────────┃
┃         https://bio.link/ctrcrk              ┃
┃──────────────────────────────────────────────┃
┃ support chrome version 113 (32/64 bit)       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n""")
        print("\n\033[32m ● \033[0mMasukkan jumlah tab yang diinginkan:",jumlah_tab, "Tab")
        print("\n\033[32m ● \033[0mMasukkan waktu klik atau 'skip' untuk tidak menggunakan waktu klik:", waktu_klik, huruf_waktu)          
        print("\n\033[32m ● \033[0mApakah Anda ingin menjalankan klik dalam mode headless? (y/n):", headless_input)
        break
    else:
        os.system('clear')
        os.system('cls')
        print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Selamat datang di program auto click Popcat! ┃
┃                                              ┃
┃\033[94m   █ ▄▀█ █▀▄▀█ █▀▀ █▀ █▀█ █▀█ █▀█ █▀▀ ▄▀█ ▀█▀\033[0m ┃
┃\033[94m █▄█ █▀█ █ ▀ █ ██▄ ▄█ █▀▀ █▄█ █▀▀ █▄▄ █▀█  █ \033[0m ┃
┃──────────────────────────────────────────────┃
┃         https://bio.link/ctrcrk              ┃
┃──────────────────────────────────────────────┃
┃ support chrome version 113 (32/64 bit)       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n""")
        print("\n\033[32m ● \033[0mMasukkan jumlah tab yang diinginkan:",jumlah_tab, "Tab")
        print("\n\033[32m ● \033[0mMasukkan waktu klik atau 'skip' untuk tidak menggunakan waktu klik:", waktu_klik, huruf_waktu)        
        print("\n\033[31mInput tidak valid y = iya n = tidak\033[0m")
        continue
if headless_input.lower() == 'y':
    options.add_argument('--headless')
while True:
    start = input("\n\033[33m ● \033[0mKetik 'start' untuk memulai: ")
    try:
        if start.lower() == "start":
            os.system('clear')
            os.system('cls')
            print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Selamat datang di program auto click Popcat! ┃
┃                                              ┃
┃\033[94m   █ ▄▀█ █▀▄▀█ █▀▀ █▀ █▀█ █▀█ █▀█ █▀▀ ▄▀█ ▀█▀\033[0m ┃
┃\033[94m █▄█ █▀█ █ ▀ █ ██▄ ▄█ █▀▀ █▄█ █▀▀ █▄▄ █▀█  █ \033[0m ┃
┃──────────────────────────────────────────────┃
┃         https://bio.link/ctrcrk              ┃
┃──────────────────────────────────────────────┃
┃ support chrome version 113 (32/64 bit)       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n""")
            print("\n\033[32m ● \033[0mMasukkan jumlah tab yang diinginkan:",jumlah_tab, "Tab")
            print("\n\033[32m ● \033[0mMasukkan waktu klik atau 'skip' untuk tidak menggunakan waktu klik:", waktu_klik, huruf_waktu)
            print("\n\033[32m ● \033[0mApakah Anda ingin menjalankan klik dalam mode headless? (y/n):", headless_input)
            print("\n\033[32m ● \033[0mProgram berhasil dimulai.")
            break
        else:
            raise ValueError
    except ValueError:
        print("\033[31mInput tidak dikenali.\033[0m ")
        os.system('clear')
        os.system('cls')
        print("""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Selamat datang di program auto click Popcat! ┃
┃                                              ┃
┃\033[94m   █ ▄▀█ █▀▄▀█ █▀▀ █▀ █▀█ █▀█ █▀█ █▀▀ ▄▀█ ▀█▀\033[0m ┃
┃\033[94m █▄█ █▀█ █ ▀ █ ██▄ ▄█ █▀▀ █▄█ █▀▀ █▄▄ █▀█  █ \033[0m ┃
┃──────────────────────────────────────────────┃
┃         https://bio.link/ctrcrk              ┃
┃──────────────────────────────────────────────┃
┃ support chrome version 113 (32/64 bit)       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n""")
        print("\n\033[32m ● \033[0mMasukkan jumlah tab yang diinginkan:",jumlah_tab, "Tab") 
        print("\n\033[32m ● \033[0mMasukkan waktu klik atau 'skip' untuk tidak menggunakan waktu klik:", waktu_klik, huruf_waktu)
        print("\n\033[32m ● \033[0mApakah Anda ingin menjalankan klik dalam mode headless? (y/n):", headless_input)
        print("\n\033[31mInput tidak dikenali klik 'start' untuk memulai.\033[0m ")
driver = webdriver.Chrome(options=options)
driver.get("https://popcat.click/")
body = driver.find_element("tag name", "body")
bodies.append((driver.current_window_handle, body))
print("Tab pertama dengan ID:", driver.current_window_handle,"berhasil ditambahkan.")
for i in range(jumlah_tab - 1):
    add_tab()
print("\nProgram Aktif\033[32m ● \033[0m")
click_all_tabs()

