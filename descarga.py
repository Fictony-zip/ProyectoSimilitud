import requests
from bs4 import BeautifulSoup
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

TOP_URL = "https://www.gutenberg.org/browse/scores/top"



# 1. Obtener el top 100 IDs de libros
def get_top100_ids():
    r = requests.get(TOP_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    h2 = soup.find("h2", string="Top 100 EBooks yesterday")
    ol = h2.find_next("ol")

    ids = []
    for a in ol.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/ebooks/"):
            try:
                ids.append(int(href.split("/")[2]))
            except:
                pass
        if len(ids) == 100:
            break

    return ids


# 2. Obtener el título del libro
def get_title(book_id):
    url = f"https://www.gutenberg.org/ebooks/{book_id}"
    r = requests.get(url)
    if r.status_code != 200:
        return str(book_id)

    soup = BeautifulSoup(r.text, "html.parser")
    title_tag = soup.find("title")

    if not title_tag:
        return str(book_id)

    title = title_tag.text.split(" by ")[0].replace(" - Free Ebook", "").strip()

    for ch in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        title = title.replace(ch, '')

    return title


# 3. Descargar
def download_book(book_id, outdir="books"):
    os.makedirs(outdir, exist_ok=True)

    title = get_title(book_id)
    filename = f"{outdir}/{title}.txt"

    urls = [
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt",
        f"https://www.gutenberg.org/files/{book_id}/{book_id}.txt.utf-8"
    ]

    for url in urls:
        resp = requests.get(url)
        if resp.status_code == 200 and len(resp.text) > 300:
            with open(filename, "w", encoding="utf-8", errors="ignore") as f:
                f.write(resp.text)
            print(f"[OK] {title}")
            return True

    print(f"[FAIL] {book_id}")
    return False


# 4. Main
def main():
    print("Obteniendo los IDs del top 100...")
    ids = get_top100_ids()
    print(f"Total IDs obtenidos: {len(ids)}\n")

    for i, book_id in enumerate(ids, start=1):
        print(f"{i}/100  ->  descargando {book_id} ...")
        download_book(book_id)


if __name__ == "__main__":
    main()
