import requests, json, warnings
warnings.filterwarnings("ignore")

url = "https://jtd.wxdnet.cn:8080/system/wechat/certificate/"
payload = {
  "method": "POST",
  "url_path": "/v3/pay/transactions/jsapi",
  "query_string": "",
  "nonce_str": "c5ac7061fccab6bf3e254dcf98995b8c",
  "timestamp": 1704067200,
  "body": json.dumps({
    "appid": "wxd678efh567hg6787",
    "mchid": "1900007291",
    "description": "Image形象店-深圳腾大-QQ公仔",
    "out_trade_no": "1217752501201407033233368018",
    "notify_url": "https://www.weixin.qq.com/wxpay/pay.php",
    "amount": {"total": 100, "currency": "CNY"},
    "payer": {"openid": "oUpF8uMuAJO_M2pxb1Q9zNjWeS6o"}
  }, ensure_ascii=False)
}
r = requests.post(url, json=payload, verify=False, timeout=20, headers={"Accept":"application/json"})
print(r.status_code)
print(r.text)