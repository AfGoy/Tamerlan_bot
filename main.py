import asyncio
import logging
import sys
from random import choice, randint
from dotenv import load_dotenv
import os
from sqlalchemy import Column, Integer, String, select, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

load_dotenv()

TK = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
FIRST_ID = os.getenv("FIRST_TID")
SEC_ID = os.getenv("SECOND_TID")

Base = declarative_base()
engine = create_async_engine("sqlite+aiosqlite:///quotes.db")
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False,)


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True)
    text = Column(String, nullable=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Я реальный Тамерлан")

@dp.message(Command("quote"))
async def quote_handler(message: Message):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Quote).order_by(func.random()).limit(1)
        )
        quote = result.scalar()

        await message.answer(f"Вот ваша цитата Тамерлана: \n{quote.text}")

@dp.message(Command("addquote"))
async def quote_handler(message: Message):
    full_text = message.text

    command = "/addquote@Tamerlan1488_bot"
    if full_text.startswith(command):
        quote_text = full_text[len(command):].strip()
    else:
        quote_text = full_text.split(maxsplit=1)[1] if len(full_text.split()) > 1 else ""

    if message.from_user.id == int(ADMIN_ID):
        if not quote_text:
            await message.answer("Цитата не может быть пустой. Пожалуйста, введите текст цитаты после команды /addquote.")
            return

        async with AsyncSessionLocal() as session:
            try:
                async with session.begin():
                    quote = Quote(text=quote_text)
                    session.add(quote)
                await message.answer(f"Цитата добавлена: {html.quote(quote_text)}")
            except SQLAlchemyError as e:
                logging.error(f"Ошибка базы данных при добавлении цитаты: {e}")
                await message.answer("Произошла ошибка при добавлении цитаты.")
    else:
        await message.answer("У вас нет прав для добавления цитат.")


@dp.message()
async def echo_handler(message: Message):
    num = randint(0, 100)
    if (message.from_user.id == int(FIRST_ID) or message.from_user.id == int(SEC_ID)) and num == 67:
        await message.answer("Тамерлан успокойся!")

async def main() -> None:
    await init_db()

    bot = Bot(token=TK, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        await dp.start_polling(bot)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())