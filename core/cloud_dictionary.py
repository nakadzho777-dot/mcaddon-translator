import requests


class CloudDictionary:

    def __init__(self):

        self.base_url = "http://127.0.0.1:8000"
        self.token = "MCADDON-DEV-TOKEN"
        self.user_id = "local-user"

    # ----------------------------
    # 取得
    # ----------------------------
    def get(self, key: str):

        try:
            r = requests.get(f"{self.base_url}/get/{key}")
            return r.json().get("value")
        except:
            return None

    # ----------------------------
    # 追加（学習＋貢献）
    # ----------------------------
    def add(self, key: str, value: str):

        try:
            requests.post(
                f"{self.base_url}/add",
                json={
                    "key": key,
                    "value": value,
                    "token": self.token,
                    "user_id": self.user_id
                }
            )
        except:
            pass

    # ----------------------------
    # ランキング取得
    # ----------------------------
    def get_ranking(self):

        try:
            r = requests.get(f"{self.base_url}/ranking")
            return r.json()
        except:
            return []