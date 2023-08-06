import datetime
import copy
import json
from typing import Union, Tuple, List, Dict, Any
import numpy as np
import xgboost
from segmenthee.config import Config
from segmenthee import parser_api
import statsmodels.api as sm

ABANDONER = 1
BUYER = 0

FILE_NAME = 'xgbm.sav'
SCORE_THRESHOLD = Config.SCORE_THRESHOLD
FRUSTRATION_TOLERANCE = Config.FRUSTRATION_TOLERANCE

# event classes

classcount = 0
def nextclassindex():
    global classcount
    retval = classcount
    classcount += 1
    return retval

#collect name from classindex
classnames = dict()

params = {
    "clickrate": 0.5,
    "actionseparation": (0.5, 0.005),
    "actionaffinity": (0.0, 0.025, 0.03),
    "timeaffinity": (0.0, 0.025, 0.03),
    "categoryaffinity": (0.025, 0.03),
    "carttotaltrend": (0.05, 0.025),
    "cartcounttrend": (0.01, 0.04),
    "avgpricemanipulation": (0.05, 0.025),
    "lastpriceviewedtrend": (0.05, 0.025),
    "tabcounttrend": (0.01, 0.04),
    "redirectstrend": (0.25, 0.01),
    "tabtypetrend": (0.25, 0.01),
    "navigationtrend": (0.25, 0.01),
    "referrertrend": (0.25, 0.01),
    "pagetrend": (0.01, 0.04),
    "sorttrend": (0.25, 0.01)
}

MAX_CATEGORY = 6
tabtype_dict = {'New':0, 'Existing':1}
navigation_dict = {'NAVIGATE':0,'FORWARD':1,'BACK':2,'RELOAD':3}
origin_dict = {"facebook":0,"google":1,"shop":2}
sort_dict = {'default':0, 'name':1, 'price':2, 'order':3, 'relevance':4, 'date':5, 'rating':6, 'latest':7, 'discount':8, 'view':9}


def get_navigation(navigation: str) -> int:
    return navigation_dict.get(navigation, len(navigation_dict))


def get_tabtype(tabtype: str) -> int:
    return tabtype_dict.get(tabtype, len(tabtype_dict))


def get_referrer(referrer: str) -> int:
    r = parser_api.parse_origin(referrer)
    return origin_dict.get(r, len(origin_dict))


def get_sort(sort: str) -> int:
    return sort_dict.get(parser_api.parse_sort(sort),len(sort_dict))


def get_page(page: str) -> int:
    try:
        return int(page)
    except:
        return 0

def get_utm_source(item: Dict) -> str:
    keys = item.keys()
    if 'utm_source' in keys:
        return item.get('utm_source')
    if 'gclid' in keys:
        return 'google'
    if 'fbclid' in keys:
        return 'facebook'
    return ''


# timeweights = json.load(open("vagyaim/timeweights.json"))

def FeatureNotAvailableWarning(feature_str):
    print(f"Warning: {feature_str} not in state.")

def LogCategory(retval,coeffs,category):
    if "categoryaffinity" not in retval:
        return None
    arr = retval["categoryaffinity"]
    categoryattfacts = coeffs["categoryaffinity"]
    for attix in range(len(categoryattfacts)):
        attfact = categoryattfacts[attix]
        for cat in range(MAX_CATEGORY):
            arr[attix][cat] *= attfact
    if category >= 0:
        for attix in range(len(categoryattfacts)):
            arr[attix][category] += 1 - categoryattfacts[attix]
        
def UpdateClickrates(retval,time,coeff,initialize=False):
    if "z_score" not in retval:
        return None
    if retval["clickrate_var"] > 0.0:
        retval["z_score"] = (time - retval["lastactioneventtime"] - retval["clickrate_avg"]) / (retval["clickrate_var"]**(1/2))
    if initialize:
        first_delta_time = retval["lastactioneventtime"] - retval["sessionstart"]
        second_delta_time = time - retval["lastactioneventtime"]
        retval["clickrate_avg"] = (1-coeff)*first_delta_time + coeff*second_delta_time
        retval["clickrate_squares"] = (1-coeff)*first_delta_time**2 + coeff*second_delta_time**2
        retval["clickrate_var"] = retval["clickrate_squares"] - retval["clickrate_avg"]**2
    else:
        delta_time = time-retval["lastactioneventtime"]
        retval["clickrate_avg"] *= (1-coeff)
        retval["clickrate_avg"] += coeff*delta_time
        retval["clickrate_squares"] *= (1-coeff)
        retval["clickrate_squares"] += coeff*delta_time**2
        retval["clickrate_var"] = retval["clickrate_squares"] - retval["clickrate_avg"]**2
    
def UpdateAttribute(retval, coeffs, feature, new_value):
    if feature not in retval:
        return None
    values = retval[feature]
    featureattfacts = coeffs[feature]
    for attix in range(len(featureattfacts)):
        values[attix] *= featureattfacts[attix]
        values[attix] += (1 - featureattfacts[attix]) * new_value
        
def UpdateAffinity(retval, coeffs, feature, update_index):
    if feature not in retval:
        return None
    values = retval[feature]
    featureattfacts = coeffs[feature]
    if (feature == "actionaffinity"):
        difffeature = "actiondifference"
        for attix in range(len(featureattfacts)):
            for act in range(len(values[0])):
                retval["actiondifference"][attix][act] = -(1 - featureattfacts[attix]) * values[attix][act]
            retval["actiondifference"][attix][update_index] += (1 - featureattfacts[attix])
    for attix in range(len(featureattfacts)):
        for act in range(len(values[0])):
            values[attix][act] *= featureattfacts[attix]
        values[attix][update_index] += 1 - featureattfacts[attix]
        
def GetCoefficients(coeffs, params, delta_time):
    ''' exp(-lambda * delta_time) '''
    for key in params:
        if not isinstance(params[key],list):
            continue
        coeffs[key][-1] = np.exp(-params[key][-1] * delta_time)

def CalculateUnalikeability(arr):
    n = len(arr)
    if n == 1:
        return 0 # may be better to return 1
    s = 0
    for i in range(n-1):
        for j in range(i+1,n):
            if arr[i] != arr[j]:
                s += 1
    u = 2*s/(n**2 - n)
    return u

def CalculateAutocorrelation(arr):
    if len(arr) == 1 or CalculateUnalikeability(arr) == 0:
        return 0
    s = set()
    for i in arr:
        s.add(i)
    enc = {value:idx for idx,value in enumerate(s)}
    arr = [enc[val] for val in arr]
    autocorr = sm.tsa.acf(arr, nlags =len(arr) - 1)[1:]
    return max(autocorr, key=abs)

class SessionBodyEvent:
    def __init__(self, time: int):
        self.time = time

    def Update(self,prevstate):
        retval = copy.deepcopy(prevstate)
        retval["lastbodyeventtime"] = self.time
        return retval
    
    @classmethod
    def classindex(cls):
        return cls.cindex
    
    def is_closing(self):
        return False

    def is_success(self) -> bool:
        return False

    def skip_update(self) -> bool:
        return False

    JSON_FIELDS: List[str] = [
        'time', 'delta_count', 'delta_total', 'event_label', 'referrer', 'tabcount', 'tabtype',
        'navigation', 'redirects', 'title', 'utm_source', 'utm_medium', 'category_id', 'price',
        'product_id', 'page', 'sort'
    ]

    def to_dict(self, **kwargs) -> Dict[str, Any]:
        data = {key: value for (key, value) in vars(self).items() if key in SessionBodyEvent.JSON_FIELDS}
        data = {'constructor': self.__class__.__name__, **data, **kwargs}
        return data

    def to_json(self, **kwargs) -> str:
        data = self.to_dict(kwargs)
        return json.dumps(data, ensure_ascii=False)


class UserActionEvent(SessionBodyEvent):
    def __init__(self, time: int):
        super().__init__(time)
        self.coeffs = copy.deepcopy(params)

    def Update(self,prevstate):
        retval = super().Update(prevstate)
        retval["actioncount"] += 1
        if retval["actioncount"] > 1: #lastactioneventtime is not None
            delta_time = self.time - retval["lastactioneventtime"]
            GetCoefficients(self.coeffs, params, delta_time)
            retval["clickrate"] = delta_time
            UpdateAffinity(retval, self.coeffs, "actionaffinity", self.classindex())
            UpdateAffinity(retval, self.coeffs, "timeaffinity", retval["lastactioneventindex"])
            UpdateAttribute(retval, self.coeffs, "actionseparation", delta_time)
            #frustration: clickrates
            if retval["actioncount"] == 2: #initialize clickrates
                UpdateClickrates(retval, self.time, params["clickrate"], initialize=True)
            else: #actioncount >= 3
                UpdateClickrates(retval, self.time, params["clickrate"], initialize=False)
        else: #first action event
            GetCoefficients(self.coeffs, params, 0) #time dependent affinity parameter stays 0.0
            UpdateAffinity(retval, self.coeffs, "actionaffinity", self.classindex())
            # actionaffinity
            arr = retval["actionaffinity"][0]
            for act in range(classcount):
                arr[act] *= 0.0
            arr[self.classindex()] += 1.0
            # actiondifference
            arr = retval["actiondifference"][0]
            for act in range(classcount):
                arr[act] *= 0.0
            arr[self.classindex()] += 1.0
        retval["lastactioneventtime"] = self.time
        retval["lastactioneventindex"] = self.classindex()
        # retval["lastactioneventclass"] = self.eventclass
        if retval["highwatermark"] < 1:
            retval["highwatermark"] = 1
        return retval

class CartModifyEvent(UserActionEvent):
    def __init__(self, time: int, delta_count: int, delta_total):
        super().__init__(time)
        self.delta_count = delta_count
        self.delta_total = delta_total

    cindex = nextclassindex()
    classnames[cindex] = "CartModifyEvent"
    
    def Update(self,prevstate):
        retval = super().Update(prevstate)
        retval["carttotal"] += self.delta_total
        retval["cartcount"] += self.delta_count
        retval["cartdeltatotal"] = self.delta_total
        retval["cartdeltacount"] = self.delta_count
        retval["sessionstatus"] = "CartModified"
        UpdateAttribute(retval, self.coeffs, "carttotaltrend", self.delta_total)
        UpdateAttribute(retval, self.coeffs, "cartcounttrend", self.delta_count)
        if self.delta_count != 0:
            avgprice = self.delta_total/self.delta_count
            retval["cartmodification"] = self.delta_total/self.delta_count
            UpdateAttribute(retval, self.coeffs, "avgpricemanipulation", avgprice)
        return retval

class WishListModifyEvent(UserActionEvent):

    cindex = nextclassindex()
    classnames[cindex] = "WishListModifyEvent"

class RegistrationEvent(UserActionEvent):

    cindex = nextclassindex()
    classnames[cindex] = "RegistrationEvent"

class CouponAcceptedEvent(UserActionEvent):
    def __init__(self, time: int, event_label: str):
        super().__init__(time)
        self.event_label = event_label

    cindex = nextclassindex()
    classnames[cindex] = "CouponAcceptedEvent"

    def Update(self,prevstate):
        retval = super().Update(prevstate)
        retval["couponstatus"] = 2
        return retval

    def skip_update(self) -> bool:
        return True

class BrowsingEvent(UserActionEvent):
    def __init__(self, time: int, referrer: int, tabcount: int, tabtype: int, navigation: int, redirects: int, title: str, utm_source: str, utm_medium: str):
        super().__init__(time)
        self.referrer = referrer
        self.tabcount = tabcount
        self.tabtype = tabtype
        self.navigation = navigation
        self.redirects = redirects
        self.title = title
        self.utm_source = utm_source
        self.utm_medium = utm_medium

    cindex = nextclassindex()
    classnames[cindex] = "BrowsingEvent"

    def Update(self,prevstate):
        retval = super().Update(prevstate)
        UpdateAttribute(retval, self.coeffs, "tabcounttrend", self.tabcount)
        UpdateAttribute(retval, self.coeffs, "tabtypetrend", self.tabtype)
        UpdateAttribute(retval, self.coeffs, "redirectstrend", self.redirects)
        UpdateAttribute(retval, self.coeffs, "navigationtrend", self.navigation)
        UpdateAttribute(retval, self.coeffs, "referrertrend", self.referrer)
        return retval

class MainPageBrowsingEvent(BrowsingEvent):

    cindex = nextclassindex()
    classnames[cindex] = "MainPageBrowsingEvent"

class ProductPageBrowsingEvent(BrowsingEvent):
    def __init__(self, time: int, category_id: int, price: int, referrer: int, tabcount: int, tabtype: int, navigation: int, redirects: int, title: str, utm_source: str, utm_medium: str, product_id: Any):
        super().__init__(time,referrer,tabcount,tabtype,navigation,redirects,title,utm_source,utm_medium)
        self.product_id = product_id
        self.category_id = category_id
        self.price = price if price else 0

    cindex = nextclassindex()
    classnames[cindex] = "ProductPageBrowsingEvent"

    def Update(self,prevstate):
        retval = super().Update(prevstate)
        retval["lastcategory"] = self.category_id
        category = self.category_id
        LogCategory(retval,self.coeffs,category)
        retval["lastprice"] = self.price
        UpdateAttribute(retval, self.coeffs, "lastpriceviewedtrend", self.price)
        retval["producteverviewed"] = 1
        retval["product_ids"].append(self.product_id)
        retval["autocorr"] = CalculateAutocorrelation(retval["product_ids"])
        retval["u_product"] = CalculateUnalikeability(retval["product_ids"])
        return retval

class CartBrowsingEvent(BrowsingEvent):

    cindex = nextclassindex()
    classnames[cindex] = "CartBrowsingEvent"

class WishListBrowsingEvent(BrowsingEvent):

    cindex = nextclassindex()
    classnames[cindex] = "WishListBrowsingEvent"

class RegistrationPageBrowsingEvent(BrowsingEvent):

    cindex = nextclassindex()
    classnames[cindex] = "RegistrationPageBrowsingEvent"

class SearchResultsBrowsingEvent(BrowsingEvent):
    def __init__(self, time: int, referrer: int, tabcount: int ,tabtype: int, navigation: int, redirects: int, title: str, utm_source: str, utm_medium: str, page: int, sort: int):
        super().__init__(time,referrer,tabcount,tabtype,navigation,redirects,title,utm_source,utm_medium)
        self.page = page
        self.sort = sort

    cindex = nextclassindex()
    classnames[cindex] = "SearchResultsBrowsingEvent"
    
    def Update(self,prevstate):
        retval = super().Update(prevstate)
        UpdateAttribute(retval, self.coeffs, "sorttrend", self.sort)
        UpdateAttribute(retval, self.coeffs, "pagetrend", self.page)
        return retval

class CategoryPageBrowsingEvent(BrowsingEvent):
    def __init__(self, time: int, category_id: int, referrer: int, tabcount: int, tabtype: int, navigation: int, redirects: int, title: str, utm_source: str, utm_medium: str, page: int, sort: int):
        super().__init__(time,referrer,tabcount,tabtype,navigation,redirects,title,utm_source,utm_medium)
        self.category_id = category_id
        self.page = page
        self.sort = sort

    cindex = nextclassindex()
    classnames[cindex] = "CategoryPageBrowsingEvent"

    def Update(self,prevstate):
        retval = super().Update(prevstate)
        retval["lastcategory"] = self.category_id
        category = self.category_id
        LogCategory(retval,self.coeffs,category)
        UpdateAttribute(retval, self.coeffs, "sorttrend", self.sort)
        UpdateAttribute(retval, self.coeffs, "pagetrend", self.page)
        return retval
    
class PredefinedFilterBrowsingEvent(BrowsingEvent):
    def __init__(self, time: int, category_id: int, referrer: int, tabcount: int, tabtype: int, navigation: int, redirects: int, title: str, utm_source: str, utm_medium: str, page: int, sort: int):
        super().__init__(time,referrer,tabcount,tabtype,navigation,redirects,title,utm_source,utm_medium)
        self.category_id = category_id
        self.page = page
        self.sort = sort

    cindex = nextclassindex()
    classnames[cindex] = "PredefinedFilterBrowsingEvent"

    def Update(self,prevstate):
        retval = super().Update(prevstate)
        retval["lastcategory"] = self.category_id
        category = self.category_id
        LogCategory(retval,self.coeffs,category)
        UpdateAttribute(retval, self.coeffs, "sorttrend", self.sort)
        UpdateAttribute(retval, self.coeffs, "pagetrend", self.page)
        return retval
    
class InformationPageBrowsingEvent(BrowsingEvent):

    cindex = nextclassindex()
    classnames[cindex] = "InformationPageBrowsingEvent"
    
class AccountPageBrowsingEvent(BrowsingEvent):

    cindex = nextclassindex()
    classnames[cindex] = "AccountPageBrowsingEvent"

class ShopListBrowsingEvent(BrowsingEvent):

    cindex = nextclassindex()
    classnames[cindex] = "ShopListBrowsingEvent"

class BoardGamesUpdateEvent(BrowsingEvent):

    cindex = nextclassindex()
    classnames[cindex] = "BoardGamesUpdateEvent"

class CheckoutPageBrowsingEvent(BrowsingEvent):

    def is_closing(self):
        return True

class CustomerDataEntryBrowsingEvent(CheckoutPageBrowsingEvent):

    def Update(self,prevstate):
        retval = super().Update(prevstate)
        if retval["highwatermark"] < 2:
            retval["highwatermark"] = 2
        return retval

class ShippingMethodBrowsingEvent(CheckoutPageBrowsingEvent):

    def Update(self,prevstate):
        retval = super().Update(prevstate)
        if retval["highwatermark"] < 3:
            retval["highwatermark"] = 3
        return retval

class PaymentMethodBrowsingEvent(CheckoutPageBrowsingEvent):

    def Update(self,prevstate):
        retval = super().Update(prevstate)
        if retval["highwatermark"] < 4:
            retval["highwatermark"] = 4
        return retval

class ConfirmationPageBrowsingEvent(CheckoutPageBrowsingEvent):

    def Update(self,prevstate):
        retval = super().Update(prevstate)
        if retval["highwatermark"] < 5:
            retval["highwatermark"] = 5
        return retval

class CheckoutSuccessPageBrowsingEvent(CheckoutPageBrowsingEvent):

    def Update(self,prevstate):
        retval = super().Update(prevstate)
        if retval["highwatermark"] < 6:
            retval["highwatermark"] = 6
        return retval

    def is_success(self) -> bool:
        return True

class SystemEvent(SessionBodyEvent):

    def skip_update(self) -> bool:
        return True

class CouponOfferedEvent(SystemEvent):
    def __init__(self, time: int, event_label: str):
        super().__init__(time)
        self.event_label = event_label

    cindex = nextclassindex()
    classnames[cindex] = "CouponOfferedEvent"

    def Update(self,prevstate):
        retval = super().Update(prevstate)
        retval["couponstatus"] = 1 if retval["couponstatus"] == 0 else retval["couponstatus"]
        return retval

# globals

device_dict = {"mobile":0,"tablet":1,"desktop":2}
os_dict = {"ms":0,"apple":1,"linux":2}
lang_dict = {"hu":0}
sessionstatus_dict = {"Browsing":0,"CartModified":1}

def Update(prevstate,bodyevent,newparams=None):
    global params
    if newparams:
        for param in newparams:
            if param in params:
                params[param] = newparams[param]
    if prevstate["sessionstatus"] == "Bot":
        return prevstate
    #if restart:
    #    return NewState(prevstate["admin_origin"], prevstate["admin_useragent"], prevstate["admin_lang"],
    #                         bodyevent, newparams)
    return bodyevent.Update(prevstate)

def NewState(origin_string, user_agent_string, lang_string, firstbodyevent, newparams=None):
    
    origin_cls = parser_api.parse_origin(origin_string)
    if origin_cls in origin_dict:
        origin = origin_dict[origin_cls]
    elif origin_cls in ["fblink","ggbot"]:
        return {"sessionstatus":"Bot"}
    else:
        origin = len(origin_dict)

    device_cls,os_cls = parser_api.parse_user_agent(user_agent_string)
    device = device_dict.get(device_cls,len(device_dict))
    os = os_dict.get(os_cls,len(os_dict))

    lang_cls = parser_api.parse_lang(lang_string)
    lang = lang_dict.get(lang_cls,len(lang_dict))

    original_state = {
        "admin_origin": origin_string,
        "admin_user_agent": user_agent_string,
        "admin_region": lang_string,
        "sessionstart": firstbodyevent.time,
        "origin": origin,
        "device": device,
        "os": os,
        "lang":lang,
        "actioncount": 0,
        "lastbodyeventtime": None,
        "lastactioneventtime": None,
        "lastactioneventindex": None,
        "clickrate_avg": 0.0,
        "clickrate_squares": 0.0,
        "clickrate_var": 0.0,
        "z_score": 0.0,
        "sessionstatus": "Browsing",
        "clickrate": 0.0,
        "actionseparation": [0.0] * len(params["actionseparation"]),
        "actionaffinity": [[1 / classcount] * classcount for _ in range(len(params["actionaffinity"]))],
        "actiondifference": [[0.0] * classcount for _ in range(len(params["actionaffinity"]))],
        "timeaffinity": [[1 / classcount] * classcount for _ in range(len(params["timeaffinity"]))],
        "lastcategory": None,
        "categoryaffinity": [[1/MAX_CATEGORY] * MAX_CATEGORY for _ in range(len(params["categoryaffinity"]))],
        "carttotal":0.0,
        "cartcount":0,
        "cartdeltatotal": 0.0,
        "cartdeltacount": 0,
        "carttotaltrend": [0.0] * len(params["carttotaltrend"]),
        "cartcounttrend": [0.0] * len(params["cartcounttrend"]),
        "cartmodification": 0.0,
        "avgpricemanipulation": [0.0] * len(params["avgpricemanipulation"]),
        "couponstatus": 0,
        "lastprice": 0.0,
        "lastpriceviewedtrend": [0.0] * len(params["lastpriceviewedtrend"]),
        "tabcounttrend" : [0.0] * len(params["tabcounttrend"]),
        #"tabcountdeltatrend": [0.0] * len(params["tabcounttrend"]),
        "redirectstrend" : [0.0] * len(params["redirectstrend"]),
        "tabtypetrend" : [0.0] * len(params["tabtypetrend"]),
        "navigationtrend": [0.0] * len(params["navigationtrend"]),
        "referrertrend": [0.0] * len(params["referrertrend"]),
        "sorttrend": [0.0] * len(params["sorttrend"]),
        "pagetrend": [0.0] * len(params["pagetrend"]),
        "producteverviewed": 0,
        "highwatermark": 0,
        "product_ids": [],
        "u_product": -1,
        "autocorr": 0
    }

    return Update(original_state,firstbodyevent,newparams)

def RowOfState(state):
    row ={k:state[k] for k in ["actioncount","origin","device","os","lang",
                               "carttotal","cartcount","cartdeltatotal","cartdeltacount",
                               "producteverviewed","couponstatus",
                               #"clickrate_squares",
                               "clickrate_avg","clickrate_var","z_score", "u_product", "autocorr"]}                  
    row["sessionage"] = state["lastbodyeventtime"] - state["sessionstart"]
    lastbodyeventtime = datetime.datetime.fromtimestamp(state["lastbodyeventtime"])
    row["hourofday"] = lastbodyeventtime.hour
    row["dayofweek"] = lastbodyeventtime.weekday()
    row["dayofmonth"] = lastbodyeventtime.day
    row["cartaverageprice"] = state["carttotal"]/state["cartcount"] if state["cartcount"] != 0 else 0.0
    # row["highwatermark"] = state["highwatermark"]
    
    arr = state["actionseparation"]
    for i in range(len(arr)):
        row["actionseparation_" + str(i)] = arr[i]

    arr = state["actionaffinity"]
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            row["actionaffinity_" + str(i) + "_" + classnames[j]] = arr[i][j]

    arr = state["actiondifference"]
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            row["actiondifference_" + str(i) + "_" + classnames[j]] = arr[i][j]

    arr = state["timeaffinity"]
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            row["timeaffinity_" + str(i) + "_" + classnames[j]] = arr[i][j]

    arr = state["categoryaffinity"]
    for i in range(len(arr)):
        for j in range(len(arr[0])):
            row["categoryaffinity_" + str(i) + "_" + str(j)] = arr[i][j]
            
    arr = state["carttotaltrend"]
    for i in range(len(arr)):
        row["carttotaltrend_" + str(i)] = arr[i]

    arr = state["cartcounttrend"]
    for i in range(len(arr)):
        row["cartcounttrend_" + str(i)] = arr[i]

    arr = state["avgpricemanipulation"]
    for i in range(len(arr)):
        row["avgpricemanipulation_" + str(i)] = arr[i]

    arr = state["lastpriceviewedtrend"]
    for i in range(len(arr)):
        row["lastpriceviewedtrend_" + str(i)] = arr[i]

    arr = state["tabcounttrend"]
    for i in range(len(arr)):
        row["tabcounttrend_" + str(i)] = arr[i]

    # arr = state["tabcountdeltatrend"]
    # for i in range(len(arr)):
    #     row["tabcountdeltatrend_" + str(i)] = arr[i]

    arr = state["redirectstrend"]
    for i in range(len(arr)):
        row["redirectstrend_" + str(i)] = arr[i]

    arr = state["tabtypetrend"]
    for i in range(len(arr)):
        row["tabtypetrend_" + str(i)] = arr[i]

    arr = state["navigationtrend"]
    for i in range(len(arr)):
        row["navigationtrend_" + str(i)] = arr[i]

    arr = state["referrertrend"]
    for i in range(len(arr)):
        row["referrertrend_" + str(i)] = arr[i]
        
    arr = state["pagetrend"]
    for i in range(len(arr)):
        row["pagetrend_" + str(i)] = arr[i]

    arr = state["sorttrend"]
    for i in range(len(arr)):
        row["sorttrend_" + str(i)] = arr[i]
        
    return row

# Cart abandon prediction


def PredictionReadyQ(state) -> bool:
    return (state["sessionstatus"] == "CartModified" and state["actioncount"] >= 5)

def is_browsing(state) -> bool:
    return state.get('sessionstatus') == 'Browsing'

def WillAbandonQ(state,modelpath='') -> Union[None, Tuple[int, float]]:
    global threshold,eps
    if not PredictionReadyQ(state):
        return None
    model = xgboost.XGBClassifier()
    model.load_model(modelpath + FILE_NAME)
    row = RowOfState(state)
    line = np.array( list(row.values()) ).reshape( (1,len(row)) )
    # you should cast np.float32 to float beacuse JSON can't serialize types of np
    score = float(model.predict_proba(line)[0][1])
    vote = ABANDONER if score>SCORE_THRESHOLD else BUYER
    return (vote,score)

# Frustration point

def FrustrationReadyQ(state):
    return (state["sessionstatus"] == "Browsing" and state["actioncount"] >= 5 and state["clickrate_var"] > 0.0)

def WasFrustratedQ(state) -> Union[None, Tuple[bool, float]]:
    ''' If got frustrated in the previous state'''
    if not FrustrationReadyQ(state):
        return None
    return (abs(state["z_score"]) > FRUSTRATION_TOLERANCE, state["z_score"])

def FrustrationUpperLimit(state):
    ''' Upper limit of being frustrated: returns a timestamp after which visitor considered frustrated'''
    timestamp_limit = state["clickrate_avg"] #+ state["lastactioneventtime"]
    timestamp_limit += state["clickrate_var"]**(1/2) * FRUSTRATION_TOLERANCE
    return int(timestamp_limit) + 1

def GetFrustrationPoint(state):
    '''
    If not Ready: return None
    If was FrustratedQ (got frustrated before = clicked quicker then tolerated): return True
    If not: return upper limit in seconds (timestamp): after this time we consider it to be frustrated as well (clicked slower then expected)
    '''
    if not FrustrationReadyQ(state):
        return None
    if WasFrustratedQ(state): #got frustrated before this event
        return True
    else: #return upper limit of frustration
        return FrustrationUpperLimit(state)

def WillLeaveQ(state,timestamp):
    ''' Will leave at time 'timestamp'? '''
    if not FrustrationReadyQ(state):
        return None
    delta_time = timestamp - state["lastactioneventtime"]
    z_score = abs(delta_time - state["clickrate_avg"])
    z_score *= state["clickrate_var"]**(-1/2)
    return z_score > FRUSTRATION_TOLERANCE

def AorB(uuid: str, *groups: int) -> Union[int,None]:
    S = sum(groups)
    residue = int(uuid[28:],base=16) % S
    for i in range(len(groups)):
        if residue < sum(groups[:i+1]):
            return i
    else:
        return None
