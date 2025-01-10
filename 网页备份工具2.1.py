import tkinter as tk
from tkinter import filedialog, messagebox
import os
import requests
import subprocess
from datetime import datetime
from threading import Thread
import webbrowser
from urllib.parse import urlparse

def backup_single_page(url, folder):
    try:
        # 获取网页内容
        response = requests.get(url)
        if response.status_code == 200:
            # 获取当前时间，用于文件命名
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            
            # 提取网页地址中的主机名（去掉协议部分）
            parsed_url = urlparse(url)
            site_name = parsed_url.netloc  # 取主机名部分
            path = parsed_url.path.strip('/').replace('/', '_')  # 处理路径部分，避免文件名包含斜杠
            
            # 如果路径为空，使用主机名作为文件名的一部分
            if not path:
                path = site_name

            # 生成文件名
            filename = f"{folder}/{site_name}_{path}_{timestamp}.html"

            # 将网页内容写入文件
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(response.text)
            messagebox.showinfo("成功", f"备份成功: {filename}")
        else:
            messagebox.showerror("错误", f"无法获取网页，状态码: {response.status_code}")
    except Exception as e:
        messagebox.showerror("错误", f"发生错误: {str(e)}")

def backup_full_site(url, folder):
    try:
        # 从URL中提取网站标题
        site_title = url.split("//")[-1].split("/")[0]
        
        # 获取当前时间
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # 创建文件夹名称
        backup_folder = f"{folder}/{site_title}_{timestamp}"
        os.makedirs(backup_folder, exist_ok=True)

        # 使用wget命令进行全站备份，将文件直接保存到主文件夹
        command = [
            "wget", "-m", "-p", "-E", "-k", "-K", "--no-parent", "-P", backup_folder, url
        ]
        subprocess.run(command, shell=True)  # 使用shell=True以确保在Windows上工作

        messagebox.showinfo("成功", f"全站备份完成，文件存储在: {backup_folder}")
    except Exception as e:
        messagebox.showerror("错误", f"发生错误: {str(e)}")

def select_folder():
    folder = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder)

def start_backup():
    url = url_entry.get()
    folder = folder_entry.get()
    if not url or not folder:
        messagebox.showerror("错误", "请输入网页地址和选择文件夹")
        return
    if not (url.startswith('http://') or url.startswith('https://')):
        messagebox.showerror("错误", "请输入有效的URL地址")
        return
    if backup_type.get() == 1:  # 选择单页面备份
        thread = Thread(target=backup_single_page, args=(url, folder))
        thread.start()
    else:  # 选择全站备份
        thread = Thread(target=backup_full_site, args=(url, folder))
        thread.start()

def browse_backup():
    backup_folder = folder_entry.get()
    if not os.path.isdir(backup_folder):
        messagebox.showerror("错误", "未选择有效的备份文件夹")
        return
    # 打开备份文件夹
    webbrowser.open(backup_folder)

# 创建主窗口
root = tk.Tk()
root.title("网页备份工具")

# 网页地址输入框
tk.Label(root, text="网页地址:").pack(padx=10, pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.pack(padx=10, pady=5)

# 文件夹选择按钮
tk.Label(root, text="备份存放文件夹:").pack(padx=10, pady=5)
folder_entry = tk.Entry(root, width=50)
folder_entry.pack(padx=10, pady=5)
folder_button = tk.Button(root, text="选择文件夹", command=select_folder)
folder_button.pack(padx=10, pady=5)

# 备份类型选择
backup_type = tk.IntVar()
backup_type.set(1)  # 默认单页面备份
tk.Label(root, text="备份类型:").pack(padx=10, pady=5)
single_page_rb = tk.Radiobutton(root, text="单页面备份", variable=backup_type, value=1)
single_page_rb.pack(padx=10, pady=5)
full_site_rb = tk.Radiobutton(root, text="全站备份", variable=backup_type, value=2)
full_site_rb.pack(padx=10, pady=5)

# 备份按钮
backup_button = tk.Button(root, text="开始备份", command=start_backup)
backup_button.pack(padx=10, pady=20)

# 浏览备份文件按钮
browse_button = tk.Button(root, text="浏览备份文件", command=browse_backup)
browse_button.pack(padx=10, pady=5)

# 启动GUI
root.mainloop()
