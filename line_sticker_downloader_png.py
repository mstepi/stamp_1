import os
import json
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://store.line.me/stickershop/product/{}/ja"

def get_sticker_data(product_id):
    """指定したLINEスタンプのページから全スタンプ情報を取得"""
    url = BASE_URL.format(product_id)
    response = requests.get(url)

    if response.status_code != 200:
        print("ページが見つかりません。IDを確認してください。")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    sticker_data_list = []

    for tag in soup.find_all("li", {"class": "mdCMN09Li"}):
        data_preview = tag.get("data-preview")
        if data_preview:
            try:
                data = json.loads(data_preview.replace("&quot;", '"'))
                sticker_data_list.append(data)
            except json.JSONDecodeError:
                print("JSONの解析に失敗しました")

    return sticker_data_list

def download_image(url, save_path):
    """指定したURLの画像をダウンロード"""
    if not url:
        print(f"URLがありません: {save_path}")
        return
    
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"Downloaded: {save_path}")
    else:
        print(f"Failed to download: {url}")

def download_sticker_pack(product_id, base_dir="stickers"):
    """スタンプパックのすべての画像を、IDごとのフォルダに保存"""
    save_dir = os.path.join(base_dir, str(product_id))
    os.makedirs(save_dir, exist_ok=True)
    
    sticker_data_list = get_sticker_data(product_id)

    if not sticker_data_list:
        print("スタンプが見つかりませんでした。")
        return
    
    for sticker_data in sticker_data_list:
        sticker_id = sticker_data["id"]
        static_url = sticker_data.get("staticUrl")
        fallback_url = sticker_data.get("fallbackStaticUrl")
        animation_url = sticker_data.get("animationUrl")
        popup_url = sticker_data.get("popupUrl")

        # ポップアップスタンプ
        if popup_url:
            file_ext = ".png" if "png" in popup_url else ".gif"
            save_path = os.path.join(save_dir, f"{sticker_id}_popup{file_ext}")
            download_image(popup_url, save_path)
        # アニメーションスタンプ
        elif animation_url:
            file_ext = ".png" if "png" in animation_url else ".gif"
            save_path = os.path.join(save_dir, f"{sticker_id}_anim{file_ext}")
            download_image(animation_url, save_path)
        # 通常スタンプ
        elif static_url:
            save_path = os.path.join(save_dir, f"{sticker_id}.png")
            download_image(static_url, save_path)
        # フォールバック画像
        elif fallback_url:
            save_path = os.path.join(save_dir, f"{sticker_id}_fallback.png")
            download_image(fallback_url, save_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("使い方: python line_sticker_downloader.py <スタンプID>")
        sys.exit(1)

    product_id = sys.argv[1]
    download_sticker_pack(product_id)
