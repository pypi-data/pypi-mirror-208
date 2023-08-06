from segmenthee.cart_api import *
from datetime import datetime as dt
import json
import re
from urllib.parse import urlparse, parse_qs, unquote


CATEGORY_MAP: Dict[str, int] = {
    '/kerekparok-138': 0,
    '/alkatreszek-139': 1,
    '/kiegeszitok-felszerelesek-140': 2,
    '/karbantartas-141': 3,
    '/ruhazat-142': 4,
    '/szerviz-143': 5,
    '/markak-144': 0,
    '/legujabb-termekek-145': 1
}

CATEGORY_FILTER: Dict[int, int] = {}

PREDEFINED_FILTER: Dict[str, int] = {}


INFO_PAGES: List[str] = [
    '/contact', 
    '/fizetes-szallitas-34',
    '/segitseg-35', 
    '/gyakran-ismetelt-kerdesek-36', 
    '/garancia-37', 
    '/30-napos-termek-visszakuldes-38', 
    '/sitemap',
    '/adatvedelmi-nyilatkozat-44',
    '/vasarlasi-feltetelek-5',
    '/adatvedelem-45',
    '/rolunk-51',
    'information/contact',
    'information/sitemap'
]


def get_event(item: Dict) -> SessionBodyEvent:
    time: int = item.get('_ts', int(dt.now().timestamp()))
    browsing_data = {'time': time,
                     'referrer': get_referrer(item.get(Config.CD_REFERRER)),
                     'tabcount': int(item[Config.CD_TABCOUNT]),
                     'tabtype': get_tabtype(item[Config.CD_TABTYPE]),
                     'navigation': get_navigation(item[Config.CD_NAVIGATION]),
                     'redirects': int(item[Config.CD_REDIRECTS]),
                     'title': item.get('dt'),
                     'utm_source': get_utm_source(item),
                     'utm_medium': item.get('utm_medium', '')}

    if item.get('t') == 'pageview':
        parts = urlparse(get_fixed_url(item.get('dl')))
        query: Dict[str, str] = parse_query(parts.query)
        if parts.path == '/':
            event = MainPageBrowsingEvent(**browsing_data)
            return event
        if item.get('pa') == 'detail':
            browsing_data['product_id'] = item.get('pr1id')
            browsing_data['category_id'] = -1
            for path, cat in CATEGORY_MAP.items():
                if parts.path.startswith(path):
                    browsing_data['category_id'] = cat
                    break

            pr1pr = item.get('pr1pr', 0)
            browsing_data['price'] = int(pr1pr) if pr1pr != 'NaN' else 0
            event = ProductPageBrowsingEvent(**browsing_data)
            return event
        if parts.path == '/szakuzletunk':
            event = ShopListBrowsingEvent(**browsing_data)
            return event
        if parts.path == '/reflexshop-tarsasjatekok':
            event = BoardGamesUpdateEvent(**browsing_data)
            return event
        if parts.path == '/cart':
            event = CartBrowsingEvent(**browsing_data)
            return event
        if parts.path == '/checkout':
            if parts.fragment == '/customerdata/':
                event = CustomerDataEntryBrowsingEvent(**browsing_data)
                return event
            if parts.fragment == '/shippingmethod/':
                event = ShippingMethodBrowsingEvent(**browsing_data)
                return event
            if parts.fragment == '/paymentmethod/':
                event = PaymentMethodBrowsingEvent(**browsing_data)
                return event
            if parts.fragment == '/confirmation/':
                event = ConfirmationPageBrowsingEvent(**browsing_data)
                return event

            event = CheckoutPageBrowsingEvent(**browsing_data)
            return event

        if parts.path == '/index.php' and query.get('route') == 'checkout/success':
            event = CheckoutSuccessPageBrowsingEvent(**browsing_data)
            return event

        if parts.path == '/index.php' and query.get('route') == 'wishlist/wishlist':
            event = WishListBrowsingEvent(**browsing_data)
            return event

        if parts.path == '/index.php' and query.get('route', '').startswith('account/'):
            event = AccountPageBrowsingEvent(**browsing_data)
            return event

        # CategoryPage
        for path, category in CATEGORY_MAP.items():
            if parts.path == path or parts.path.find(path) > -1:
                kwargs = {**browsing_data, 'category_id': category, **get_pagination(query)}
                event = CategoryPageBrowsingEvent(**kwargs)
                return event

        # CategoryPage
        if parts.path == '/index.php' and query.get('route') == 'product/list':
            if query.get('keyword') is None and (cat_id := query.get('category_id')):
                category = CATEGORY_FILTER.get(int(cat_id), -1)
                kwargs = {**browsing_data, 'category_id': category, **get_pagination(query)}
                event = CategoryPageBrowsingEvent(**kwargs)
                return event

        # PredefinedFilter -> CategoryPage -> SearchResults
        if parts.path == '/index.php' and query.get('route') == 'filter':
            category = PREDEFINED_FILTER.get(query.get('filter'), -2)
            if category > -2:
                kwargs = {**browsing_data, 'category_id': category, **get_pagination(query)}
                event = PredefinedFilterBrowsingEvent(**kwargs)
                return event

            if query.get('filter', '').startswith('category|') and query.get('keyword') is None:
                numbers = re.findall(r'\d+', query.get('filter'))
                category = CATEGORY_FILTER.get(int(numbers[0]), -2) if numbers else -2
                if category > -2:
                    kwargs = {**browsing_data, 'category_id': category, **get_pagination(query)}
                    event = CategoryPageBrowsingEvent(**kwargs)
                    return event

            kwargs = {**browsing_data, **get_pagination(query)}
            event = SearchResultsBrowsingEvent(**kwargs)
            return event

        # SearchResults
        if parts.path == '/kereses' or query.get('route') == 'product/list':
            kwargs = {**browsing_data, **get_pagination(query)}
            event = SearchResultsBrowsingEvent(**kwargs)
            return event

        # InformationPage
        if parts.path in INFO_PAGES or query.get('route') in INFO_PAGES:
            event = InformationPageBrowsingEvent(**browsing_data)
            return event

        event = BrowsingEvent(**browsing_data)
        return event

    if item.get('t') == 'event':
        if item.get('ec') == 'Értesítés kérése' and item.get('ea') == 'Értesítés kérése sikeres':
            event = RegistrationEvent(time)
            return event
        if item.get('ec') == 'e-cart' and item.get('ea') == 'update':
            data = json.loads(item.get('el'))
            delta_count = data.get('itemCount')
            delta_total = round(data.get('total'), 2)
            event = CartModifyEvent(time, delta_count, delta_total)
            return event
        if item.get('ec') == 'OptiMonk':
            if item.get('ea') == 'shown':
                event = CouponOfferedEvent(time, item.get('el'))
                return event
            if item.get('ea') == 'filled':
                event = CouponAcceptedEvent(time, item.get('el'))
                return event

    event = SystemEvent(time)
    return event


def get_fixed_url(url: str) -> str:
    p1 = url.find('?')
    p2 = url.find('&')
    if p1 == -1 and p2 > -1:
        return url[:p2] + '?' + url[p2+1:]
    return url[:p2] + url[p1:] + url[p2:p1] if -1 < p2 < p1 else url


def parse_query(query: str) -> Dict[str, str]:
    return {} if query.strip() == '' else {k: v[0] for k, v in parse_qs(unquote(query)).items()}


def get_pagination(query: Dict) -> Dict:
    pagination = {"page": get_page(query.get('page', '1'))}
    if 'sort_order' in query.keys():
        pagination["sort"] = get_sort(query.get('sort_order'))
    elif 'sort' in query.keys():
        pagination["sort"] = get_sort(query.get('sort') + '_' + query.get('order', 'asc').lower())
    else:
        pagination["sort"] = get_sort('default')
    return pagination
