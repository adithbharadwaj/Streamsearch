REGION_VPN_MAP = {
    'US': [["ExpressVPN", "https://expressvpn.com"], ["NordVPN", "https://nordvpn.com"]],
    'UK': [["ExpressVPN", "https://expressvpn.com"], ["NordVPN", "https://nordvpn.com"]],
    'IN': [["ExpressVPN", "https://expressvpn.com"], ["NordVPN", "https://nordvpn.com"]]
}

def region_vpn_map(locale_code):
    return REGION_VPN_MAP[locale_code]
