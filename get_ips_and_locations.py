import pandas as pd
import subprocess
import requests
# from bs4 import BeautifulSoup
# import urllib.request
from urllib.parse import urlparse
import re
from collections import Counter

def Get_urls_website(website_url):
    # html_page = urllib.request.urlopen(website_url)
    # soup = BeautifulSoup(html_page, "html.parser")
    # url_list = []
    # for link in soup.findAll('a', attrs={'href': re.compile("^https://")}):
    #     url = link.get('href')
    #     url_list.append((url.replace('https://', '')).rstrip('/'))
    # print(url_list)

    # fetching links using linkchecker
    command = "linkchecker {} --file-output=csv --verbose --check-extern -r 1".format(website_url)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    out, err = process.communicate()
    url_list = re.findall(r'Real URL   (.*?)\n', out.decode('utf-8'))

    domains = set()
    for link in url_list:
        domains.add(urlparse(link).netloc)
    return domains

def Get_IP(domain_list):
    IP_list = []

    for site in domain_list:
        cmd = 'ping -c1 {0} | grep PING | cut -d"(" -f2 | cut -d ")" -f1'.format(site)
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
        IP_list.append((output.decode('ascii')).rstrip())

    return IP_list

def Get_location(IP_list):
    Location_list = []

    for ip in IP_list:
        r = requests.get(url = "http://api.db-ip.com/v2/free/{}".format(ip))
        data = r.json()
        if 'countryName' in data:
            Location_list.append(data['countryName'])
        else:
            Location_list.append("NA")

    return Location_list


def get_resources_and_locations(websites_list):
    domains = []

    for website in websites_list:
        domains_list = Get_urls_website(website)
        domains.extend(domains_list)

    IP_list = Get_IP(domains)
    Location_list = Get_location(IP_list)
    return domains, IP_list, Location_list

def update_xls_with_IP(input_file, output_file):    
    df = pd.read_excel(input_file)
    websites_list = df['Websites'].tolist()
    IP_list = Get_IP(websites_list)
    df['IP (VPN)'] = IP_list  # comment out this line by connecting to VPN to get IP with VPN on
    # df['IP (No VPN)'] = IP_list # comment out this line by disabling to VPN to get IP with VPN off

    # For IPs with VPN on
    ip_col = "IP (VPN)"
    location = "IP (VPN) Location"

    # For IPs with VPN off
    # ip_col = "IP (No VPN)"
    # location = "IP (No VPN) Location"

    IP_list = df[ip_col].tolist()
    Location_list = Get_location(IP_list)
    df[location] = Location_list
    df.to_excel(output_file, index=False)

# , "https://www.google.com.br/", "https://www.tiktok.com/", "https://www.mercadolivre.com.br/", "https://www.magazineluiza.com.br/", "https://www.olx.com.br/", "https://www.noticias.uol.com.br/", "https://www.r7.com/"

def get_domain_counter(websites_list):
    domains, IP_list, Location_list = get_resources_and_locations(websites_list)
    print(domains)
    print(IP_list)
    print(Location_list)
    r = requests.get("https://api.ivpn.net/v4/geo-lookup")
    country = (r.json())['country']
    print(country)
    domain_counter = []
    for idx, location in enumerate(Location_list):
        if location == country:
            domain_counter.append(domains[idx])
    return Counter(domain_counter)

# websites_list = ["https://www.google.com/", "https://www.facebook.com/", "https://www.youtube.com/", "https://www.instagram.com/", "https://www.whatsapp.com/", "https://www.google.com.br/", "https://www.tiktok.com/", "https://www.r7.com/" ]
# result_domain_dict = get_domain_counter(websites_list)
# print(result_domain_dict)

update_xls_with_IP('In_Spain_top_websites.xlsx', 'Result_Spain_top_websites.xlsx')
