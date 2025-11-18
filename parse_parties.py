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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Пробуем сначала с проверкой SSL, если не работает - без проверки
        try:
            response = requests.get(url, headers=headers, verify=True)
        except requests.exceptions.SSLError:
            print("⚠️  SSL ошибка, пробуем без проверки сертификата...")
            response = requests.get(url, headers=headers, verify=False)
        
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        print("✅ Страница загружена")
        
        # Ищем нумерованный список с партиями
        parties_list = soup.find('ol')
        
        if not parties_list:
            print("❌ Не найден список партий")
            return []
        
        # Извлекаем все элементы списка
        party_items = parties_list.find_all('li')
        print(f"📋 Найдено партий: {len(party_items)}")
        
        parties_data = []
        
        for item in party_items:
            # Находим ссылку в элементе списка
            link = item.find('a', href=True)
            
            if link:
                # Извлекаем название партии (весь текст ссылки)
                name = link.get_text(strip=True)
                
                # Извлекаем URL
                doc_url = link['href']
                
                # Преобразуем относительные ссылки в абсолютные
                if doc_url.startswith('/'):
                    doc_url = urljoin('https://minjust.gov.ru', doc_url)
                
                # Исправляем протокол если нужно
                doc_url = doc_url.replace('http://', 'https://')
                
                parties_data.append({
                    "name": name,
                    "doc_url": doc_url
                })
                
                print(f"✅ Партия: {name[:50]}...")
                print(f"   📄 Документ: {doc_url}")
            else:
                # Если ссылки нет, добавляем партию без документа
                name = item.get_text(strip=True)
                parties_data.append({
                    "name": name,
                    "doc_url": None
                })
                print(f"⚠️  Партия без документа: {name[:50]}...")
        
        return parties_data
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def main():
    print("🔄 Запускаем парсер политических партий...")
    
    # Игнорируем предупреждения SSL
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    parties = parse_political_parties()
    
    print(f"\n🎉 Парсинг завершен!")
    print(f"📊 Всего обработано партий: {len(parties)}")
    
    # Сохраняем в JSON файл
    if parties:
        with open('parties.json', 'w', encoding='utf-8') as f:
            json.dump(parties, f, ensure_ascii=False, indent=2)
        print("💾 Данные сохранены в parties.json")
        
        # Показываем первые 3 партии для примера
        print("\n📋 Пример данных (первые 3 партии):")
        for i, party in enumerate(parties[:3]):
            print(f"{i+1}. {party['name']}")
            print(f"   🔗 {party['doc_url'] or 'Нет документа'}")
    else:
        print("❌ Не удалось получить данные")

if __name__ == "__main__":
    main()