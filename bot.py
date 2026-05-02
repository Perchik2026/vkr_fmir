# bot.py
import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from texts import PP, REQ, AGREEMENT

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VK_TOKEN = os.getenv('VK_TOKEN')
if not VK_TOKEN:
    raise ValueError("VK_TOKEN не найден в переменных окружения")

GROUP_ID = int(os.getenv('GROUP_ID', '237589569'))

USER_DATA_FILE = 'user_data.json'


def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_user_data(data):
    with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def update_user(user_id, first_name, last_name, action):
    data = load_user_data()
    uid = str(user_id)
    now = datetime.now().isoformat()
    
    if uid not in data:
        data[uid] = {
            "user_id": user_id,
            "first_name": first_name,
            "last_name": last_name,
            "created_at": now,
            "last_activity": now,
            "actions": []
        }
    
    data[uid]["last_activity"] = now
    data[uid]["actions"].append({"action": action[:50], "time": now})
    save_user_data(data)


def get_user_name(vk, user_id):
    try:
        user = vk.users.get(user_ids=user_id)[0]
        return user.get('first_name', ''), user.get('last_name', '')
    except Exception as e:
        logger.error(f"Ошибка получения имени: {e}")
        return "", ""


def create_main_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("📋 ОТЧЕТ О ПП", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("📚 ВКР (в разработке)", color=VkKeyboardColor.SECONDARY)
    keyboard.add_line()
    keyboard.add_button("📝 ОБЩИЕ ТРЕБОВАНИЯ", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("📄 ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ", color=VkKeyboardColor.PRIMARY)
    return keyboard


def create_pp_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("О БЛАНКАХ", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("ИНДИВИДУАЛЬНОЕ ЗАДАНИЕ", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("ТРЕБОВАНИЯ ДЛЯ ОТЧЕТА", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("ФИНАНСОВЫЙ АНАЛИЗ", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("PESTLE-анализ", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("SWOT-анализ", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("МАТРИЦА РЕШЕНИЙ SWOT-анализа", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("КОНКУРЕНТНЫЙ АНАЛИЗ", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("АНАЛИЗ 5 СИЛ ПОРТЕРА", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🔙 Главное меню", color=VkKeyboardColor.NEGATIVE)
    return keyboard


def create_req_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Эффект и Эффективность", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Источники", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Ссылки", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Список литературы", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Цитирование", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Публикации ППС", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Птичий язык", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Слова-паразиты", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Научный стиль", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Запрещенные сети", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Форматирование текста", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Англицизмы", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Сроки проверки работ", color=VkKeyboardColor.PRIMARY)
    keyboard.add_button("Обозначения и сокращения", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Материалы по оформлению", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("🔙 Главное меню", color=VkKeyboardColor.NEGATIVE)
    return keyboard


class BotHandler:
    def __init__(self, vk_api_instance):
        self.vk = vk_api_instance
    
    def send_message(self, user_id, text, keyboard=None):
        try:
            self.vk.messages.send(
                user_id=user_id,
                message=text,
                random_id=0,
                keyboard=keyboard.get_keyboard() if keyboard else None
            )
        except Exception as e:
            logger.error(f"Ошибка отправки: {e}")
    
    def handle(self, user_id, text, first_name, last_name):
        update_user(user_id, first_name, last_name, text[:50])
        
        if text == "🔙 Главное меню" or text.lower() in ["start", "начать", "/start"]:
            self.send_message(user_id, f"🎓 Добро пожаловать, {first_name}!\n\nВыберите раздел:", create_main_keyboard())
            return
        
        if text == "📋 ОТЧЕТ О ПП":
            self.send_message(user_id, "Выберите раздел отчета о ПП:", create_pp_keyboard())
            return
        
        if text == "📝 ОБЩИЕ ТРЕБОВАНИЯ":
            self.send_message(user_id, "Выберите раздел общих требований:", create_req_keyboard())
            return
        
        if text == "📚 ВКР (в разработке)":
            self.send_message(user_id, "📚 Раздел ВКР находится в разработке", create_main_keyboard())
            return
        
        if text == "📄 ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ":
            agreement_text = AGREEMENT.get("ПОЛЬЗОВАТЕЛЬСКОЕ СОГЛАШЕНИЕ", AGREEMENT)
            self.send_message(user_id, agreement_text, create_main_keyboard())
            return
        
        if text in PP:
            self.send_message(user_id, PP[text], create_pp_keyboard())
            return
        
        if text in REQ:
            self.send_message(user_id, REQ[text], create_req_keyboard())
            return
        
        self.send_message(user_id, "❌ Неизвестная команда\n\nИспользуйте кнопки меню или напишите /start", create_main_keyboard())


def run_bot():
    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        longpoll = VkBotLongPoll(vk_session, GROUP_ID)
        handler = BotHandler(vk)
        
        logger.info(f"✅ Бот запущен! ID сообщества: {GROUP_ID}")
        
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                try:
                    msg = event.object.message
                    user_id = msg['from_id']
                    text = msg.get('text', '')
                    
                    first_name = msg.get('from_first_name', '')
                    last_name = msg.get('from_last_name', '')
                    
                    if not first_name:
                        first_name, last_name = get_user_name(vk, user_id)
                    
                    handler.handle(user_id, text, first_name, last_name)
                    
                except Exception as e:
                    logger.error(f"Ошибка обработки события: {e}")
                    
    except Exception as e:
        logger.error(f"❌ Ошибка запуска: {e}")
        raise


if __name__ == "__main__":
    run_bot()
