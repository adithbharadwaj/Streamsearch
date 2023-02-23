REGION_VPN_MAP = {
    'US': [["ExpressVPN", "https://expressvpn.com"], ["NordVPN", "https://nordvpn.com"]],
    'GB': [["ExpressVPN", "https://expressvpn.com"], ["NordVPN", "https://nordvpn.com"]],
    'IN': [["ExpressVPN", "https://expressvpn.com"], ["NordVPN", "https://nordvpn.com"]]
}

def region_vpn_map(locale_code):
    if locale_code not in REGION_VPN_MAP:
        return []
    else:
        return REGION_VPN_MAP[locale_code]
