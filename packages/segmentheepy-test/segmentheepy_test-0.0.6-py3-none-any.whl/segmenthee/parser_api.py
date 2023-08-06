import re
import user_agents

from segmenthee.config import Config


def parse_lang(lang):
    if not isinstance(lang,str):
        return "other"
    return "hu" if "hu" in lang else "other"
    
def parse_user_agent(user_agent_string):
    user_agent = user_agents.parse(user_agent_string)
    device = ("mobile" if user_agent.is_mobile 
                else "tablet" if user_agent.is_tablet 
                else "desktop" if user_agent.is_pc
                else "other")
    os = ("ms" if user_agent.os.family.startswith("Windows")
               else "apple" if user_agent.os.family in ["Mac OS X", "iOS"]
               else "linux" if user_agent.os.family in ["Android","Chrome OS","Fedora","Linux","Ubuntu"]
               else "other")
    return device,os

facebookpattern = re.compile('http(s?)://(((www)|[a-z]+)\.)?(facebook|instagram)\.')
googlepattern = re.compile('http(s?)://(((www)|[a-z]+)\.)?google\.')
tiktokpattern = re.compile('http(s?)://((www)|[a-z]+\.)?tiktok\.')
shoppattern = re.compile(Config.SHOP_URL)
facebookexternalpattern = re.compile('facebookexternalhit')
googlebotpattern = re.compile('http://www.google.com/bot.html')

def parse_origin(origin: str) -> str:
    if not origin:
        return "other"
    # elif facebookexternalpattern.match(user_agent_string):
    #     return "fblink"
    # elif googlebotpattern.search(user_agent_string):
    #     return "ggbot"
    elif facebookpattern.match(origin):
        return "facebook"
    elif googlepattern.match(origin):
        return "google"
    elif shoppattern.match(origin):
        return "shop"
    elif tiktokpattern.match(origin):
        return "tiktok"
    else:
        return "other"

# def parse_category(category_string):
#     return category_dict.get(category_string,"other")

sort_set = {'default', 'name', 'price', 'order', 'relevance', 'date', 'rating', 'latest', 'discount', 'view'}

def parse_sort(sort_string):
    for key in sort_set:
        if key in sort_string:
            return key
    return sort_string
