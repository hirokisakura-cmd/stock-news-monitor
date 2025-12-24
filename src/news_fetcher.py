import yfinance as yf
from datetime import datetime, timedelta
import pytz

# ノイズ除去用キーワード
IGNORE_KEYWORDS = ["PR TIMES", "キャンペーン", "開催", "お知らせ", "募集", "オープン", "記念", "発売"]

# 悪材料・好材料のキーワード候補（一次選別用）
BAD_KEYWORDS = ["下方修正", "減益", "赤字", "損失", "暴落", "ストップ安", "提訴", "訴訟", "疑義", "監理", "廃止", "売却", "不祥事", "不正", "リコール"]
GOOD_KEYWORDS = ["上方修正", "増益", "復配", "増配", "自社株買い", "株式分割", "提携", "買収", "ストップ高", "最高益", "黒字化", "承認"]

def get_target_time_range():
    """現在のJST時刻に基づいて、取得すべきニュースの時間範囲を返す"""
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst)
    
    # 12:05起動の回 (前日17:00 〜 当日12:04:59)
    if 11 <= now.hour <= 13:
        end_dt = now.replace(hour=12, minute=4, second=59)
        start_dt = (now - timedelta(days=1)).replace(hour=17, minute=0, second=0)
        mode = "NOON_CHECK"
        
    # 17:00起動の回 (当日12:05 〜 当日16:59:59)
    elif 16 <= now.hour <= 18:
        start_dt = now.replace(hour=12, minute=5, second=0)
        end_dt = now.replace(hour=16, minute=59, second=59)
        mode = "EVENING_CHECK"
        
    else:
        # 手動実行などで時間がずれた場合の安全策（直近6時間）
        end_dt = now
        start_dt = now - timedelta(hours=6)
        mode = "MANUAL_CHECK"
        
    return start_dt, end_dt, mode

def fetch_stock_news(tickers):
    """yfinanceでニュースを一括取得し、時間とキーワードでフィルタする"""
    start_dt, end_dt, mode = get_target_time_range()
    print(f"[{mode}] Time Filter: {start_dt} ~ {end_dt} (JST)")
    
    # Tickerオブジェクトを一括作成
    stocks = yf.Tickers(" ".join(tickers))
    
    candidates = []

    for ticker in tickers:
        try:
            # yfinanceのnews取得 (個別銘柄ごとにアクセス)
            # ※一括取得メソッドはないためループするが、情報量は軽いので高速
            info = stocks.tickers[ticker].news
            
            for item in info:
                # タイムスタンプ判定 (Unix Time -> JST datetime)
                pub_time = datetime.fromtimestamp(item['providerPublishTime'], pytz.timezone('Asia/Tokyo'))
                
                # 1. 時間フィルタ
                if not (start_dt <= pub_time <= end_dt):
                    continue
                
                title = item['title']
                
                # 2. ノイズフィルタ
                if any(k in title for k in IGNORE_KEYWORDS):
                    continue
                
                # 3. 候補判定
                is_bad = any(k in title for k in BAD_KEYWORDS)
                is_good = any(k in title for k in GOOD_KEYWORDS)
                
                if is_bad or is_good:
                    candidates.append({
                        "ticker": ticker,
                        "title": title,
                        "time": pub_time.strftime('%m/%d %H:%M'),
                        "link": item['link'],
                        "type": "BAD" if is_bad else "GOOD" # とりあえずキーワードで仮分類
                    })
                    
        except Exception as e:
            continue

    return candidates
