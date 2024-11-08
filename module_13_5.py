from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb = ReplyKeyboardMarkup(resize_keyboard=True)
bt_info = KeyboardButton('Информация')
dt_calc = KeyboardButton('Расчет')
kb.add(bt_info, dt_calc)


class UserState(StatesGroup):
      age = State()
      growth = State()
      weight = State()


API = '_'
bot = Bot(token=API)
dp = Dispatcher(bot, storage=MemoryStorage())

data = {}

#функция для проверки ответа, млжет ли быть ответ чилом

def try_int(x):
    try:
        int(x)
        return True
    except ValueError:
        return False

#реагируем на текст 'Calories' и запрашиваем возраст
    
@dp.message_handler(text='Расчет')
async def set_age(message):
    await message.answer('Введите свой возраст')
    await UserState.age.set()

#проверяем возраст, если возрас передан коректно то запускаем функцию set_growth, если нет то запрашиваем возраст еще раз  

@dp.message_handler(state=UserState.age)
async def chec_age(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    if try_int(data['age']):
        await set_growth(message, state, data=data)
    else:
        await message.answer('Возраст введен не корректно, попробуйте еще раз.')
        await set_age(message)
        
 # если в data на была записана информация о возрасте записываем ее и запрашиваем рост, если информация уже есть просто запрашиваем рост

@dp.message_handler(state=UserState.age)
async def set_growth(message, state, data):
    if 'age' in data.keys():
        await message.answer('Введите свой рост')
        await UserState.growth.set()
    else:
        await state.update_data(age=message.text)
        data = await state.get_data()
        await message.answer('Введите свой рост')
        await UserState.growth.set()
    
# проверяем переданные данные о росте, если корректно, запускаем функцию set_weight, если нет просим ввести данные заново

@dp.message_handler(state=UserState.growth)
async def chec_growth(message, state):
    await state.update_data(growth=message.text)
    data = await state.get_data()
    if try_int(data['growth']):
        await set_weight(message, state, data=data)
    else:
        await message.answer('Рост введен не корректно, попробуйте еще раз.')
        await set_growth(message, state, data)

# если в дате есть информация о росте запрашиваем вес, если нет то добавляем рост и запрашиваем вес.

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state, data):
    if 'growth' in data.keys():
        await message.answer('Введите свой вес')
        await UserState.weight.set()
    else:    
        await state.update_data(growth=message.text)
        data = await state.get_data()
        await message.answer('Введите свой вес')
        await UserState.weight.set()
# проверяем вес, если вес корректный, то запускаем функцию set_weight, если нет просим ввести вес еще раз

@dp.message_handler(state=UserState.weight)
async def chec_weight(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    if try_int(data['weight']):
        await send_calories(message, state, data=data)
    else:
        await message.answer('Вес введен не корректно, попробуйте еще раз.')
        await set_weight(message, state, data)

# производим расчет нормы каллориев и отправляем ее пользователю

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state, data):
    
    women_cal = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) - 161
    men_cal = 10 * int(data['weight']) + 6.25 * int(data['growth']) - 5 * int(data['age']) + 5
    await message.answer(f'Ваша норма калорий {men_cal}')
    await state.finish()

def input_info(file):
    with open(file, 'r') as f:
        result = f.read()
    return result        
                    

@dp.message_handler(text='Информация')
async def info(message):
    
    await message.answer(input_info('info.txt'))

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)

@dp.message_handler()
async def all_massage(message):
    await message.answer('Введите команду /start, чтобы начать общение.', reply_markup=kb)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)