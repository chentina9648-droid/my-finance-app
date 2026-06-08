import urllib.parse
from urllib.parse import urlparse, parse_qs, unquote
from bs4 import BeautifulSoup
from curl_cffi import requests
import sys
import io

# 確保 stdout 為 UTF-8
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
except Exception:
    pass

def get_real_url(ddg_url):
    """將 DuckDuckGo 的跳轉連結還原成真實網址"""
    if ddg_url.startswith("//"):
        ddg_url = "https:" + ddg_url
    parsed = urlparse(ddg_url)
    qs = parse_qs(parsed.query)
    if "uddg" in qs:
        return unquote(qs["uddg"][0])
    return ddg_url

def search_hotel_reviews(hotel_name, site_filter=None):
    """
    搜尋特定飯店的評價與心得。
    site_filter: 可指定 'dcard'、'ptt' 或 None (全部)
    """
    query = f"{hotel_name} 評價"
    if site_filter == "dcard":
        query += " dcard"
    elif site_filter == "ptt":
        query += " ptt"
    else:
        query += " dcard ptt 旅遊板"
        
    encoded_query = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://duckduckgo.com/"
    }
    
    try:
        # 使用 curl_cffi 模擬 Chrome 110
        response = requests.get(url, headers=headers, impersonate="chrome110", timeout=12)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, "html.parser")
        results = []
        for result in soup.find_all("div", class_="result"):
            # 排除廣告
            if "result--ad" in result.get("class", []):
                continue
                
            title_tag = result.find("a", class_="result__a")
            snippet_tag = result.find("a", class_="result__snippet")
            
            if title_tag:
                title = title_tag.get_text(strip=True)
                raw_link = title_tag["href"]
                link = get_real_url(raw_link)
                
                # 過濾明顯的廣告或跳轉頁面
                if "duckduckgo.com/y.js" in raw_link or "doubleclick.net" in link or "googleadservices" in link:
                    continue
                    
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                
                # 判斷來源網站
                source = "網路評價"
                if "dcard.tw" in link:
                    source = "Dcard"
                elif "ptt.cc" in link:
                    source = "PTT"
                elif "pixnet.net" in link or "sainteat.tw" in link or "itravelblog" in link or "saratrip" in link:
                    source = "旅遊部落格"
                elif "trip.com" in link or "agoda" in link or "booking" in link:
                    source = "訂房網反饋"
                
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "source": source
                })
        return results
    except Exception as e:
        print(f"Search error: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    import json
    test_hotel = "首爾麻浦魯內飯店"
    print(f"--- 測試搜尋飯店: {test_hotel} ---")
    reviews = search_hotel_reviews(test_hotel)
    print(json.dumps(reviews[:5], indent=2, ensure_ascii=False))
