import requests
import subprocess
import json
import qrcode
import base64

def parse_proxy_line(line):
    # Преобразует строку ip:port:login:password в socks5h://login:password@ip:port
    parts = line.strip().split(':')
    if len(parts) == 4:
        ip, port, login, password = parts
        return f"socks5h://{login}:{password}@{ip}:{port}"
    else:
        # Если строка уже в формате ссылки, возвращаем как есть
        return line.strip()

def get_random_proxy():
    with open("workingproxy.txt", "r") as f:
        lines = [parse_proxy_line(line) for line in f if line.strip()]
    proxy_url = lines[0] if lines else None
    if proxy_url is not None:
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    else:
        return None

# Если не нужен прокси (например, через TOR), закомментируй этот блок:
proxies = get_random_proxy()

def gen_wg_keys():
    wg_path = r"C:\Program Files\WireGuard\wg.exe"  # Укажите свой путь к wg.exe
    priv = subprocess.check_output([wg_path, 'genkey']).decode().strip()
    pub = subprocess.run([wg_path, 'pubkey'], input=priv.encode(), capture_output=True).stdout.decode().strip()
    return priv, pub

def register_device(api, pub):
    headers = {'user-agent': '', 'content-type': 'application/json'}
    data = {
        "install_id": "",
        "tos": "2025-01-01T00:00:00.000Z",
        "key": pub,
        "fcm_token": "",
        "type": "ios",
        "locale": "en_US"
    }
    resp = requests.post(api + "/reg", headers=headers, data=json.dumps(data), proxies=proxies)
    return resp.json()

def enable_warp(api, id_, token):
    headers = {
        'user-agent': '',
        'content-type': 'application/json',
        'authorization': f'Bearer {token}'
    }
    data = {'warp_enabled': True}
    resp = requests.patch(f"{api}/reg/{id_}", headers=headers, data=json.dumps(data), proxies=proxies)
    return resp.json()

def make_config(priv, client_ipv4, client_ipv6, peer_pub):
    return f"""[Interface]
PrivateKey = {priv}
Address = {client_ipv4}, {client_ipv6}
DNS = 1.1.1.1, 2606:4700:4700::1111, 1.0.0.1, 2606:4700:4700::1001

[Peer]
PublicKey = {peer_pub}
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = 188.114.99.224:1002
"""

def safe_get(d, *keys):
    for key in keys:
        d = d.get(key, {})
    return d or None

def main():
    print("Генерируем ключи WireGuard...")
    priv, pub = gen_wg_keys()

    api_versions = [
    "v0a769", "v0i1909051800", "v0a215"
    ]

    reg = None
    api = None
    for version in api_versions:
        api = f"https://api.cloudflareclient.com/{version}"
        try:
            reg = register_device(api, pub)
            if "result" in reg:
                break
        except Exception:
            continue
    else:
        print("Не удалось зарегистрировать устройство ни на одной из версий API.")
        return

    print("Регистрируем устройство в Cloudflare...")
    id_ = reg["result"]["id"]
    token = reg["result"]["token"]

    print("Включаем WARP...")
    conf_data = enable_warp(api, id_, token)

    peer_pub = conf_data['result']['config']['peers'][0]['public_key']
    client_ipv4 = conf_data['result']['config']['interface']['addresses']['v4']
    client_ipv6 = conf_data['result']['config']['interface']['addresses']['v6']

    config = make_config(priv, client_ipv4, client_ipv6, peer_pub)
    print("\n########## НАЧАЛО КОНФИГА ##########")
    print(config)
    print("########### КОНЕЦ КОНФИГА ###########\n")

    # Генерируем QR-код
    print("QR-код для AmneziaWG:")
    qr = qrcode.QRCode()
    qr.add_data(config)
    qr.make(fit=True)
    qr.print_ascii(invert=True)

    # Сохраняем конфиг в файл
    with open("WARP.conf", "w") as f:
        f.write(config)
    print("\nКонфиг сохранён в файл WARP.conf")

    # Генерируем base64-ссылку для загрузки
    conf_base64 = base64.b64encode(config.encode()).decode()
    link = f"https://immalware.vercel.app/download?filename=WARP.conf&content={conf_base64}"
    print(f"Скачать конфиг файлом: {link}")

if __name__ == "__main__":
    main()