import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json

def parse_political_parties():
    """
    Парсит список политических партий с сайта Минюста
    """
    url = "https://minjust.gov.ru/ru/pages/politicheskie-partii/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Простая обработка SSL - сразу без проверки
    response = requests.get(url, headers=headers, verify=False)
    
    # Если статус не 200 - возвращаем пустой список
    if response.status_code != 200:
        print(f"❌ Ошибка загрузки: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.content, 'html.parser')
    print("✅ Страница загружена")
    
    # Ищем список партий
    parties_list = soup.find('ol')
    if not parties_list:
        print("❌ Не найден список партий")
        return []
    
    # Извлекаем партии
    party_items = parties_list.find_all('li')
    print(f"📋 Найдено партий: {len(party_items)}")
    
    parties_data = []
    
    for item in party_items:
        link = item.find('a', href=True)
        
        # Если есть ссылка - обрабатываем
        if link:
            name = link.get_text(strip=True)
            doc_url = link['href']
            
            # Исправляем ссылку
            if doc_url.startswith('/'):
                doc_url = urljoin('https://minjust.gov.ru', doc_url)
            doc_url = doc_url.replace('http://', 'https://')
            
            parties_data.append({
                "name": name,
                "doc_url": doc_url
            })
            
            print(f"✅ {name[:40]}...")
            print(f"   🔗 {doc_url}")
    
    return parties_data

def main():
    print("🔄 Запускаем парсер...")
    
    # Отключаем SSL предупреждения один раз
    import urllib3
    urllib3.disable_warnings()
    
    parties = parse_political_parties()
    
    print(f"\n🎉 Найдено партий: {len(parties)}")
    
    # Сохраняем результат
    if parties:
        with open('parties.json', 'w', encoding='utf-8') as f:
            json.dump(parties, f, ensure_ascii=False, indent=2)
        print("💾 Данные сохранены в parties.json")

if __name__ == "__main__":
    main()