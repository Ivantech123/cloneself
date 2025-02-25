import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from datetime import datetime
import time
import json

def save_results(posts):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'zen_posts_{timestamp}.txt'
    
    with open(filename, 'w', encoding='utf-8') as f:
        for post in posts:
            f.write(f"Заголовок: {post['title']}\n")
            f.write(f"Дата: {post['date']}\n")
            f.write(f"Просмотры: {post['views']}\n")
            f.write(f"Текст: {post['text']}\n")
            f.write("-" * 50 + "\n")
    
    print(f"Результаты сохранены в файл: {filename}")

def parse_zen_channel(channel_url):
    print("Запускаем браузер...")
    options = uc.ChromeOptions()
    options.add_argument('--headless')
    driver = uc.Chrome(options=options)
    
    try:
        print(f"Открываем канал: {channel_url}")
        driver.get(channel_url)
        
        # Ждем загрузки контента
        time.sleep(5)
        
        posts = []
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        print("Начинаем сбор постов...")
        
        # Прокручиваем страницу для загрузки всех постов
        scroll_attempts = 0
        max_scroll_attempts = 50  # Максимальное количество прокруток
        
        while scroll_attempts < max_scroll_attempts:
            # Прокрутка вниз
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Собираем посты
            articles = driver.find_elements(By.TAG_NAME, "article")
            
            for article in articles:
                try:
                    title = article.find_element(By.CSS_SELECTOR, "h2").text
                except:
                    try:
                        # Альтернативный поиск заголовка
                        title = article.find_element(By.CSS_SELECTOR, "[class*='title']").text
                    except:
                        title = "Без заголовка"
                
                try:
                    text = article.find_element(By.CSS_SELECTOR, "[class*='content']").text
                except:
                    text = "Текст не найден"
                
                try:
                    date = article.find_element(By.CSS_SELECTOR, "time").get_attribute("datetime")
                except:
                    try:
                        # Альтернативный поиск даты
                        date = article.find_element(By.CSS_SELECTOR, "[class*='date']").text
                    except:
                        date = "Дата не указана"
                
                try:
                    views = article.find_element(By.CSS_SELECTOR, "[class*='views']").text
                except:
                    views = "0"
                
                post_data = {
                    'title': title,
                    'text': text,
                    'date': date,
                    'views': views
                }
                
                if post_data not in posts:  # Избегаем дубликатов
                    posts.append(post_data)
                    print(f"Собрано постов: {len(posts)}")
            
            # Проверяем, достигли ли конца страницы
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
            last_height = new_height
            
            if scroll_attempts >= 3:  # Если высота не менялась 3 раза подряд, считаем что достигли конца
                break
        
        print(f"Парсинг завершен. Всего собрано постов: {len(posts)}")
        return posts
        
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        return []
        
    finally:
        driver.quit()

if __name__ == "__main__":
    channel_url = input("Введите URL канала на Дзен (например, https://dzen.ru/username): ")
    posts = parse_zen_channel(channel_url)
    if posts:
        save_results(posts)
