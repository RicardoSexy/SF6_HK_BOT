import requests, json, pickle, time, logging
from bs4 import BeautifulSoup
from config import *
from cogs.module.bot import main

class Scaling:
    def __init__(self, id):
        self.url = f"https://www.streetfighter.com/6/buckler/profile/{id}"
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8,zh-TW;q=0.7,zh;q=0.6",
            "Cache-Control": "max-age=0",
            "Referer": "https://cid.capcom.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0"
        }
        self.data = {}
        self.id = id

    def checking(self):
        
        session = requests.Session()
        cookie_path = os.path.join(f'{bot_config().path}/data', 'cookies.pkl')
        try:
            with open(cookie_path, 'rb') as f:
                cookies = pickle.load(f)

            for cookie in cookies:
                if "buckler_r_id" in cookie['name']:
                    expiry = cookie.get('expiry')  
                    if (expiry - time.time()) < 86400:
                        logging.info('Cookies.pkl is gonna expired, Now run selenium')
                        main()
                    
            for cookie in cookies:
                if 'name' in cookie and 'value' in cookie:
                    session.cookies.set(cookie['name'], cookie['value'])
                    
            return session
        
        except:
            
            logging.info('Cookies.pkl not found, Now run selenium')
            main() 
            with open(cookie_path, 'rb') as f:
                cookies = pickle.load(f)
            for cookie in cookies:
                if 'name' in cookie and 'value' in cookie:
                    session.cookies.set(cookie['name'], cookie['value'])
            
            return session

    def fetch_data(self):
        
        session = self.checking()
        response = session.get(self.url, headers=self.headers)
        soup = BeautifulSoup(response.text, features="html.parser")
        self.fetch = soup.find('script', {'type': 'application/json', 'id': '__NEXT_DATA__'})
        return self.fetch.text

    def extract_data(self):

        datas = json.loads(self.fetch.text)
        props = datas.get("props", {}).get("pageProps", {})
        banner_info = props.get("fighter_banner_info", {})
        personal_info = banner_info.get("personal_info", {})
        fav_char_info = banner_info.get("favorite_character_league_info", {})
        online_status = banner_info.get("online_status_info", {})

        if not personal_info:
            self.data = 'Cookies expired, Please contact <@399538717812850688>. Thank you'
            return self.data

        self.data.update({
            '玩家名稱': personal_info.get("fighter_id"),
            '玩家ID': self.id,
            '角色名稱': banner_info.get("favorite_character_name"),
            '排名': fav_char_info.get("league_rank_info", {}).get("league_rank_name"),
            'LP': fav_char_info.get("league_point")
        })

        master_rating = fav_char_info.get("master_rating")
        if master_rating:
            self.data['MR'] = master_rating

        status = online_status.get("online_status_data", {}).get("online_status_name")
        battlehub = online_status.get("battlehub_region_name")
        battlehubid = online_status.get("battlehub_formated_server_no")
        if battlehub:
            self.data['Status'] = f"{status} {battlehub}#{battlehubid}"
        else:
            self.data['Status'] = status

    def run(self):
        try:
            self.fetch_data()
            self.extract_data()
            return self.data
        except requests.RequestException as e:
            return f"An error occurred while fetching data: {e}"
