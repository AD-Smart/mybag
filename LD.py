import os
import json
import urllib.request
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class MinecraftPydroidApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Minecraft Natives Downloader")
        self.root.geometry("380x520")
        
        # عنوان التطبيق
        title_lbl = tk.Label(root, text="تحميل Windows Natives (ماينكرافت)", font=("Arial", 11, "bold"), fg="#2196F3")
        title_lbl.pack(pady=10)
        
        # اختيار ملف الـ JSON عبر زر التصفح
        lbl_file = tk.Label(root, text="ملف JSON الخاص بالنسخة:", font=("Arial", 10))
        lbl_file.pack(anchor="w", padx=15, pady=(5, 2))
        
        frame_file = tk.Frame(root)
        frame_file.pack(fill="x", padx=15, pady=5)
        
        # حقل للقراءة فقط يظهر المسار الذي اخترته من مدير الملفات
        self.ent_file = tk.Entry(frame_file, font=("Arial", 9), state="readonly", readonlybackground="#f0f0f0")
        self.ent_file.pack(side="left", expand=True, fill="x", ipady=4)
        
        btn_browse = tk.Button(frame_file, text="تصفح...", command=self.browse_file, font=("Arial", 9, "bold"), bg="#2196F3", fg="white")
        btn_browse.pack(side="right", padx=(5, 0))
        
        # اختيار مجلد الحفظ
        lbl_out = tk.Label(root, text="مجلد حفظ الملفات:", font=("Arial", 10))
        lbl_out.pack(anchor="w", padx=15, pady=(10, 2))
        
        frame_out = tk.Frame(root)
        frame_out.pack(fill="x", padx=15, pady=5)
        
        self.ent_out = tk.Entry(frame_out, font=("Arial", 9))
        self.ent_out.pack(side="left", expand=True, fill="x", ipady=4)
        
        # تعيين مسار التحميل الافتراضي في ذاكرة الهاتف الداخلية إن وجد
        default_out = "/sdcard/Download/windows_natives" if os.path.exists("/sdcard/Download") else "windows_natives"
        self.ent_out.insert(0, default_out)
        
        btn_out = tk.Button(frame_out, text="مجلد...", command=self.browse_output, font=("Arial", 9))
        btn_out.pack(side="right", padx=(5, 0))
        
        # زر بدء التحميل
        self.btn_start = tk.Button(root, text="بدء تحميل Windows Natives", bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), command=self.start_download_thread)
        self.btn_start.pack(fill="x", padx=15, pady=15, ipady=5)
        
        # صندوق عرض سجل العمليات
        lbl_log = tk.Label(root, text="سجل العمليات:", font=("Arial", 10, "bold"))
        lbl_log.pack(anchor="w", padx=15)
        
        self.txt_log = scrolledtext.ScrolledText(root, height=10, state="disabled", font=("Courier", 8))
        self.txt_log.pack(fill="both", expand=True, padx=15, pady=(5, 15))

    def browse_file(self):
        # فتح مدير الملفات في مجلد التحميلات افتراضياً لتسهيل الوصول لملفات الـ JSON
        initial_dir = "/sdcard/Download" if os.path.exists("/sdcard/Download") else "/"
        filename = filedialog.askopenfilename(
            title="اختر ملف JSON للنسخة",
            initialdir=initial_dir,
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if filename:
            self.ent_file.config(state="normal")
            self.ent_file.delete(0, tk.END)
            self.ent_file.insert(0, filename)
            self.ent_file.config(state="readonly")

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
        json_path = self.ent_file.get().strip()
        output_dir = self.ent_out.get().strip()
        
        if not json_path or not os.path.exists(json_path):
            messagebox.showerror("خطأ", "الرجاء الضغط على زر (تصفح...) لاختيار ملف الـ JSON أولاً!")
            return
            
        if not output_dir:
            output_dir = "windows_natives"

        self.btn_start.config(state="disabled", text="جاري التحميل...")
        self.txt_log.config(state="normal")
        self.txt_log.delete(1.0, tk.END)
        self.txt_log.config(state="disabled")
        
        # تشغيل التحميل في خيط منفصل لكي لا تتجمد الواجهة
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
            self.root.after(0, lambda: self.btn_start.config(state="normal", text="بدء تحميل Windows Natives"))
            return

        libraries = data.get("libraries", [])
        os.makedirs(output_dir, exist_ok=True)
        
        downloaded_count = 0
        self.log("[+] جاري فحص واستخراج ملفات Windows Natives فقط...")

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
    app = MinecraftPydroidApp(root)
    root.mainloop()
