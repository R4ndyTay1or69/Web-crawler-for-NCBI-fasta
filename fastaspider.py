import urllib.request
import urllib.error
import csv
import sys
import time
import ssl
import os
import re

def fetch_fasta_data(genbank_id, email, context):
    """
    获取指定 GenBank ID 的 FASTA 格式数据。

    参数:
        genbank_id (str): GenBank 登录号。
        email (str): 用户邮箱地址（NCBI 要求）。
        context (ssl.SSLContext): SSL 上下文，用于处理证书验证。

    返回:
        str: FASTA 格式的数据，如果成功获取；否则返回 None。
    """
    url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" \
          f"db=nucleotide&id={genbank_id}&rettype=fasta&retmode=text&email={email}"
    try:
        with urllib.request.urlopen(url, context=context) as response:
            data = response.read().decode('utf-8')
            return data
    except urllib.error.URLError as e:
        print(f"无法获取 {genbank_id} 的 FASTA 信息: {e}")
        return None
    except Exception as e:
        print(f"解析 {genbank_id} 时出错: {e}")
        return None


def save_individual_file(genbank_id, fasta_data, extension="fasta"):
    """
    将 FASTA 数据保存到 tmp 。

    参数:
        genbank_id (str): GenBank 登录号。
        fasta_data (str): FASTA 格式的数据。
        extension (str): 文件扩展名，默认为 'fasta'。
    """
    tmp_dir = "tmp"
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    # 去掉 GenBank ID 后的扩展名（如 '.1'）
    base_genbank_id = re.sub(r'\.\d+$', '', genbank_id)
    file_path = os.path.join(tmp_dir, f"{base_genbank_id}.{extension}")

    try:
        with open(file_path, "w", encoding='utf-8') as file:
            file.write(fasta_data)
    except Exception as e:
        print(f"无法保存 {genbank_id} 的文件: {e}")

def main(id_file):
    """
    处理 GenBank ID 下载 FASTA 文件。
        id_file (str): 包含 GenBank ID 的文件路径。
    """
    # 设置邮箱
    email = "00000000000@qq.com"  # 请替换为您的邮箱地址

    # 创建 SSL 上下文 忽略证书验证错误
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # 读取 GenBank 登录号列表
    try:
        with open(id_file, "r") as file:
            genbank_ids = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"文件 {id_file} 未找到。")
        sys.exit(1)


    for idx, genbank_id in enumerate(genbank_ids, 1):
        print(f"正在处理 {idx}/{len(genbank_ids)}: {genbank_id}")
        tmp_dir = "tmp"
        # 去掉 GenBank ID 后的扩展名（如 '.1'）
        base_genbank_id = re.sub(r'\.\d+$', '', genbank_id)
        file_path = os.path.join(tmp_dir, f"{base_genbank_id}.fasta")

        # 检查文件是否已存在且大小大于10KB
        if os.path.exists(file_path) and os.path.getsize(file_path) > 10 * 1024:
            #print(f"文件 {file_path} 已存在且大小大于10KB，跳过下载。")
            try:
                with open(file_path, "r", encoding='utf-8') as file:
                    fasta_data = file.read()
            except Exception as e:
                print(f"无法读取已存在的文件 {file_path}: {e}")
                fasta_data = None
        else:
            # 下载并保存文件
            fasta_data = fetch_fasta_data(genbank_id, email, context)
            if fasta_data:
                save_individual_file(genbank_id, fasta_data)

        # 遵守 NCBI 的请求频率限制（最多 3 请求/秒）
        time.sleep(0.36)  #约每 0.36 秒一个请求
    print("fasta文件已保存到 tmp 文件夹中")
    print("fasta has been downloaded in the tmp folder")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please change the email address to your own in line 67.")
        print("Usage: python fastaworm.py id.txt")
        sys.exit(1)
    id_file = sys.argv[1]
    main(id_file)