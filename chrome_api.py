from flask import Flask, request, jsonify
import time
import requests
import json
import threading

app = Flask(__name__)

HEADERS = {
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "origin": "https://proxy.owlproxy.com",
    "referer": "https://proxy.owlproxy.com/",
    "accept": "application/json, text/plain, */*",
    "appversion": "2007000",
    "clienttype": "web"
}

BOT_TOKEN = "8795125731:AAGtIs-9iWnprqDEP7T38t54H6gCaY04xIs"

CLAIM_STATUSES = {}

def send_tg_msg(chat_id, text, topic_id=None, parse_mode=None, msg_id=None):
    if msg_id:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
        payload = {"chat_id": chat_id, "message_id": msg_id, "text": text}
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        if topic_id:
            payload["message_thread_id"] = topic_id
            
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        res = requests.post(url, json=payload).json()
        if res.get("ok"):
            return res.get("result", {}).get("message_id")
    except:
        pass
    return None

def do_browser_login(email, password, chat_id=None, topic_id=None, caption_prefix=None):
    from seleniumbase import Driver
    driver = None
    try:
        driver = Driver(uc=True, no_sandbox=True, disable_gpu=True)
        driver.get("https://proxy.owlproxy.com/")
        time.sleep(5) # Wait for page to load
        
        # 1. Switch to Log in tab
        js_switch = """
        let elements = document.querySelectorAll('span, a, div');
        for (let el of elements) {
            if (el.innerText && el.innerText.includes('Log In Now') && el.children.length === 0) {
                el.click();
                break;
            }
        }
        """
        driver.execute_script(js_switch)
        time.sleep(2)
        
        # 2. Fill credentials and submit
        js_fill = f"""
        let inputs = document.querySelectorAll('input');
        for (let inp of inputs) {{
            if (inp.type === 'email' || (inp.type === 'text' && inp.placeholder && inp.placeholder.toLowerCase().includes('email'))) {{
                inp.value = '{email}';
                inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
            if (inp.type === 'password') {{
                inp.value = '{password}';
                inp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }}
        }}
        let buttons = document.querySelectorAll('button');
        for (let btn of buttons) {{
            let text = btn.innerText.toLowerCase().trim();
            if (text === 'log in' || text === 'login' || text === 'sign in') {{
                btn.click();
                break;
            }}
        }}
        """
        driver.execute_script(js_fill)
        time.sleep(3)
        
        if chat_id:
            try:
                import requests
                import os
                BOT_TOKEN = "8284450010:AAEDxODh46GHFm01oQjVIipik1lSbs_qfMc"
                driver.save_screenshot("step2_filled.png")
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
                caption_text = f"Chrome API: Credentials submitted for {email}"
                if caption_prefix:
                    caption_text = f"{caption_prefix}\n{caption_text}"
                data = {"chat_id": chat_id, "caption": caption_text, "parse_mode": "Markdown"}
                if topic_id:
                    data["message_thread_id"] = topic_id
                with open("step2_filled.png", "rb") as photo:
                    requests.post(url, data=data, files={"photo": photo})
                os.remove("step2_filled.png")
            except Exception as e:
                print("Failed to send screenshot:", e)
                
        return {"status": "success", "message": "Browser login executed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

@app.route("/run-browser", methods=["POST"])
def run_browser():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    chat_id = data.get("chat_id")
    topic_id = data.get("topic_id")
    
    if not email or not password:
        return jsonify({"status": "error", "message": "Email and password required"}), 400
        
    result = do_browser_login(email, password, chat_id, topic_id)
    return jsonify(result)

@app.route("/api/sms", methods=["POST"])
def api_sms():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"code": 400, "msg": "Missing email"})
    url = "https://api.owlproxy.com/owlproxy/api/sms/smsSend"
    payload = {"smsType": 2, "mobilePhone": email, "channel": "owlagcphkck"}
    try:
        res = requests.post(url, headers=HEADERS, json=payload)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"code": 500, "msg": str(e)})

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    try:
        url = "https://api.owlproxy.com/owlproxy/api/user/login"
        payload = data.get("payload", {})
        res = requests.post(url, headers=HEADERS, json=payload)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"code": 500, "msg": str(e)})

@app.route("/api/tempmail/generate", methods=["POST", "GET"])
def tempmail_generate():
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.post("https://web2.temp-mail.org/mailbox", headers=headers, timeout=15)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({"code": 500, "msg": str(e)})

@app.route("/api/tempmail/poll_otp", methods=["POST"])
def tempmail_poll_otp():
    data = request.json
    token = data.get("token")
    if not token:
        return jsonify({"code": 400, "msg": "Missing token"})
        
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        import re
        for _ in range(5):
            res = requests.get("https://web2.temp-mail.org/messages", headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                messages = data.get("messages", [])
                if messages:
                    body = messages[0].get("bodyPreview", "") + " " + messages[0].get("subject", "")
                    match = re.search(r'\b(\d{6})\b', body)
                    if match:
                        return jsonify({"code": 200, "otp": match.group(1)})
            time.sleep(15)
            
        return jsonify({"code": 404, "msg": "OTP not found after 75 seconds"})
    except Exception as e:
        return jsonify({"code": 500, "msg": str(e)})

def claim_worker(token, userid, email, password, chat_id, topic_id, is_auto, retries, msg_id=None):
    CLAIM_STATUSES[token] = {"status": "running"}
    
    admin_msg_id = None
    if not is_auto:
        admin_msg = f"[User ID: {chat_id}](tg://user?id={chat_id})\nAsking claim.."
        admin_msg_id = send_tg_msg(-1004487523301, admin_msg, 1449, parse_mode="Markdown")
        send_tg_msg(chat_id, "Asking claim..", msg_id=msg_id)
        
    try:
        if not is_auto:
            caption_prefix = f"[User ID: {chat_id}](tg://user?id={chat_id})"
            do_browser_login(email, password, -1004487523301, 1449, caption_prefix=caption_prefix)
        else:
            do_browser_login(email, password, chat_id, topic_id)
        time.sleep(3)
    except Exception as e:
        pass

    claim_url = "https://api.owlproxy.com/owlproxy/api/newUserGuide/getNewUserReceiveTraffic?guideId=10003"
    claim_headers = HEADERS.copy()
    claim_headers["token"] = str(token)
    claim_headers["userid"] = str(userid)
    
    if not is_auto:
        admin_msg = f"[User ID: {chat_id}](tg://user?id={chat_id})\nClaim busy. I will keep retrying (up to {retries} times)..."
        send_tg_msg(-1004487523301, admin_msg, 1449, msg_id=admin_msg_id, parse_mode="Markdown")
        send_tg_msg(chat_id, f"Claim busy. I will keep retrying (up to {retries} times)...", msg_id=msg_id)
        
    for attempt in range(retries):
        try:
            claim_res = requests.get(claim_url, headers=claim_headers)
            claim_data = claim_res.json()
            code = claim_data.get("code")
            if code == 200:
                if not is_auto:
                    admin_msg = f"[User ID: {chat_id}](tg://user?id={chat_id})\n✅ Claim Successful 200 MB !"
                    send_tg_msg(-1004487523301, admin_msg, 1449, msg_id=admin_msg_id, parse_mode="Markdown")
                    send_tg_msg(chat_id, "✅ Claim Successful 200 MB !", msg_id=msg_id)
                else:
                    send_tg_msg(-1004487523301, f"✅ Account `{email}` Claim Successful 200 MB !", 10, parse_mode="Markdown")
                
                # Auto create proxy
                proxy_str = create_proxy_logic(token, userid, chat_id, is_auto, topic_id, msg_id, email, password)
                
                CLAIM_STATUSES[token] = {
                    "status": "success",
                    "email": email,
                    "password": password,
                    "proxy_str": proxy_str,
                    "userid": userid
                }
                break
            else:
                time.sleep(5)
        except:
            time.sleep(5)
    else:
        # Failed
        if not is_auto:
            admin_msg = f"[User ID: {chat_id}](tg://user?id={chat_id})\n❌ Claim failed after {retries} retries."
            send_tg_msg(-1004487523301, admin_msg, 1449, msg_id=admin_msg_id, parse_mode="Markdown")
            # We don't send failure message to the user anymore per request
        else:
            send_tg_msg(-1004487523301, f"❌ Account `{email}` Claim Failed after {retries} retries.", 10, parse_mode="Markdown")
        CLAIM_STATUSES[token] = {"status": "failed"}

def create_proxy_logic(token, userid, chat_id, is_auto, topic_id, msg_id=None, email=None, password=None):
    url = "https://api.owlproxy.com/owlproxy/api/vcDynamicGood/createProxy"
    headers = HEADERS.copy()
    headers["token"] = str(token)
    headers["userid"] = str(userid)
    payload = {
        "proxyType": "socks5",
        "proxyHost": "change4.owlproxy.com:7778",
        "countryCode": "AO",
        "state": "",
        "city": "",
        "time": 5,
        "goodNum": 1,
        "format": "protocol://ip:port:user:pass"
    }
    try:
        res = requests.post(url, headers=headers, json=payload)
        data = res.json()
        if data.get("code") == 200 and data.get("data"):
            p = data["data"][0]
            proxy_str = f"➦Type: `{p.get('proxyType', 'socks5')}`\n➦Host: `{p.get('proxyHost')}`\n➦Port: `{p.get('proxyPort')}`\n➦UserName: `{p.get('userName')}`\n➦password: `{p.get('password')}`"
            msg = f"✅ Purchase Successful!\n➦Email: `{email}`\n\n{proxy_str}"
            if is_auto:
                send_tg_msg(-1004487523301, msg, 10, parse_mode="Markdown")
            else:
                send_tg_msg(chat_id, msg, topic_id, msg_id=msg_id, parse_mode="Markdown")
            return proxy_str
        else:
            err = f"❌ Proxy creation failed: {data.get('msg')}"
            if is_auto:
                send_tg_msg(-1004487523301, err, 10)
            else:
                send_tg_msg(chat_id, err, topic_id, msg_id=msg_id)
            return None
    except Exception as e:
        return None

@app.route("/api/claim", methods=["POST"])
def api_claim():
    data = request.json
    token = data.get("token")
    userid = data.get("userid")
    email = data.get("email")
    password = data.get("password")
    chat_id = data.get("chat_id")
    topic_id = data.get("topic_id")
    is_auto = data.get("is_auto", False)
    retries = data.get("retries", 100)
    msg_id = data.get("msg_id")
    
    threading.Thread(target=claim_worker, args=(token, userid, email, password, chat_id, topic_id, is_auto, retries, msg_id)).start()
    return jsonify({"status": "started"})

@app.route("/api/claim_status/<token>", methods=["GET"])
def api_claim_status(token):
    status = CLAIM_STATUSES.get(token, {"status": "unknown"})
    return jsonify(status)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
