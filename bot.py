import os
import random
import logging
from datetime import datetime
import asyncio
import schedule
import time
from dotenv import load_dotenv
from telegram import Bot, InputMediaPhoto
from telegram.constants import ParseMode
from telegram.request import HTTPXRequest
from tarot_data import TAROT_CARDS

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/tarot_bot/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Конфигурация бота
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

if not TOKEN:
    raise ValueError("❌ Не найден токен бота. Проверьте переменную TELEGRAM_BOT_TOKEN в файле .env")
if not CHANNEL_ID:
    raise ValueError("❌ Не найден ID канала. Проверьте переменную TELEGRAM_CHANNEL_ID в файле .env")

logger.info(f"✓ Токен бота: {TOKEN[:10]}...")
logger.info(f"✓ ID канала: {CHANNEL_ID}")

# Увеличиваем размер пула соединений
request = HTTPXRequest(
    http_version="1.1",
    connection_pool_size=100,
    read_timeout=30,
    write_timeout=30,
    connect_timeout=30,
    pool_timeout=30
)
bot = Bot(token=TOKEN, request=request)

def get_russian_month():
    """Возвращает название текущего месяца на русском языке"""
    months = {
        1: 'января',
        2: 'февраля',
        3: 'марта',
        4: 'апреля',
        5: 'мая',
        6: 'июня',
        7: 'июля',
        8: 'августа',
        9: 'сентября',
        10: 'октября',
        11: 'ноября',
        12: 'декабря'
    }
    return months[datetime.now().month]

def get_moon_phase():
    """Возвращает текущую фазу луны"""
    moon_phases = ['🌑 Новолуние', '🌒 Растущая луна', '🌓 Первая четверть', 
                  '🌔 Растущая луна', '🌕 Полнолуние', '🌖 Убывающая луна',
                  '🌗 Последняя четверть', '🌘 Убывающая луна']
    
    # Упрощенный расчет фазы луны
    current_date = datetime.now()
    days_since_new_moon = (current_date - datetime(2000, 1, 6)).days
    moon_age = days_since_new_moon % 29.53
    phase_index = int((moon_age / 29.53) * 8) % 8
    
    return moon_phases[phase_index]

async def get_tarot_image():
    """Получаем URL изображения для общей картинки Таро"""
    tarot_images = [
        "https://raw.githubusercontent.com/rws-cards-api/rws-cards-api/master/public/cards/back.jpg",
        "https://raw.githubusercontent.com/rws-cards-api/rws-cards-api/master/public/cards/background.jpg"
    ]
    return random.choice(tarot_images)

async def generate_daily_reading():
    """Генерируем ежедневное гадание на картах Таро"""
    # Выбираем три случайные карты
    cards = random.sample(list(TAROT_CARDS.items()), 3)
    
    # Создаем сообщение
    current_date = datetime.now()
    date_str = f"{current_date.day} {get_russian_month()} {current_date.year}"
    moon_phase = get_moon_phase()
    current_hour = current_date.hour
    
    # Определяем время дня
    if current_hour < 12:
        time_of_day = "🌅 Утреннее"
    elif current_hour < 18:
        time_of_day = "🌞 Дневное"
    else:
        time_of_day = "🌙 Вечернее"
    
    message = f"🔮 *{time_of_day} гадание на картах Таро* 🔮\n"
    message += f"📅 {date_str}\n"
    message += f"{moon_phase}\n\n"
    
    positions = ["Прошлое ⏮", "Настоящее ⏺", "Будущее ⏭"]
    
    # Формируем список изображений
    images = []
    
    # Добавляем общее изображение Таро
    tarot_image = await get_tarot_image()
    images.append(InputMediaPhoto(media=tarot_image, caption=message, parse_mode=ParseMode.MARKDOWN))
    
    # Добавляем информацию о картах
    for (card_name, card_info), position in zip(cards, positions):
        message += f"*{position}*: 🎴 _{card_name}_\n"
        message += f"📝 {card_info['meaning']}\n"
        message += f"⚡ Стихия: {card_info['element']}\n"
        message += f"🔢 Число: {card_info['number']}\n\n"
        
        # Добавляем изображение карты
        if 'image_url' in card_info:
            images.append(InputMediaPhoto(media=card_info['image_url']))
    
    message += "✨ *Совет дня*:\n"
    message += f"Обратите внимание на карту '{cards[1][0]}' в позиции настоящего - {cards[1][1]['meaning']}\n\n"
    
    message += "🌟 *Общее толкование расклада*:\n"
    message += f"Энергии прошлого ({cards[0][0]}) влияют на ваше настоящее ({cards[1][0]}), "
    message += f"направляя вас к будущему ({cards[2][0]}). "
    message += "Прислушайтесь к подсказкам карт и доверьтесь своей интуиции.\n\n"
    
    message += "#ТароНаДень #Духовность #Гадание #Таро"
    
    return message, images

async def post_reading():
    """Отправляем гадание в канал"""
    try:
        logger.info("🔄 Генерируем гадание...")
        message, images = await generate_daily_reading()
        logger.info("✓ Гадание сгенерировано")
        
        # Добавляем задержку между отправкой сообщений
        await asyncio.sleep(2)
        
        logger.info(f"🔄 Отправляем изображения в канал {CHANNEL_ID}...")
        try:
            # Отправляем изображения с первым изображением, содержащим текст сообщения
            await bot.send_media_group(
                chat_id=CHANNEL_ID,
                media=images
            )
            logger.info("✓ Изображения успешно отправлены")
        except Exception as img_error:
            logger.error(f"⚠️ Ошибка при отправке изображений: {img_error}")
            # Если не удалось отправить изображения, отправляем только текст
            await asyncio.sleep(2)  # Добавляем задержку перед повторной попыткой
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=message,
                parse_mode=ParseMode.MARKDOWN
            )
        
        logger.info("✅ Гадание успешно отправлено в канал!")
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке гадания: {str(e)}")
        logger.error(f"Детали ошибки: {type(e).__name__}")

async def send_startup_message():
    """Отправляем первое гадание при запуске бота"""
    try:
        await post_reading()
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке первого гадания: {str(e)}")

def run_schedule():
    """Запускает асинхронную функцию в синхронном контексте"""
    try:
        asyncio.run(post_reading())
    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении запланированной задачи: {str(e)}")

def main():
    """Основная функция для запуска бота по расписанию"""
    print("🤖 Бот для гадания на Таро запущен")
    
    # Отправляем тестовое гадание при запуске
    print("🔄 Отправляем первое гадание...")
    asyncio.run(send_startup_message())
    print("✅ Первое гадание отправлено")
    
    # Настраиваем расписание
    schedule.every().day.at("09:00").do(run_schedule)  # Утренний пост
    schedule.every().day.at("15:35").do(run_schedule)  # Дневной пост
    schedule.every().day.at("15:40").do(run_schedule)  # Дополнительный дневной пост
    schedule.every().day.at("18:00").do(run_schedule)  # Вечерний пост
    schedule.every().day.at("23:00").do(run_schedule)  # Ночной пост
    
    print("\n📅 Расписание гаданий на день:")
    print("   • 09:00 - Утреннее гадание")
    print("   • 15:35 - Дневное гадание")
    print("   • 15:40 - Дополнительное дневное гадание")
    print("   • 18:00 - Вечернее гадание")
    print("   • 23:00 - Ночное гадание")
    print("\n⌛ Бот ожидает следующего времени для гадания...")
    
    # Бесконечный цикл для проверки расписания
    while True:
        try:
            schedule.run_pending()
            time.sleep(30)  # Проверяем расписание каждые 30 секунд
        except Exception as e:
            logger.error(f"❌ Произошла ошибка: {str(e)}")
            time.sleep(60)  # В случае ошибки ждем минуту перед следующей попыткой

if __name__ == '__main__':
    main()
