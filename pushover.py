import http.client, urllib.request, urllib.parse, urllib.error
import config

def send_message(message,url=None,priority=0): 
    
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": config.pushover["token"],
        "user": config.pushover["user"],
        "message": message,
        "url": url,
        "priority": priority,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    
    
def send_message_alert(message,url=None,priority=0):

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": config.pushover["token"],
        "user": config.pushover["user"],
        "message": message,
        "url": url,
        "priority": priority,
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()    
    
    
if __name__ == "__main__":
    send_message("Test con coma y prioridad 0",priority=0)
