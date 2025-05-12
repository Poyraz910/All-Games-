import tkinter as tk
from tkinter import messagebox
import json
import random
import math
import time
import os

# Sabitler
UPDATE_INTERVAL = 1000
EVAPORATION_TIME = 10
URANYUM_ISI = 20
TORYUM_ISI = 10
PLUTONYUM_ISI = 200
ANTIMADDE_ISI = 5000
SU_SOGUTMA = 5
PATLAMA_ISI_MAX = 30000
PATLAMA_ISI_MIN = -30000
NITROJEN_SOGUTMA = 2000

# Panel boyutları
PANEL_WIDTH = 240
PANEL_HEIGHT = 330
PANEL_Y_OFFSET = 200

# Başlangıç verileri
havzalar = {i: {"uranyum": 0, "toryum": 0, "plütonyum": 0, "antimadde": 0, "su": 0, "nitrojen": 0, "timer": EVAPORATION_TIME} for i in (1, 2, 3)}
envanter = {"uranyum": 3, "toryum": 2, "plütonyum": 0, "su": 15, "antimadde": 0, "nitrojen": 0}
para = 150
enerji = 0
isi = 30
calisiyor = True
oynama_suresi = 0

# Araştırma sistemi
arastirma_puani = 0
arastirma_durumlari = {
    "kaliteli_toryum": False,  # 90 puan gerekli
    "buzlu_su": False,  # 40 puan gerekli
}

# Bulutların pozisyonlarını tutacak global değişken
bulut_x_pozisyonlari = [200, 500, 800, 1100]

# Oyun ayarları
oyun_ayarlari = {
    "bulut_animasyonu": False,  # Varsayılan olarak kapalı
    "oyun_hizi": "durdur"       # Başlangıçta durdurulmuş olarak başla
}

# Global değişkenler
root = None
canvas = None
market = None
screen_width = None
screen_height = None
env_frame = None
lbl_env = None
lbl_para = None
lbl_enerji = None
lbl_isi = None
lbl_skor = None
lbl_sure = None
lbl_arastirma = None
havza_frames = {}
havza_labels = {}
havza_butonlari = {}
window_created = False  # Pencere oluşturuldu mu kontrolü

def create_main_window():
    """Ana pencereyi oluşturur ve yapılandırır"""
    global root, screen_width, screen_height
    
    # Eğer zaten bir pencere varsa ve hala açıksa
    if root is not None and root.winfo_exists():
        print("Zaten bir pencere açık, yeni bir pencere açılmıyor.")
        return None
    
    # Eğer zaten bir pencere varsa, onu kapat
    if root is not None:
        try:
            root.destroy()
        except:
            pass  # Pencere zaten kapanmışsa hata almayı engelle
    
    # Yeni pencere oluştur
    root = tk.Tk()
    root.title("Nükleer Reaktör Oyunu")
    
    # Tam ekran ayarları
    root.attributes("-fullscreen", True)
    root.resizable(False, False)
    
    # Ekran boyutlarını al
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Pencereyi ortala
    x = (screen_width - root.winfo_reqwidth()) // 2
    y = (screen_height - root.winfo_reqheight()) // 2
    root.geometry(f"+{x}+{y}")
    
    # ESC tuşu ile çıkış
    root.bind("<Escape>", lambda e: kapat_onay())
    
    return root

def create_canvas():
    """Ana canvas'ı oluşturur"""
    global canvas
    
    canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="#87CEEB")
    canvas.pack(fill="both", expand=True)
    
    return canvas

def create_info_bar():
    """Üst bilgi çubuğunu oluşturur"""
    global lbl_para, lbl_enerji, lbl_isi, lbl_skor, lbl_sure, lbl_arastirma
    
    info_frame = tk.Frame(canvas, bg="#222")
    canvas.create_window(screen_width / 2, 25, window=info_frame)
    
    font_boyutu = 12
    lbl_para = tk.Label(info_frame, text="Para: $0", fg="white", bg="#222", font=("Arial", font_boyutu))
    lbl_enerji = tk.Label(info_frame, text="Enerji: 0 MW", fg="white", bg="#222", font=("Arial", font_boyutu))
    lbl_isi = tk.Label(info_frame, text="Sıcaklık: 0°C", fg="white", bg="#222", font=("Arial", font_boyutu))
    lbl_skor = tk.Label(info_frame, text="Skor: 0", fg="white", bg="#222", font=("Arial", font_boyutu))
    lbl_sure = tk.Label(info_frame, text="Süre: 0 sn", fg="white", bg="#222", font=("Arial", font_boyutu))
    lbl_arastirma = tk.Label(info_frame, text="Araştırma Puanı: 0", fg="white", bg="#222", font=("Arial", font_boyutu))
    
    for w in (lbl_para, lbl_enerji, lbl_isi, lbl_skor, lbl_sure, lbl_arastirma):
        w.pack(side="left", padx=15)

def create_inventory_panel():
    """Envanter panelini oluşturur"""
    global env_frame, lbl_env
    
    env_frame = tk.LabelFrame(canvas, text="Envanter", font=("Arial", 14, "bold"), 
                            bg="#1a1a1a", fg="#00ff00", 
                            width=PANEL_WIDTH, height=PANEL_HEIGHT, 
                            relief="ridge", bd=3)
    env_frame.pack_propagate(False)
    canvas.create_window(150, screen_height/2 - PANEL_Y_OFFSET + 30, window=env_frame)
    
    inner_env_frame = tk.Frame(env_frame, bg="#2F4F4F", relief="sunken", bd=2)
    inner_env_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
    
    lbl_env = tk.Label(inner_env_frame, text="", font=("Arial", 12), 
                      bg="#2F4F4F", fg="#00ff00", justify="left")
    lbl_env.pack(padx=10, pady=10)

def create_market_frame():
    """Market frame'ini oluşturur"""
    global market
    
    market = tk.LabelFrame(root, text="Market", font=("Arial", 14, "bold"), 
                         bg="#1a1a1a", fg="#00ff00",
                         width=280, height=400,
                         relief="ridge", bd=3)
    market.pack_propagate(False)

def close_all_tkinter_windows():
    """Sistemdeki tüm Tkinter pencerelerini bulup kapatır"""
    global root
    
    # Öncelikle sistemde başka aktif Tkinter pencereleri varsa kapatalım
    try:
        # Eğer varsayılan bir Tkinter kökü varsa
        if hasattr(tk, '_default_root') and tk._default_root is not None:
            # Ana uygulama penceresi dışındaki tüm pencereleri kapat
            for widget in tk._default_root.winfo_children():
                if isinstance(widget, tk.Toplevel):
                    try:
                        widget.destroy()
                        print(f"Ek pencere kapatıldı: {widget}")
                    except:
                        pass
            
            # Eğer varsayılan kök bizim root değilse, onu da kapatalım
            if root is not tk._default_root:
                try:
                    old_root = tk._default_root
                    tk._default_root = None  # Önce referansı temizle
                    old_root.destroy()
                    print("Varsayılan Tkinter kökü kapatıldı.")
                except:
                    pass
    except Exception as e:
        print(f"Pencereleri kapatırken hata: {str(e)}")

def start_game():
    """Oyunu başlatır ve ana pencereyi oluşturur"""
    global root, canvas, market, havza_frames, havza_labels, screen_width, screen_height
    global env_frame, lbl_env, lbl_para, lbl_enerji, lbl_isi, lbl_skor, lbl_sure, lbl_arastirma
    global havza_butonlari
    
    try:
        # Mevcut açık olan tüm Tkinter pencerelerini kapat
        close_all_tkinter_windows()
        
        # Ana pencereyi oluştur
        new_root = create_main_window()
        
        # Eğer pencere zaten varsa ve oluşturulamadıysa çık
        if new_root is None:
            return
        
        # Canvas'ı oluştur
        create_canvas()
        
        # Bilgi çubuğunu oluştur
        create_info_bar()
        
        # Envanter panelini oluştur
        create_inventory_panel()
        
        # Market frame'ini oluştur
        create_market_frame()
        
        # Oyunu başlat
        ciz_arkaplan()
        menu_olustur()
        create_market_button()
        create_admin_button()
        
        # Havzaları oluştur
        for idx, ratio in zip((1, 2, 3), (0.25, 0.5, 0.75)):
            havza_butonlari[idx] = yap_havza_ui(idx, ratio)
        
        # Market butonlarını güncelle
        update_market_buttons()
        
        # Araştırma puanı toplamayı başlat
        arastirma_puani_topla()
        
        # Oyun döngüsünü başlat
        if calisiyor:
            oyun_dongusu()
        
        # Süre güncellemeyi başlat
        sure_guncelle()
        
        # Bulut animasyonunu başlat
        if oyun_ayarlari["bulut_animasyonu"]:
            root.after(500, bulutlari_hareket_ettir)
        
        root.mainloop()
        
    except Exception as e:
        print(f"Oyun başlatılırken bir hata oluştu: {str(e)}")
        if root:
            try:
                root.destroy()
            except:
                pass  # Pencere zaten kapanmışsa hata almayı engelle

def save_game():
    global havzalar, envanter, para, enerji, isi, calisiyor, oynama_suresi, arastirma_puani, arastirma_durumlari
    save_data = {
        'havzalar': havzalar,
        'envanter': envanter,
        'para': para,
        'enerji': enerji,
        'isi': isi,
        'calisiyor': calisiyor,
        'oynama_suresi': oynama_suresi,
        'arastirma_puani': arastirma_puani,
        'arastirma_durumlari': arastirma_durumlari,
        'oyun_ayarlari': oyun_ayarlari
    }
    try:
        with open('save.json', 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False)
        messagebox.showinfo("Kayıt Başarılı", "Oyun başarıyla kaydedildi!")
    except Exception as e:
        messagebox.showerror("Hata", f"Kayıt yapılamadı: {str(e)}")

def load_game():
    global havzalar, envanter, para, enerji, isi, calisiyor, oynama_suresi, arastirma_puani, arastirma_durumlari, oyun_ayarlari
    try:
        with open('save.json', 'r', encoding='utf-8') as f:
            save_data = json.load(f)
        
        havzalar = {int(k): v for k, v in save_data['havzalar'].items()}
        envanter = save_data['envanter']
        para = save_data['para']
        enerji = save_data['enerji']
        isi = save_data['isi']
        calisiyor = save_data['calisiyor']
        oynama_suresi = save_data['oynama_suresi']
        arastirma_puani = save_data.get('arastirma_puani', 0)
        arastirma_durumlari = save_data.get('arastirma_durumlari', {"kaliteli_toryum": False, "buzlu_su": False})
        oyun_ayarlari = save_data.get('oyun_ayarlari', {"bulut_animasyonu": False, "oyun_hizi": "durdur"})
        
        update_ui()
        update_game_speed()  # Oyun hızını güncelle
        
        # Bulut animasyonunu güncelle
        if oyun_ayarlari["bulut_animasyonu"]:
            global bulut_x_pozisyonlari
            bulut_x_pozisyonlari = [200, 500, 800, 1100]
            root.after(500, bulutlari_hareket_ettir)
        
        if calisiyor:
            oyun_dongusu()
        messagebox.showinfo("Yükleme Başarılı", "Oyun başarıyla yüklendi!")
    except FileNotFoundError:
        messagebox.showerror("Hata", "Kayıt dosyası bulunamadı!")
    except Exception as e:
        messagebox.showerror("Hata", f"Yükleme başarısız: {str(e)}")

def admin_paneli():
    def check_password():
        password = entry_password.get()
        if password == "zikkalar":
            global para, envanter, arastirma_puani, arastirma_durumlari
            # Parayı ve envanteri güncelle
            para = 999999
            for item in ["uranyum", "toryum", "plütonyum", "antimadde", "su", "nitrojen", "kaliteli_toryum", "buzlu_su"]:
                envanter[item] = 999
            
            # Tüm araştırmaları aç
            arastirma_puani = 999
            for key in arastirma_durumlari:
                arastirma_durumlari[key] = True
            
            update_ui()
            messagebox.showinfo("Başarılı", "Admin erişimi sağlandı! 🎮")
            admin_window.destroy()
        else:
            messagebox.showerror("Hata", "Yanlış şifre! 🚫")

    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Paneli")
    admin_window.geometry("300x150")
    admin_window.configure(bg="#1a1a1a")  # Koyu arka plan
    
    # Pencereyi sağ alta konumlandır
    admin_window.geometry(f"+{root.winfo_screenwidth() - 350}+{root.winfo_screenheight() - 200}")
    
    # Şifre etiketi
    label = tk.Label(admin_window, 
                    text="Admin şifresini girin:", 
                    font=("Arial", 12),
                    bg="#1a1a1a",
                    fg="#00ff00")  # Neon yeşil yazı
    label.pack(pady=10)
    
    # Şifre giriş kutusu
    entry_password = tk.Entry(admin_window, 
                            show="*", 
                            font=("Arial", 12),
                            bg="#2d2d2d",
                            fg="#00ff00",
                            insertbackground="#00ff00")  # İmleç rengi
    entry_password.pack(pady=10)
    
    # Giriş butonu
    btn_login = tk.Button(admin_window, 
                         text="Giriş Yap",
                         command=check_password,
                         font=("Arial", 12),
                         bg="#006400",  # Koyu yeşil
                         fg="#ffffff",
                         activebackground="#008000",  # Açık yeşil
                         activeforeground="#ffffff")
    btn_login.pack(pady=10)

def arastirma_puani_topla():
    global arastirma_puani
    arastirma_puani += random.randint(3, 6)
    update_ui()
    root.after(3000, arastirma_puani_topla)

def arastirma_menu():
    def kaliteli_toryum_al():
        global arastirma_puani
        if arastirma_puani >= 90 and not arastirma_durumlari["kaliteli_toryum"]:
            arastirma_puani -= 90
            arastirma_durumlari["kaliteli_toryum"] = True
            update_ui()
            messagebox.showinfo("Başarılı", "Kaliteli Toryum araştırması tamamlandı!")
            arastirma_window.destroy()
        else:
            messagebox.showerror("Hata", "Yeterli araştırma puanınız yok veya zaten araştırıldı!")

    def buzlu_su_al():
        global arastirma_puani
        if arastirma_puani >= 40 and not arastirma_durumlari["buzlu_su"]:
            arastirma_puani -= 40
            arastirma_durumlari["buzlu_su"] = True
            update_ui()
            messagebox.showinfo("Başarılı", "Buzlu Su araştırması tamamlandı!")
            arastirma_window.destroy()
        else:
            messagebox.showerror("Hata", "Yeterli araştırma puanınız yok veya zaten araştırıldı!")

    arastirma_window = tk.Toplevel(root)
    arastirma_window.title("Araştırma Merkezi")
    arastirma_window.geometry("400x300")
    
    tk.Label(arastirma_window, text="Araştırma Merkezi", font=("Arial", 16, "bold")).pack(pady=10)
    tk.Label(arastirma_window, text=f"Mevcut Araştırma Puanı: {arastirma_puani}", font=("Arial", 12)).pack(pady=5)
    
    kt_frame = tk.Frame(arastirma_window)
    kt_frame.pack(pady=10, fill="x", padx=20)
    tk.Label(kt_frame, text="Kaliteli Toryum (90 Puan)", font=("Arial", 12)).pack(side="left")
    tk.Button(kt_frame, text="Araştır", command=kaliteli_toryum_al,
              state="disabled" if arastirma_durumlari["kaliteli_toryum"] else "normal").pack(side="right")
    
    bs_frame = tk.Frame(arastirma_window)
    bs_frame.pack(pady=10, fill="x", padx=20)
    tk.Label(bs_frame, text="Buzlu Su (40 Puan)", font=("Arial", 12)).pack(side="left")
    tk.Button(bs_frame, text="Araştır", command=buzlu_su_al,
              state="disabled" if arastirma_durumlari["buzlu_su"] else "normal").pack(side="right")

def bilgi_goster():
    bilgi = (
        "🔧 OYUN BİLGİLERİ 🔧\n\n"
        "- Uranyum: +20°C, 2 MW (30$)\n"
        "- Toryum: +10°C, 1 MW (60$)\n"
        "- Plütonyum: +200°C, 5 MW (1500$)\n"
        "- Antimadde: +5000°C, 50 MW (20000$)\n"
        "- Su: -5°C soğutma (10$)\n"
        "- Nitrojen: -2000°C soğutma (2000$)\n"
        "- Kaliteli Toryum: +10°C, 3 MW (120$)\n"
        "- Buzlu Su: -15°C soğutma (30$)\n"
        "- Sıcaklık -30000 ila 30000°C arasında olmalı.\n"
        "- Su zamanla buharlaşır.\n"
        "- Skor: Üretilen enerji.\n"
        "İyi oyunlar! 🚀"
    )
    messagebox.showinfo("Yardım", bilgi)

def kapat_onay():
    def cikis():
        if kayit_var.get() and not kayit_checkbox.get():
            messagebox.showwarning("Uyarı", "Lütfen ilerlemenizi kaydettiğinizi onaylayın!")
            return
        root.destroy()

    onay_pencere = tk.Toplevel(root)
    onay_pencere.title("Çıkış Onayı")
    onay_pencere.geometry("400x200")
    onay_pencere.transient(root)
    onay_pencere.grab_set()
    
    # Pencereyi ortala
    onay_pencere.geometry(f"+{root.winfo_x() + root.winfo_width()//2 - 200}+{root.winfo_y() + root.winfo_height()//2 - 100}")
    
    tk.Label(onay_pencere, text="Kapatmak istediğinize emin misiniz?\nBütün ilerlemeniz kaybolabilir!", 
             font=("Arial", 12), pady=20).pack()
    
    kayit_var = tk.BooleanVar(value=True)
    kayit_checkbox = tk.BooleanVar(value=False)
    
    tk.Checkbutton(onay_pencere, text="İlerlemeyi kaydettim", variable=kayit_checkbox,
                   font=("Arial", 10)).pack(pady=10)
    
    buton_frame = tk.Frame(onay_pencere)
    buton_frame.pack(pady=20)
    
    tk.Button(buton_frame, text="Çıkış", command=cikis, 
              bg="#ff4444", fg="white", font=("Arial", 11)).pack(side="left", padx=10)
    tk.Button(buton_frame, text="İptal", command=onay_pencere.destroy,
              bg="#444", fg="white", font=("Arial", 11)).pack(side="left", padx=10)

def ciz_arkaplan():
    # Gökyüzü rengi
    canvas.configure(bg="#87CEEB")  # Açık mavi gökyüzü
    
    # Güneş çizimi
    canvas.create_oval(50, 50, 150, 150, 
                      fill="#FFD700", outline="#FFA500", width=3)
    # Güneş ışınları
    for i in range(12):
        aci = i * 30
        x1 = 100 + 60 * math.cos(math.radians(aci))
        y1 = 100 + 60 * math.sin(math.radians(aci))
        x2 = 100 + 80 * math.cos(math.radians(aci))
        y2 = 100 + 80 * math.sin(math.radians(aci))
        canvas.create_line(x1, y1, x2, y2, fill="#FFD700", width=2)
    
    if oyun_ayarlari["bulut_animasyonu"]:
        ciz_bulutlar()
    else:
        # Sabit bulutlar
        bulut_pozisyonlari = [(200, 80), (500, 120), (800, 60), (1100, 100)]
        for x, y in bulut_pozisyonlari:
            for i in range(4):
                canvas.create_oval(x + i*30, y, x + 80 + i*20, y + 40,
                                 fill="white", outline="white")
    
    # Arka sıradaki dağlar (daha uzaktaki)
    for x in range(-100, screen_width + 200, 300):
        # Üçgen dağlar
        canvas.create_polygon(x, screen_height - 100,  # Sol alt
                            x + 150, screen_height - 300,  # Tepe
                            x + 300, screen_height - 100,  # Sağ alt
                            fill="#4A5D16",  # Koyu yeşil
                            outline="#2A3A10")  # Daha koyu yeşil
    
    # Ön sıradaki dağlar (daha yakındaki)
    for x in range(-200, screen_width + 300, 400):
        # Daha büyük üçgen dağlar
        canvas.create_polygon(x, screen_height - 80,  # Sol alt
                            x + 200, screen_height - 250,  # Tepe
                            x + 400, screen_height - 80,  # Sağ alt
                            fill="#556B2F",  # Orta koyu yeşil
                            outline="#3B4A21")  # Koyu yeşil
    
    # Zemin katmanları
    # En arka zemin (koyu çimen)
    canvas.create_rectangle(0, screen_height - 100,
                          screen_width, screen_height,
                          fill="#2F4F2F",  # Koyu yeşil
                          outline="#1B4D1B")
    
    # Orta zemin (orta ton çimen)
    canvas.create_rectangle(0, screen_height - 80,
                          screen_width, screen_height,
                          fill="#3B5F3B",
                          outline="#2F4F2F")
    
    # Ön zemin (açık çimen)
    canvas.create_rectangle(0, screen_height - 60,
                          screen_width, screen_height,
                          fill="#446644",
                          outline="#3B5F3B")

# Envanter paneli - Sol orta
PANEL_WIDTH = 240
PANEL_HEIGHT = 330
PANEL_Y_OFFSET = 200  # Yukarıdan uzaklık artırıldı

# Market butonu oluştur
def create_market_button():
    # Araştırma butonu
    research_btn = tk.Button(canvas,
                          text="🔬 Araştırma",
                          command=arastirma_menu,
                          font=("Arial", 12),
                          bg="#1a1a1a",
                          fg="#00ff00",
                          relief="flat",
                          activebackground="#2d2d2d",
                          activeforeground="#00ff00",
                          width=25)
    canvas.create_window(150, screen_height/2 - PANEL_Y_OFFSET - 210, window=research_btn)  # Market butonunun 50 piksel üstünde

    # Market butonu
    market_btn = tk.Button(canvas,
                          text="🏪 Market",
                          command=lambda: market.place(relx=0.95, rely=0.25, anchor="e") if not market.winfo_viewable() else market.place_forget(),
                          font=("Arial", 12),
                          bg="#1a1a1a",
                          fg="#00ff00",
                          relief="flat",
                          activebackground="#2d2d2d",
                          activeforeground="#00ff00",
                          width=25)
    canvas.create_window(150, screen_height/2 - PANEL_Y_OFFSET - 160, window=market_btn)

# Envanter paneli
env_frame = tk.LabelFrame(canvas, text="Envanter", font=("Arial", 14, "bold"), bg="#1a1a1a", fg="#00ff00", 
                         width=PANEL_WIDTH, height=PANEL_HEIGHT, relief="ridge", bd=3)
env_frame.pack_propagate(False)

# İç frame (gradient efekti için)
inner_env_frame = tk.Frame(env_frame, bg="#2F4F4F", relief="sunken", bd=2)
inner_env_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)

lbl_env = tk.Label(inner_env_frame, text="", font=("Arial", 12), bg="#2F4F4F", fg="#00ff00", justify="left")
lbl_env.pack(padx=10, pady=10)

# Üst bilgi çubuğu - Sadece bilgiler
info_frame = tk.Frame(canvas, bg="#222")


font_boyutu = 12

lbl_para = tk.Label(info_frame, text="Para: $0", fg="white", bg="#222", font=("Arial", font_boyutu))
lbl_enerji = tk.Label(info_frame, text="Enerji: 0 MW", fg="white", bg="#222", font=("Arial", font_boyutu))
lbl_isi = tk.Label(info_frame, text="Sıcaklık: 0°C", fg="white", bg="#222", font=("Arial", font_boyutu))
lbl_skor = tk.Label(info_frame, text="Skor: 0", fg="white", bg="#222", font=("Arial", font_boyutu))
lbl_sure = tk.Label(info_frame, text="Süre: 0 sn", fg="white", bg="#222", font=("Arial", font_boyutu))
lbl_arastirma = tk.Label(info_frame, text="Araştırma Puanı: 0", fg="white", bg="#222", font=("Arial", font_boyutu))

for w in (lbl_para, lbl_enerji, lbl_isi, lbl_skor, lbl_sure, lbl_arastirma):
    w.pack(side="left", padx=15)

def menu_olustur():
    menu_btn = tk.Menubutton(canvas, 
                            text="☰",
                            font=("Arial", 16),
                            bg="#1a1a1a",
                            fg="#00ff00",
                            relief="flat",
                            activebackground="#2d2d2d",
                            activeforeground="#00ff00")
    
    menu = tk.Menu(menu_btn, tearoff=0, bg="#1a1a1a", fg="#00ff00")
    menu_btn["menu"] = menu
    
    # Ana menü öğeleri
    menu.add_command(label="💾 Kaydet", command=save_game)
    menu.add_command(label="📂 Yükle", command=load_game)
    menu.add_separator()
    
    # Ayarlar alt menüsü
    ayarlar_menu = tk.Menu(menu, tearoff=0, bg="#1a1a1a", fg="#00ff00")
    menu.add_cascade(label="⚙️ Ayarlar", menu=ayarlar_menu)
    
    # Bulut animasyonu ayarı
    def bulut_animasyonu_toggle():
        oyun_ayarlari["bulut_animasyonu"] = not oyun_ayarlari["bulut_animasyonu"]
        if oyun_ayarlari["bulut_animasyonu"]:
            global bulut_x_pozisyonlari
            bulut_x_pozisyonlari = [200, 500, 800, 1100]
            root.after(500, bulutlari_hareket_ettir)
        else:
            canvas.delete("bulut")
            ciz_arkaplan()
    
    ayarlar_menu.add_checkbutton(label="☁️ Bulut Animasyonu",
                                variable=tk.BooleanVar(value=oyun_ayarlari["bulut_animasyonu"]),
                                command=bulut_animasyonu_toggle)
    
    # Oyun hızı alt menüsü
    hiz_menu = tk.Menu(ayarlar_menu, tearoff=0, bg="#1a1a1a", fg="#00ff00")
    ayarlar_menu.add_cascade(label="⚡ Oyun Hızı", menu=hiz_menu)
    
    hiz_var = tk.StringVar(value=oyun_ayarlari["oyun_hizi"])
    for hiz in ["yavas", "normal", "hizli", "durdur"]:
        hiz_menu.add_radiobutton(
            label=hiz.title(),
            value=hiz,
            variable=hiz_var,
            command=lambda h=hiz: [oyun_ayarlari.update({"oyun_hizi": h}), update_game_speed()]
        )
    
    menu.add_separator()
    menu.add_command(label="❌ Çıkış", command=root.destroy)  # Doğrudan çıkış
    
    canvas.create_window(screen_width - 40, 30, window=menu_btn)

def yap_havza_ui(i, x_ratio):
    global havza_frames
    w = int(screen_width * 0.2)
    h = 400
    x = int(screen_width * x_ratio)
    y = screen_height - 250
    
    f = tk.LabelFrame(canvas, text=f"Havza {i}", width=w, height=h, 
                     bg="#D3D3D3", relief="solid", borderwidth=2,
                     font=("Arial", 14, "bold"))
    havza_frames[i] = f
    canvas.create_window(x, y, window=f)
    
    lbl = tk.Label(f, text="", font=("Arial", 12), bg="#F0E68C", justify="left", width=15, height=12)
    lbl.place(x=10, y=10)
    
    button_frame = tk.Frame(f, bg="#D3D3D3")
    button_frame.place(x=w-150, y=10)
    
    # Temel materyaller için butonlar
    temel_materyaller = ["uranyum", "toryum", "plütonyum", "antimadde", "su", "nitrojen"]
    for nesne in temel_materyaller:
        btn = tk.Button(button_frame, 
                 text=f"{nesne.title()} Ekle",
                 command=lambda n=nesne: ekle(n, i),
                 font=("Arial", 10),
                 bg="#696969",
                 fg="#FFFFFF",
                 relief="solid",
                 padx=5,
                 pady=2,
                 bd=2)
        btn.pack(pady=3)
        btn.bind('<Button-1>', lambda e, n=nesne: root.after(1, lambda: ekle(n, i)))  # Daha hızlı yanıt
    
    # Ayırıcı çizgi
    tk.Frame(button_frame, bg="#444444", height=2).pack(fill="x", pady=5)
    
    # Araştırma materyalleri için butonlar/etiketler
    arastirma_materyalleri = {
        "kaliteli_toryum": "Kaliteli Toryum",
        "buzlu_su": "Buzlu Su"
    }
    arastirma_butonlari = {}
    
    for kod, isim in arastirma_materyalleri.items():
        if arastirma_durumlari[kod]:
            btn = tk.Button(button_frame, 
                     text=f"{isim} Ekle",
                     command=lambda k=kod: ekle(k, i),
                     font=("Arial", 10),
                     bg="#696969",
                     fg="#FFFFFF",
                     relief="solid",
                     padx=5,
                     pady=2,
                     bd=2)
            btn.bind('<Button-1>', lambda e, k=kod: root.after(1, lambda: ekle(k, i)))  # Daha hızlı yanıt
        else:
            btn = tk.Label(button_frame,
                     text=f"{isim} - Araştırılmadı",
                     font=("Arial", 10),
                     bg="#444444",
                     fg="#888888",
                     relief="solid",
                     padx=5,
                     pady=2)
        btn.pack(pady=3)
        arastirma_butonlari[kod] = btn
    
    havza_labels[i] = lbl
    return arastirma_butonlari

def update_market_buttons():
    for widget in market.winfo_children():
        widget.destroy()
    
    # İç frame (gradient efekti için)
    inner_market_frame = tk.Frame(market, bg="#333333", relief="sunken", bd=2)
    inner_market_frame.place(relx=0.05, rely=0.05, relwidth=0.9, relheight=0.9)
    
    items = [
        ("uranyum", 30),
        ("toryum", 60),
        ("plütonyum", 1500),
        ("antimadde", 20000),
        ("su", 10),
        ("nitrojen", 2000)
    ]
    
    # Araştırma materyalleri
    research_items = [
        ("kaliteli_toryum", 120),
        ("buzlu_su", 30)
    ]
    
    # Normal materyaller için butonlar
    for item, price in items:
        btn_frame = tk.Frame(inner_market_frame, bg="#333333")
        btn_frame.pack(pady=2, fill="x", padx=5)
        
        btn = tk.Button(
            btn_frame,
            text=f"{item.title().replace('_', ' ')} ({price}$)",
            command=lambda i=item: satin_al(i),
            font=("Arial", 11),
            bg="#1a1a1a",
            fg="#00ff00",
            activebackground="#2F4F4F",
            activeforeground="#00ff00",
            relief="ridge",
            bd=2,
            width=18,
            cursor="hand2"
        )
        btn.pack(pady=1)
        btn.bind('<Button-1>', lambda e, i=item: root.after(1, lambda: satin_al(i)))  # Daha hızlı yanıt
        
        # Hover efekti
        def on_enter(e, button=btn):
            button.config(bg="#2F4F4F")
        
        def on_leave(e, button=btn):
            button.config(bg="#1a1a1a")
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
    
    # Araştırma materyalleri için butonlar/etiketler
    tk.Label(inner_market_frame, text="─── Araştırma Materyalleri ───",
             bg="#333333", fg="#00ff00", font=("Arial", 10)).pack(pady=5)
    
    for item, price in research_items:
        btn_frame = tk.Frame(inner_market_frame, bg="#333333")
        btn_frame.pack(pady=2, fill="x", padx=5)
        
        if arastirma_durumlari[item]:
            btn = tk.Button(
                btn_frame,
                text=f"{item.title().replace('_', ' ')} ({price}$)",
                command=lambda i=item: satin_al(i),
                font=("Arial", 11),
                bg="#1a1a1a",
                fg="#00ff00",
                activebackground="#2F4F4F",
                activeforeground="#00ff00",
                relief="ridge",
                bd=2,
                width=18,
                cursor="hand2"
            )
            btn.bind('<Button-1>', lambda e, i=item: root.after(1, lambda: satin_al(i)))  # Daha hızlı yanıt
        else:
            btn = tk.Label(
                btn_frame,
                text=f"{item.title().replace('_', ' ')} - Araştırılmadı",
                font=("Arial", 11),
                bg="#1a1a1a",
                fg="#666666",
                width=18,
                relief="ridge",
                bd=2
            )
        btn.pack(pady=1)

def satin_al(item):
    global para, envanter
    prices = {
        "uranyum": 30,
        "toryum": 60,
        "plütonyum": 1500,
        "antimadde": 20000,
        "su": 10,
        "nitrojen": 2000,
        "kaliteli_toryum": 120,
        "buzlu_su": 30
    }
    if para >= prices[item]:
        para -= prices[item]
        if item not in envanter:
            envanter[item] = 0
        envanter[item] += 1
        update_ui()
        root.update_idletasks()  # Hemen güncelle

def ekle(item, i):
    if envanter.get(item, 0) > 0:
        if item not in havzalar[i]:
            havzalar[i][item] = 0
        havzalar[i][item] += 1
        envanter[item] -= 1
        update_ui()
        root.update_idletasks()  # Hemen güncelle

def oyun_dongusu():
    global isi, enerji, para, calisiyor, oynama_suresi
    if not calisiyor:
        return
    for h in havzalar.values():
        isi += h.get('uranyum', 0) * URANYUM_ISI
        isi += h.get('toryum', 0) * TORYUM_ISI
        if 'kaliteli_toryum' in h:
            isi += h['kaliteli_toryum'] * TORYUM_ISI
        isi += h.get('plütonyum', 0) * PLUTONYUM_ISI
        isi += h.get('antimadde', 0) * ANTIMADDE_ISI
        
        # Soğutma sistemleri
        isi -= h.get('su', 0) * SU_SOGUTMA
        if 'buzlu_su' in h:
            isi -= h['buzlu_su'] * (SU_SOGUTMA + 10)  # Normal sudan 10 birim daha fazla soğutma
        isi -= h.get('nitrojen', 0) * NITROJEN_SOGUTMA
        
        # Enerji üretimi
        enerji += h.get('uranyum', 0) * 2
        enerji += h.get('toryum', 0) * 1
        if 'kaliteli_toryum' in h:
            enerji += h['kaliteli_toryum'] * 3  # Normal toryumdan 2 birim daha fazla enerji
        enerji += h.get('plütonyum', 0) * 5
        
        # Para üretimi
        para += h.get('uranyum', 0) + h.get('toryum', 0)
        if 'kaliteli_toryum' in h:
            para += h['kaliteli_toryum'] * 2
        para += h.get('plütonyum', 0) * 3
        
        h['timer'] -= 1
        if h['timer'] <= 0:
            if h.get('su', 0) > 0:
                h['su'] -= 1
            if h.get('buzlu_su', 0) > 0:
                h['buzlu_su'] -= 1
            h['timer'] = EVAPORATION_TIME
            
    if isi < PATLAMA_ISI_MIN or isi > PATLAMA_ISI_MAX:
        calisiyor = False
        messagebox.showerror("Patlama!", "Reaktör patladı! 💥")
        return
    update_ui()
    root.after(UPDATE_INTERVAL, oyun_dongusu)

def update_ui():
    lbl_para.config(text=f"Para: ${para}")
    lbl_enerji.config(text=f"Enerji: {enerji} MW")
    lbl_isi.config(text=f"Sıcaklık: {isi}°C")
    lbl_skor.config(text=f"Skor: {enerji}")
    lbl_sure.config(text=f"Süre: {oynama_suresi} sn")
    lbl_arastirma.config(text=f"Araştırma Puanı: {arastirma_puani}")
    
    # Envanter etiketini güncelle
    envanter_text = []
    for k, v in envanter.items():
        if v > 0:  # Sadece 0'dan büyük değerleri göster
            isim = k.replace('_', ' ').title()
            envanter_text.append(f"{isim}: {v}")
    lbl_env.config(text='\n'.join(envanter_text))
    
    # Havza etiketlerini güncelle
    for i, lbl in havza_labels.items():
        h = havzalar[i]
        content = []
        for k in h.keys():
            if k != 'timer' and h[k] > 0:
                isim = k.replace('_', ' ').title()
                content.append(f"{isim}: {h[k]}")
        lbl.config(text='\n'.join(content))
    
    # Havzalardaki araştırma butonlarını güncelle
    for havza_id in havza_butonlari:
        for materyal, btn in havza_butonlari[havza_id].items():
            if arastirma_durumlari[materyal]:
                # Eğer araştırma tamamlandıysa ve buton hala Label ise, yeni buton oluştur
                if isinstance(btn, tk.Label):
                    yeni_btn = tk.Button(btn.master,
                                       text=f"{materyal.replace('_', ' ').title()} Ekle",
                                       command=lambda k=materyal, i=havza_id: ekle(k, i),
                                       font=("Arial", 10),
                                       bg="#696969",
                                       fg="#FFFFFF",
                                       relief="solid",
                                       padx=5,
                                       pady=2,
                                       bd=2)
                    yeni_btn.pack(pady=3)
                    btn.destroy()  # Eski Label'ı kaldır
                    havza_butonlari[havza_id][materyal] = yeni_btn
            else:
                # Eğer araştırma tamamlanmadıysa ve hala Label değilse, Label'a çevir
                if isinstance(btn, tk.Button):
                    yeni_label = tk.Label(btn.master,
                                        text=f"{materyal.replace('_', ' ').title()} - Araştırılmadı",
                                        font=("Arial", 10),
                                        bg="#444444",
                                        fg="#888888",
                                        relief="solid",
                                        padx=5,
                                        pady=2)
                    yeni_label.pack(pady=3)
                    btn.destroy()  # Eski butonu kaldır
                    havza_butonlari[havza_id][materyal] = yeni_label
    
    update_market_buttons()
        
def sure_guncelle():
    global oynama_suresi
    oynama_suresi += 1
    lbl_sure.config(text=f"Süre: {oynama_suresi} sn")
    root.after(1000, sure_guncelle)


# Admin butonunu oluştur
def create_admin_button():
    admin_btn = tk.Button(canvas,
                         text="⚙️",  # Dişli emoji
                         command=admin_paneli,
                         font=("Arial", 12),
                         bg="#1a1a1a",
                         fg="#00ff00",
                         width=3,
                         height=1,
                         relief="flat",
                         borderwidth=0)
    
    # Butonu sağ alta yerleştir
    canvas.create_window(screen_width - 40, screen_height - 40,
                        window=admin_btn)

def bulutlari_hareket_ettir():
    if not oyun_ayarlari["bulut_animasyonu"]:
        return
        
    global bulut_x_pozisyonlari
    for i in range(len(bulut_x_pozisyonlari)):
        bulut_x_pozisyonlari[i] += 20
        if bulut_x_pozisyonlari[i] > screen_width + 100:
            bulut_x_pozisyonlari[i] = -200
    
    canvas.delete("bulut")
    ciz_bulutlar()
    
    root.after(500, bulutlari_hareket_ettir)

def ciz_bulutlar():
    for x in bulut_x_pozisyonlari:
        y = random.randint(60, 120)
        for i in range(4):
            canvas.create_oval(x + i*30, y, x + 80 + i*20, y + 40,
                             fill="white", outline="white", tags="bulut")

def update_game_speed():
    global UPDATE_INTERVAL, calisiyor
    hiz_ayarlari = {
        "yavas": 2000,
        "normal": 1000,
        "hizli": 500,
        "durdur": None
    }
    if oyun_ayarlari["oyun_hizi"] != "durdur":
        UPDATE_INTERVAL = hiz_ayarlari[oyun_ayarlari["oyun_hizi"]]
        if not calisiyor:  # Eğer oyun durdurulmuşsa ve hız değiştirilirse
            calisiyor = True
            oyun_dongusu()
    else:
        calisiyor = False

# Ana giriş noktası
if __name__ == "__main__":
    try:
        # Başlamadan önce tüm açık Tkinter pencerelerini kapat
        if 'close_all_tkinter_windows' in globals():
            close_all_tkinter_windows()
        
        # Eğer zaten bir root varsa ve açıksa, yeniden oluşturmayı dene
        if root is not None and hasattr(root, 'winfo_exists') and root.winfo_exists():
            print("Uyarı: Zaten açık bir pencere var, kapatılıyor...")
            try:
                root.destroy()
            except:
                pass
        start_game()
    except Exception as e:
        print(f"Kritik hata: {str(e)}")
        # Herhangi bir açık pencereyi kapat
        if 'root' in globals() and root is not None:
            try:
                root.destroy()
            except:
                pass