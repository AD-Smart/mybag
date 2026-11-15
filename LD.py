import os
import json
import urllib.request
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog

class MinecraftDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MC Windows Natives Extractor")
        self.root.geometry("360x600")
        self.root.configure(f"#f5f5f5")

        # العنوان الرئيسي
        header = tk.Label(root, text="محمل Windows Natives (ماينكرافت)", font=("Tahoma", 11, "bold"), bg="#f5f5f5", fg="#333")
        header.pack(pady=10)

        # منطقة لصق الـ JSON
        lbl_json = tk.Label(root, text="ألصق محتوى ملف JSON هنا:", font=("Tahoma", 9, "bold"), bg="#f5f5f5", anchor="w")
        lbl_json.pack(fill="x", padx=15, pady=(5, 2))

        self.txt_json = scrolledtext.ScrolledText(root, height=10, font=("Courier", 8), bg="#ffffff", relief="solid", bd=1)
        self.txt_json.pack(fill="both", expand=True, padx=15, pady=5)

        # مسار مجلد الحفظ
        lbl_folder = tk.Label(root, text="مجلد الحفظ:", font=("Tahoma", 9, "bold"), bg="#f5f5f5", anchor="w")
        lbl_folder.pack(fill="x", padx=15, pady=(8, 2))

        frame_folder = tk.Frame(root, bg="#f5f5f5")
        frame_folder.pack(fill="x", padx=15, pady=5)

        self.ent_folder = tk.Entry(frame_folder, font=("Tahoma", 9), relief="solid", bd=1)
        self.ent_folder.pack(side="left", expand=True, fill="x", ipady=4)
        
        default_path = "/sdcard/Download/windows_natives" if os.path.exists("/sdcard/Download") else "windows_natives"
        self.ent_folder.insert(0, default_path)

        btn_browse = tk.Button(frame_folder, text="استعراض", font=("Tahoma", 8, "bold"), bg="#e0e0e0", command=self.select_folder)
        btn_browse.pack(side="right", padx=(5, 0))

        # زر بدء العملية
        self.btn_action = tk.Button(root, text="بدء تحميل Natives للويندوز", font=("Tahoma", 10, "bold"), bg="#2196F3", fg="white", relief="flat", command=self.start_process)
        self.btn_action.pack(fill="x", padx=15, pady=12, ipady=6)

        # صندوق السجل (Logs)
        lbl_logs = tk.Label(root, text="سجل التنفيذ:", font=("Tahoma", 9, "bold"), bg="#f5f5f5", anchor="w")
        lbl_logs.pack(fill="x", padx=15)

        self.txt_logs = scrolledtext.ScrolledText(root, height=8, font=("Courier", 8), bg="#1e1e1e", fg="#00ff00", relief="solid", bd=1, state="disabled")
        self.txt_logs.pack(fill="both", expand=True, padx=15, pady=(5, 12))

    def select_folder(self):
        initial_dir = "/sdcard/Download" if os.path.exists("/sdcard/Download") else "/"
        path = filedialog.askdirectory(initialdir=initial_dir)
        if path:
            self.ent_folder.delete(0, tk.END)
            self.ent_folder.insert(0, path)

    def log(self, text):
        def _write():
            self.txt_logs.config(state="normal")
            self.txt_logs.insert(tk.END, text + "\n")
            self.txt_logs.see(tk.END)
            self.txt_logs.config(state="disabled")
        self.root.after(0, _write)

    def start_process(self):
        json_data = self.txt_json.get("1.0", tk.END).strip()
        out_dir = self.ent_folder.get().strip()

        if not json_data:
            messagebox.showerror("خطأ", "الرجاء لصق كود الـ JSON أولاً!")
            return

        if not out_dir:
            out_dir = "windows_natives"

        self.btn_action.config(state="disabled", text="جاري التحميل...", bg="#9e9e9e")
        self.txt_logs.config(state="normal")
        self.txt_logs.delete(1.0, tk.END)
        self.txt_logs.config(state="disabled")

        # تشغيل في خلفية منفصلة لمنع تجمد واجهة الهاتف
        threading.Thread(target=self.process_download, args=(json_data, out_dir), daemon=True).start()

    def process_download(self, json_str, output_dir):
        try:
            self.log("[*] جاري تحليل بيانات الـ JSON...")
            data = json.loads(json_str)
        except Exception as e:
            self.log("[-] خطأ: كود الـ JSON غير صالح أو غير مكتمل!")
            self.reset_button()
            return

        libraries = data.get("libraries", [])
        if not libraries:
            self.log("[-] تنبيه: لم يتم العثور على حقل libraries في الـ JSON.")
            self.reset_button()
            return

        os.makedirs(output_dir, exist_ok=True)
        count = 0
        self.log(f"[+] تم إنشاء المجلد: {output_dir}")
        self.log("[+] جاري فحص واستخراج ملفات ويندوز...")

        for lib in libraries:
            natives = lib.get("natives", {})
            downloads = lib.get("downloads", {})
            
            # التحقق من وجود تصنيف خاص بالويندوز
            target_key = None
            if "windows" in natives:
                target_key = natives["windows"]
            
            classifiers = downloads.get("classifiers", {})
            
            # محاولة العثور على ملف الـ Native المطابق
            native_info = None
            if target_key and target_key in classifiers:
                native_info = classifiers[target_key]
            else:
                # بحث احتياطي لأي مفتاح يحتوي على windows و native
                for key, val in classifiers.items():
                    if "windows" in key.lower():
                        native_info = val
                        break

            if native_info:
                url = native_info.get("url")
                path = native_info.get("path")
                
                if url and path:
                    filename = os.path.basename(path)
                    filepath = os.path.join(output_dir, filename)
                    
                    self.log(f"[تحميل] {filename}")
                    try:
                        urllib.request.urlretrieve(url, filepath)
                        count += 1
                    except Exception as err:
                        self.log(f"[-] فشل تحميل {filename}: {err}")

        self.log(f"\n[تم بنجاح!] تم تحميل {count} ملف بنجاح.")
        self.log(f"[*] مسار الحفظ: {os.path.abspath(output_dir)}")
        
        def finish_msg():
            messagebox.showinfo("اكتمل", f"تم تحميل {count} من ملفات Windows Natives بنجاح!")
            self.reset_button()

        self.root.after(0, finish_msg)

    def reset_button(self):
        def _reset():
            self.btn_action.config(state="normal", text="بدء تحميل Natives للويندوز", bg="#2196F3")
        self.root.after(0, _reset)

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftDownloaderApp(root)
    root.mainloop()
