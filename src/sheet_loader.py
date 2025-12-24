import gspread
from oauth2client.service_account import ServiceAccountCredentials
from src.config import GCP_SA_KEY, SPREADSHEET_ID, SHEET_NAME

def get_stock_list():
    """スプレッドシートから銘柄コードのリストを取得する"""
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(GCP_SA_KEY, scope)
        client = gspread.authorize(creds)
        
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
        
        # A2からA列の最後までの値を取得
        # 日本株コード（数字4桁）を想定し、末尾に.Tがなければ付与する
        raw_values = sheet.col_values(1)[1:] # 1行目(ヘッダー)をスキップ
        
        stock_list = []
        for code in raw_values:
            code = str(code).strip()
            if not code:
                continue
            if not code.endswith(".T"):
                code = f"{code}.T"
            stock_list.append(code)
            
        return stock_list
    except Exception as e:
        print(f"Error loading spreadsheet: {e}")
        return []
