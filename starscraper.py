import requests
from lxml import html
from bs4 import BeautifulSoup  

def get_actor_rank():
     total_info = ''
     for i in range(1,11):
          url = "https://www.imdb.com/list/ls058011111/?sort=list_order,asc&mode=detail&page=%d" %(i) 
          page = requests.Session().get(url)
          tree = html.fromstring(page.text)
          
          rank_list = tree.xpath('//h3[@class="lister-item-header"]//span/text()')
          name_list = tree.xpath('//h3[@class="lister-item-header"]//a/text()')
          id_list = [] 
          soup = BeautifulSoup(page.text, "html5lib")
          herfs = soup.select('.lister-item-header a')
          for link in herfs:
               id_list.append(link.attrs["href"][6:])
          
          info = ""
          for num in range(100):
               info += id_list[num] + "," + rank_list[num][0:-2] + "," + name_list[num][1:-1] + '\n'
          total_info += info
     return total_info

def main():
     info = get_actor_rank()
     f = open("1000_actor_rank.csv", "w")
     f.write(info)
     f.close()
 
if __name__ == '__main__':
	main()
