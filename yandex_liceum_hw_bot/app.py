import logging
import random
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

UNSPLASH_API_KEY = 'cXN1IR42M6RYLk5B_SdFA4E4ImgGly4fbJ_FZGqozMY'
PIC = ''
Hi = False
ANSWERED = False


async def send_image_by_keyword(update: Update, context):
    # Отправка соообщения в случае правильного ответа в тесте
    keyword = PIC
    headers = {'Authorization': f'Client-ID {UNSPLASH_API_KEY}'}
    print(PIC)
    params = {'query': PIC}
    response = requests.get('https://api.unsplash.com/photos/random', headers=headers, params=params)
    if response.ok:
        data = response.json()
        if data.get('urls') is not None:
            image_url = data['urls']['regular']
            await context.bot.send_photo(update.effective_chat.id, photo=image_url)
        else:
            await update.message.reply_text("Извините, я не нашёл картинку на эту тему")
    else:
        await update.message.reply_text("Извините, в прцессе поиска картинок призошла ошибка")


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
    )

    application = Application.builder().token('7108896576:AAEwiSpVqata0L-H3Sb0tq1d_Fj3MmC34nQ').build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_nickname))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CommandHandler("play", play))
    application.add_handler(CallbackQueryHandler(handle_button_click))
    application.run_polling()


engine = create_engine('sqlite:///db1')
Base = declarative_base()


class User(Base):
    # ORM для данных пользователя
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    authorized = Column(String, default=False)


async def start(update: Update, context: CallbackContext):
    # Функция start
    await update.message.reply_text(
        "Привет! Введите ваш никнейм:"
    )


async def handle_nickname(update: Update, context: CallbackContext):
    # Получение никнейма из ответа пользователя
    nickname = update.message.text

    # Проверка, что никнейм не пустой
    if nickname:
        # Получить ID пользователя
        user_id = update.effective_user.id

        session = Session(bind=create_engine('sqlite:///db1'))

        # Проверка, есть ли пользователь в базе данных
        user_data = session.query(User).filter_by(id=user_id).first()
        if user_data is None:
            # Добавить нового пользователя
            user_data = User(id=user_id, username=nickname)
            session.add(user_data)

        # Обновление статуса авторизации
            user_data.authorized = True
            session.commit()

            session.close()

            await update.message.reply_html(
                f"Привет {nickname}! Вы авторизованы."
            )
        else:
            await update.message.reply_html('Вам доступны команды /help и /play')
    else:
        await update.message.reply_text(
            "Никнейм не может быть пустым. Попробуйте еще раз."
        )


async def help_command(update: Update, context):
    # команда help
    await update.message.reply_text("Чтобы начать играть напишите команду /play")


async def echo(update: Update, context):
    # Реакция на текст сообщений ползователя
    await update.message.reply_text('Используйте кнопки или команды')


async def play(update: Update, context: CallbackContext):
    # Команда play
    buttons = [
        [
            InlineKeyboardButton("Animals", callback_data='animals'),
            InlineKeyboardButton("Birds", callback_data='birds')
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        "Ура! Давайте играть! Выберите тему:",
        reply_markup=keyboard
    )


async def handle_button_click(update: Update, context: CallbackContext):
    # Оработчик кнопок
    query = update.callback_query
    theme = query.data
    if theme == 'animals':
        await query.answer('Вы выбрали тему "животные"!')
        engine = create_engine('sqlite:///db1')
        Base = declarative_base()

        # Определяем ORM модель
        class Animal(Base):
            __tablename__ = 'animals'

            id = Column(Integer, primary_key=True)
            eng = Column(String)
            ru = Column(String)
            wrong1 = Column(String)
            wrong2 = Column(String)

        # Создаем таблицы в базе данных
        Base.metadata.create_all(bind=engine)

        # Создаем сессию для работы с базой данных
        Session = sessionmaker(bind=engine)
        session = Session()

        # Получаем все значения из таблицы animals
        animals = session.query(Animal).all()

        # Создание списка строк для вывода
        output = []
        for animal in animals:
            output.append([animal.eng, animal.ru, animal.wrong1, animal.wrong2])
        random.shuffle(output)
        context.user_data['output'] = output
        context.user_data['current_quiz_index'] = 0

        await send_quiz_question(query.message, context)

    elif theme == 'birds':
        await query.answer('Вы выбрали тему "птицы"!')
        engine = create_engine('sqlite:///db1')
        Base = declarative_base()

        # Определяем ORM модель
        class Bird(Base):
            __tablename__ = 'birds'

            id = Column(Integer, primary_key=True)
            eng = Column(String)
            ru = Column(String)
            wrong1 = Column(String)
            wrong2 = Column(String)

        # Создаем таблицы в базе данных
        Base.metadata.create_all(bind=engine)

        # Создаем сессию для работы с базой данных
        Session = sessionmaker(bind=engine)
        session = Session()

        # Получаем все значения из таблицы animals
        birds = session.query(Bird).all()

        # Создание списка строк для вывода
        output = []
        for bird in birds:
            output.append([bird.eng, bird.ru, bird.wrong1, bird.wrong2])
        random.shuffle(output)
        context.user_data['output'] = output
        context.user_data['current_quiz_index'] = 0

        await send_quiz_question(query.message, context)

    else:
        # Верный ответ
        if theme[0] == 'c':
            await send_image_by_keyword(update, context)
        # Неверный ответ
        elif theme == 'wrong':
            await query.message.reply_text("Неверно")
        else:
            await query.message.reply_text("Invalid choice!")

        await send_quiz_question(query.message, context)


async def send_quiz_question(message, context):
    # Викторины
    global PIC
    output = context.user_data['output']
    current_quiz_index = context.user_data['current_quiz_index']

    if current_quiz_index < len(output):
        quiz = output[current_quiz_index]
        question = quiz[1]
        correct_answer = quiz[0]
        answers = [quiz[2], quiz[3], quiz[0]]
        random.shuffle(answers)
        PIC = correct_answer

        buttons = []
        for answer in answers:
            if answer == correct_answer:
                buttons.append([InlineKeyboardButton(answer, callback_data='correct' + correct_answer)])
            else:
                buttons.append([InlineKeyboardButton(answer, callback_data='wrong')])
        keyboard = InlineKeyboardMarkup(buttons)
        await message.reply_text(question, reply_markup=keyboard)

        context.user_data['current_quiz_index'] += 1
    else:
        await message.reply_text("Игра окончена. Спасибо за участие!")


if __name__ == '__main__':
    main()
