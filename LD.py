import os
import json
import urllib.request
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog

class MinecraftJsonPasteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Windows Natives Downloader")
        self.root.geometry("380x620")
        
        title_lbl = tk.Label(root, text="تحميل Windows Natives (لصق JSON)", font=("Arial", 11, "bold"), fg="#2196F3")
        title_lbl.pack(pady=8)
        
        # صندوق لصق كود الـ JSON
        lbl_json = tk.Label(root, text="ألصق محتوى ملف الـ JSON هنا:", font=("Arial", 9, "bold"))
        lbl_json.pack(anchor="w", padx=15, pady=(5, 2))
        
        self.txt_json = scrolledtext.ScrolledText(root, height=11, font=("Courier", 8))
        self.txt_json.pack(fill="both", expand=True, padx=15, pady=5)
        
        # اختيار مجلد الحفظ
        lbl_out = tk.Label(root, text="مجلد حفظ الملفات:", font=("Arial", 9, "bold"))
        lbl_out.pack(anchor="w", padx=15, pady=(8, 2))
        
        frame_out = tk.Frame(root)
        frame_out.pack(fill="x", padx=15, pady=5)
        
        self.ent_out = tk.Entry(frame_out, font=("Arial", 9))
        self.ent_out.pack(side="left", expand=True, fill="x", ipady=3)
        
        # المسار الافتراضي للحفظ في ذاكرة الهاتف إن وجد
        default_out = "/sdcard/Download/windows_natives" if os.path.exists("/sdcard/Download") else "windows_natives"
        self.ent_out.insert(0, default_out)
        
        btn_out = tk.Button(frame_out, text="مجلد...", command=self.browse_output, font=("Arial", 9))
        btn_out.pack(side="right", padx=(5, 0))
        
        # زر بدء التحميل
        self.btn_start = tk.Button(root, text="بدء تحميل Windows Natives", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), command=self.start_download_thread)
        self.btn_start.pack(fill="x", padx=15, pady=12, ipady=4)
        
        # صندوق عرض سجل العمليات
        lbl_log = tk.Label(root, text="سجل العمليات:", font=("Arial", 9, "bold"))
        lbl_log.pack(anchor="w", padx=15)
        
        self.txt_log = scrolledtext.ScrolledText(root, height=7, state="disabled", font=("Courier", 8))
        self.txt_log.pack(fill="both", expand=True, padx=15, pady=(5, 10))

    def browse_output(self):
        initial_dir = "/sdcard/Download" if os.path.exists("/sdcard/Download") else "/"
        dirname = filedialog.askdirectory(title="اختر مجلد الحفظ", initialdir=initial_dir)
        if dirname:
            self.ent_out.delete(0, tk.END)
            self.ent_out.insert(0, dirname)

    def log(self, message):
        def _log():
            self.txt_log.config(state="normal")
            self.txt_log.insert(tk.END, message + "\n")
            self.txt_log.see(tk.END)
            self.txt_log.config(state="disabled")
        try:
            self.root.after(0, _log)
        except:
            pass

    def start_download_thread(self):
        json_text = self.txt_json.get("1.0", tk.END).strip()
        output_dir = self.ent_out.get().strip()
        
        if not json_text:
            messagebox.showerror("خطأ", "الرجاء لصق كود الـ JSON في الصندوق أولاً!")
            return
            
        if not output_dir:
            output_dir = "windows_natives"

        self.btn_start.config(state="disabled", text="جاري التحميل...")
        self.txt_log.config(state="normal")
        self.txt_log.delete(1.0, tk.END)
        self.txt_log.config(state="disabled")
        
        # تشغيل التحميل في خلفية منفصلة لمنع تجمد الواجهة (تم تصحيح السطر هنا)
        thread = threading.Thread(target=self.download_natives, args=(json_text, output_dir))
        thread.daemon = True
        thread.start()

    def download_natives(self, json_text, output_dir):
        try:
            self.log("[*] جاري تحليل كود الـ JSON...")
            data = json.loads(json_text)
        except Exception as e:
            self.log("[-] خطأ: كود الـ JSON غير صالح (تأكد من نسخه كاملاً)!")
            self.root.after(0, lambda: self.btn_start.config(state="normal", text="بدء تحميل Windows Natives"))
            return

        libraries = data.get("libraries", [])
        os.makedirs(output_dir, exist_ok=True)
        
        downloaded_count = 0
        self.log("[+] جاري استخراج وتحميل ملفات Windows Natives فقط...")

        for lib in libraries:
            natives = lib.get("natives", {})
            downloads = lib.get("downloads", {})
            
            if "windows" in natives:
                classifier_key = natives["windows"]
                classifiers = downloads.get("classifiers", {})
                
                native_info = None
                if classifier_key in classifiers:
                    native_info = classifiers.get(classifier_key)
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

        self.log(f"\n[تم بنجاح!] تم تحميل {downloaded_count} ملف.")
        self.log(f"[*] المجلد: {os.path.abspath(output_dir)}")
        
        def finish():
            messagebox.showinfo("تم الانتهاء", f"تم تحميل {downloaded_count} من ملفات Windows Natives بنجاح!")
            self.btn_start.config(state="normal", text="بدء تحميل Windows Natives")
            
        self.root.after(0, finish)

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftJsonPasteApp(root)
    root.mainloop()
