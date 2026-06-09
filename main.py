
import telebot
import sqlite3


BOT_TOKEN = '8482899652:AAH4JMUoOhU2_Z659elwnJHmvMwa7LkkOIs'
bot = telebot.TeleBot(BOT_TOKEN)

# Функция для выполнения SQL‑запроса
def execute_query(query: str, params: tuple = ()) -> list:
    conn = sqlite3.connect('world_cup.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    return result

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = '''
🤖 Бот по чемпионатам мира по футболу

Доступные команды:
/winner <год> — победитель чемпионата
/final <год> — информация о финале
/top_scorer <год> — лучший бомбардир
/all_winners — все победители
/host <страна> — чемпионаты, проведённые в стране
/help — справка по командам

Примеры:
/winner 2018
/final 1998
/top_scorer 2006
    '''
    bot.reply_to(message, welcome_text)

# Обработчик команды /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = '''
📋 Справка по командам:

/winner <год>
Пример: /winner 2022
Показывает победителя чемпионата мира заданного года.

/final <год>
Пример: /final 2014
Информация о финальном матче чемпионата.

/top_scorer <год>
Пример: /top_scorer 1986
Лучший бомбардир чемпионата мира.

/all_winners
Список всех победителей чемпионатов мира.

/host <страна>
Пример: /host Бразилия
Чемпионаты мира, проведённые в указанной стране.
    '''
    bot.reply_to(message, help_text)

# Обработчик команды /winner
@bot.message_handler(commands=['winner'])
def get_winner(message):
    try:
        year = int(message.text.split()[1])
        query = '''
        SELECT year, winner, runner_up, third_place
        FROM world_cups
        WHERE year = ?
        '''
        result = execute_query(query, (year,))

        if result:
            year, winner, runner_up, third = result[0]
            response = f'''
🏆 Чемпионат мира {year} года

Победитель: {winner}
Финалист: {runner_up}
Третье место: {third if third else '—'}
            '''
        else:
            response = '❌ Чемпионат мира в указанном году не найден.'
    except (IndexError, ValueError):
        response = '❌ Укажите корректный год. Пример: /winner 2018'

    bot.reply_to(message, response)

# Обработчик команды /final
@bot.message_handler(commands=['final'])
def get_final(message):
    try:
        year = int(message.text.split()[1])
        query = '''
        SELECT w.year, f.date, f.stadium, f.city, f.score
        FROM finals f
        JOIN world_cups w ON f.world_cup_id = w.id
        WHERE w.year = ?
        '''
        result = execute_query(query, (year,))

        if result:
            year, date, stadium, city, score = result[0]
            response = f'''
🏟️ Финал чемпионата мира {year}

🗓 Дата: {date}
📍 Стадион: {stadium}
🌆 Город: {city}
⚽ Счёт: {score}
            '''
        else:
            response = '❌ Информация о финале указанного года не найдена.'
    except (IndexError, ValueError):
        response = '❌ Укажите корректный год. Пример: /final 1994'

    bot.reply_to(message, response)

# Обработчик команды /top_scorer
@bot.message_handler(commands=['top_scorer'])
def get_top_scorer(message):
    try:
        year = int(message.text.split()[1])
        query = '''
        SELECT w.year, t.player_name, t.country, t.goals
        FROM top_scorers t
        JOIN world_cups w ON t.world_cup_id = w.id
        WHERE w.year = ?
        ORDER BY t.goals DESC
        LIMIT 1
        '''
        result = execute_query(query, (year,))

        if result:
            year, player, country, goals = result[0]
            response = f'''
⭐ Лучший бомбардир ЧМ {year}:

👤 Игрок: {player}
🌍 Страна: {country}
⚽ Голов: {goals}
            '''
        else:
            response = '❌ Лучший бомбардир для указанного года не найден.'
    except (IndexError, ValueError):
        response = '❌ Укажите корректный год. Пример: /top_scorer 2002'

    bot.reply_to(message, response)

# Обработчик команды /all_winners
@bot.message_handler(commands=['all_winners'])
def get_all_winners(message):
    query = '''
    SELECT year, winner, host_country
    FROM world_cups
    ORDER BY year
    '''
    results = execute_query(query)

    if results:
        response = '🏆 Все победители чемпионатов мира:\n\n'
        for year, winner, host in results:
            response += f'{year}: {winner} (хозяин: {host})\n'
    else:
        response = '❌ Данные о победителях не найдены.'

    bot.reply_to(message, response)

# Обработчик команды /host
@bot.message_handler(commands=['host'])
def get_hosted_championships(message):
    try:
        country = ' '.join(message.text.split()[1:])
        if not country:
            raise ValueError

        query = '''
        SELECT year, winner, winner_goals, runner_up_goals
        FROM world_cups w
        JOIN finals f ON w.id = f.world_cup_id
        WHERE w.host_country = ?
        ORDER BY year
        '''
        results = execute_query(query, (country,))

        if results:
            response = f'🗺️ Чемпионаты мира, проведённые в {country}:\n\n'
            for year, winner, w_goals, r_goals in results:
                response += f'{year}: {winner} ({w_goals}:{r_goals})\n'
        else:
            response = f'❌ В стране {country} чемпионаты мира не проводились.'
    except ValueError:
        response = '❌ Укажите страну. Пример: /host Италия'

    bot.reply_to(message, response)

# Запуск бота
if __name__ == '__main__':
    print('Бот запущен...')
    bot.polling(none_stop=True)