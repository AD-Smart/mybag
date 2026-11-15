import os
import json
import urllib.request
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class MinecraftNativesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Windows Natives Downloader")
        self.root.geometry("480x500")
        
        # اختيار ملف الـ JSON
        self.lbl_file = tk.Label(root, text="اختر ملف JSON الخاص بالنسخة:", font=("Arial", 10, "bold"))
        self.lbl_file.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.frame_file = tk.Frame(root)
        self.frame_file.pack(fill="x", padx=15, pady=5)
        
        self.ent_file = tk.Entry(self.frame_file, width=35, font=("Arial", 10))
        self.ent_file.pack(side="left", expand=True, fill="x")
        
        self.btn_browse = tk.Button(self.frame_file, text="استعراض...", command=self.browse_file, font=("Arial", 9))
        self.btn_browse.pack(side="right", padx=(8, 0))
        
        # اختيار مجلد الحفظ
        self.lbl_out = tk.Label(root, text="اختر مجلد الحفظ:", font=("Arial", 10, "bold"))
        self.lbl_out.pack(anchor="w", padx=15, pady=(15, 5))
        
        self.frame_out = tk.Frame(root)
        self.frame_out.pack(fill="x", padx=15, pady=5)
        
        self.ent_out = tk.Entry(self.frame_out, width=35, font=("Arial", 10))
        self.ent_out.pack(side="left", expand=True, fill="x")
        self.ent_out.insert(0, "windows_natives")
        
        self.btn_out = tk.Button(self.frame_out, text="مجلد...", command=self.browse_output, font=("Arial", 9))
        self.btn_out.pack(side="right", padx=(8, 0))
        
        # زر بدء التحميل
        self.btn_start = tk.Button(root, text="بدء التحميل", bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), command=self.start_download_thread)
        self.btn_start.pack(fill="x", padx=15, pady=20)
        
        # صندوق عرض السجل والرسائل
        self.lbl_log = tk.Label(root, text="سجل العمليات:", font=("Arial", 10, "bold"))
        self.lbl_log.pack(anchor="w", padx=15)
        
        self.txt_log = scrolledtext.ScrolledText(root, height=12, state="disabled", font=("Courier", 9))
        self.txt_log.pack(fill="both", expand=True, padx=15, pady=(5, 15))

    def browse_file(self):
        filename = filedialog.askopenfilename(title="اختر ملف JSON", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if filename:
            self.ent_file.delete(0, tk.END)
            self.ent_file.insert(0, filename)

    def browse_output(self):
        dirname = filedialog.askdirectory(title="اختر مجلد حفظ النتائج")
        if dirname:
            self.ent_out.delete(0, tk.END)
            self.ent_out.insert(0, dirname)

    def log(self, message):
        def _log():
            self.txt_log.config(state="normal")
            self.txt_log.insert(tk.END, message + "\n")
            self.txt_log.see(tk.END)
            self.txt_log.config(state="disabled")
        self.root.after(0, _log)

    def start_download_thread(self):
        json_path = self.ent_file.get().strip()
        output_dir = self.ent_out.get().strip()
        
        if not json_path or not os.path.exists(json_path):
            messagebox.showerror("خطأ", "الرجاء اختيار ملف JSON صحيح أولاً!")
            return
            
        if not output_dir:
            output_dir = "windows_natives"

        self.btn_start.config(state="disabled", text="جاري التحميل...")
        self.txt_log.config(state="normal")
        self.txt_log.delete(1.0, tk.END)
        self.txt_log.config(state="disabled")
        
        # تشغيل عملية التحميل في خلفية منفصلة لكي لا تتجمّد الواجهة
        thread = threading.Thread(target=self.download_natives, args=(json_path, output_dir))
        thread.daemon = True
        thread.start()

    def download_natives(self, json_file_path, output_dir):
        try:
            self.log("[*] جاري قراءة ملف الـ JSON...")
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            self.log(f"[-] خطأ في قراءة الملف: {e}")
            self.root.after(0, lambda: self.btn_start.config(state="normal", text="بدء التحميل"))
            return

        libraries = data.get("libraries", [])
        os.makedirs(output_dir, exist_ok=True)
        
        downloaded_count = 0
        self.log("[+] جاري فحص المكتبات واستخراج ملفات Windows Natives...")

        for lib in libraries:
            natives = lib.get("natives", {})
            downloads = lib.get("downloads", {})
            
            if "windows" in natives:
                classifier_key = natives["windows"]
                classifiers = downloads.get("classifiers", {})
                
                native_info = None
                if classifier_key in classifiers:
                    native_info = classifiers[classifier_key]
                else:
                    for k, v in classifiers.items():
                        if "windows" in k.lower():
                            native_info = v
                            break
                
                if native_info:
                    url = native_info.get("url")
                    path_str = native_info.get("path")
                    
                    if url and path_str:
                        file_name = os.path.basename(path_str)
                        file_path = os.path.join(output_dir, file_name)
                        
                        self.log(f"[تحميل] {file_name}")
                        try:
                            urllib.request.urlretrieve(url, file_path)
                            downloaded_count += 1
                        except Exception as e:
                            self.log(f"[-] فشل تحميل {file_name}: {e}")

        self.log(f"\n[تم بنجاح!] تم تحميل {downloaded_count} ملف بنجاح.")
        self.log(f"[*] المجلد: {os.path.abspath(output_dir)}")
        
        def finish():
            messagebox.showinfo("تم الانتهاء", f"تم تحميل {downloaded_count} من ملفات Windows Natives بنجاح!")
            self.btn_start.config(state="normal", text="بدء التحميل")
            
        self.root.after(0, finish)

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftNativesApp(root)
    root.mainloop()
