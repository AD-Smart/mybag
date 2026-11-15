import os
import json
import urllib.request
from pathlib import Path

def download_windows_natives(json_file_path, output_dir="windows_natives"):
    """
    قراءة ملف JSON الخاص بنسخة ماينكرافت وتحميل مكتبات الـ Windows Natives فقط.
    """
    # تنظيف مسار الملف من علامات التنصيص إن وجدت
    json_file_path = json_file_path.strip('"\'')

    if not os.path.exists(json_file_path):
        print(f"[-] خطأ: الملف غير موجود في المسار المحدد: {json_file_path}")
        return

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[-] خطأ أثناء قراءة ملف الـ JSON: {e}")
        return

    libraries = data.get("libraries", [])
    
    # إنشاء مجلد الحفظ
    os.makedirs(output_dir, exist_ok=True)
    
    downloaded_count = 0
    print("[+] جاري فحص المكتبات والبحث عن ملفات Windows Natives...")

    for lib in libraries:
        natives = lib.get("natives", {})
        downloads = lib.get("downloads", {})
        
        # التحقق مما إذا كانت المكتبة تحتوي على تعريف لـ windows ضمن الـ natives
        if "windows" in natives:
            classifier_key = natives["windows"]
            classifiers = downloads.get("classifiers", {})
            
            # استبدال المتغيرات المحتملة مثل ${arch} إذا وجدت في المفتاح
            # وغالباً تكون مفاتيح جاهزة مثل natives-windows أو natives-windows-64
            native_info = None
            
            # البحث المباشر عن المفتاح
            if classifier_key in classifiers:
                native_info = classifiers[classifier_key]
            else:
                # بحث مرن عن أي مفتاح يحتوي على كلمة windows في التصنيفات
                for k, v in classifiers.items():
                    if "windows" in k.lower():
                        native_info = v
                        break
            
            # إذا وجدنا معلومات التحميل الخاصة بالملف
            if native_info:
                url = native_info.get("url")
                path_str = native_info.get("path")
                
                if url and path_str:
                    file_name = os.path.basename(path_str)
                    file_path = os.path.join(output_dir, file_name)
                    
                    print(f"[تحميل] {file_name}...")
                    try:
                        urllib.request.urlretrieve(url, file_path)
                        downloaded_count += 1
                    except Exception as e:
                        print(f"[-] فشل تحميل {file_name}: {e}")

    print(f"\n[تم بنجاح!] تم تحميل {downloaded_count} من ملفات Windows Natives.")
    print(f"[*] تم حفظ الملفات في المجلد: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    print("=== أداة تحميل Windows Natives لماينكرافت ===")
    path_input = input("أدخل مسار ملف الـ JSON (مثال: /sdcard/Download/1.20.4.json): ")
    download_windows_natives(path_input)
