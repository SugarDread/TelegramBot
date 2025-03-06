from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


import app.keyboards as kb
from app.middlewares import TestMiddleWare
import app.database.requests as rq

router = Router()



class Reg(StatesGroup):
    name = State()
    number = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await rq.set_user(message.from_user.id)
    await message.reply('Добро пожаловать в магазин', reply_markup=kb.main)

@router.message(F.text == 'Каталог')
async def catalog(message: Message):
    await message.answer('Выберите категорию товара', reply_markup=await kb.categories())

@router.callback_query(F.data.startswith('category_'))
async def category(callback: CallbackQuery):
    await callback.answer('Вы выбрали категорию')
    await callback.message.answer('Выберите товар по категории', 
                                  reply_markup=await kb.items(callback.data.split('_')[1]))


@router.callback_query(F.data.startswith('item_'))
async def item(callback: CallbackQuery):
    item_data = await rq.get_item(callback.data.split('_')[1])
    await callback.answer('Вы выбрали товар')
    await callback.message.answer(f'Название: {item_data.name}\nОписание: {item_data.description}\nЦена: {item_data.price}', 
                                  reply_markup=await kb.items(callback.data.split('_')[1]))
    

@router.callback_query(F.data == 'to_main')
async def to_main(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.answer('Выберите категорию товара', reply_markup=await kb.categories())


@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('Это команда /help')

@router.message(F.text == 'Wassup Bejing?')
async def wassup(message: Message):
    await message.answer('Good good')

@router.message(F.photo)
async def get_photo_id(message: Message):
    await message.answer(f'ID фото: {message.photo[-1].file_id}')

@router.message(Command('get_photo'))
async def get_photo(message: Message):
    await message.answer_photo(photo='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTR0c4zR8yHUsQgD810z3a9gfmQZUnn-8y5JA&s',
                               caption='Peta')
    
@router.callback_query(F.data == 'catalogi')
async def catalog(callback: CallbackQuery):
    await callback.answer('Выбран каталог', show_alert=True)
    await callback.message.edit_text('Kys', reply_markup=await kb.inline_cars())

@router.message(Command('reg'))
async def reg_one(message: Message, state: FSMContext):
    await state.set_state(Reg.name)
    await message.answer('Введите ваше имя')

@router.message(Reg.name)
async def reg_two(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Reg.number)
    await message.answer('Введите номер')

@router.message(Reg.number)
async def reg_three(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    data = await state.get_data()
    await message.answer(f'Регистрация завершена\nИмя: {data["name"]}\nНомер: {data["number"]}')
    await state.clear()