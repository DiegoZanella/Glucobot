import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import numpy as np
import sqlite3
from databasefunc import *
from flow_func import *

print('Hello, I am Glucobot. I am working, please be quiet.')
# Training TOKEN
bot = Bot(token=TOKEN)
# Dispatcher
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
# Finite State Machine
class Form(StatesGroup):
    # Ask for info
    ask = State()
    # Entering data Before breakfast
    edbb = State()
    # rewrite Before Breakfast
    rwbb = State()
    # Entering data After breakfast
    edab = State()
    rwab = State()
    # Entering data Before lunch
    edbl = State()
    rwbl = State()
    # Entering data after lunch
    edal = State()
    rwal = State()
    # Entering data before dinner
    edbd = State()
    rwbd = State()
    # Entering data after dinner
    edad = State()
    rwad = State()
    # Entering data AM medicine
    edam = State()
    rwam = State()
    # Entering data PM medicine
    edpm = State()
    rwpm = State()
    # More options
    more_opt = State()
    # Manual mode
    manual = State()

### Welcome message
@dp.message_handler(commands=['start', 'help'])
async def welcome(message: types.Message):
    # Get user info
    user_id = message.from_user.id
    user_name = message.from_user.username
    user_firstname = message.from_user.first_name
    user_lastname = message.from_user.last_name
    # Enter user info in database
    conn = sqlite3.connect('GlucoDB.db')
    cur = conn.cursor()
    cur.execute(''' INSERT OR IGNORE INTO Users (user_id, user_name, user_firstname, user_lastname)
                     VALUES (?,?,?,?)''', (user_id, user_name, user_firstname, user_lastname))
    conn.commit()
    conn.close()
    # Send welcoming message
    await message.answer('Hola, soy Glucobot 🤖\n'
                         'Para iniciar, escribe /registrar  \n')

## Start to register
butt1 = InlineKeyboardButton(text='Desayuno☀️', callback_data='gluc_des')
butt2 = InlineKeyboardButton(text='Comida🍝', callback_data='gluc_comida')
butt3 = InlineKeyboardButton(text='Cena🌜', callback_data='gluc_cena')
butt4 = InlineKeyboardButton(text='Medicinas💊', callback_data='medicina')
doc_butt = InlineKeyboardButton(text='Descargar documento📄', callback_data='Document')
other_butt = InlineKeyboardButton(text='Más opciones🛠️', callback_data='more')
keyboard1 = InlineKeyboardMarkup().add(butt1, butt2, butt3).add(butt4).add(doc_butt, other_butt)
# Ask for new record
@dp.message_handler(commands=['registrar'])
async def welcome(message: types.Message):
    # Set State
    await Form.ask.set()
    # Ask to select option
    await message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)


##################### SEND DOCUMENT FUNCTIONS #################
###############################################################
# This funcion sends excel file when called
async def send_sheet(user_id):
    document = generate_sheet(user_id)
    caption = 'He recopilado toda tu información en esta tabla de excel. Espero que te sea útil 🤖'
    await bot.send_document(chat_id=user_id, document=document, caption=caption)
# When user presses Document button, this function is triggered and calls the sen_sheet function
@dp.callback_query_handler(text=['Document'], state=Form.ask)
async def trigger_sendsheet(call: types.CallbackQuery, state: FSMContext):
    user_id = call.message.chat.id
    await send_sheet(user_id)
    await call.message.answer('¿Te puedo ayudar con algo más?🤖', reply_markup=keyboard1)

############## BREAKFAST FUNCTIONS ##################################
#####################################################################
#####################################################################
#### Antes o después keyboard Breakfast
butt5 = InlineKeyboardButton(text='Antes', callback_data='bef_break')
butt6 = InlineKeyboardButton(text='Después', callback_data='aft_break')
keyboard2 = InlineKeyboardMarkup().add(butt5, butt6)
# This function is trigered when user presses the Desayuno button.
@dp.callback_query_handler(text=['gluc_des'], state=Form.ask)
async def gluc_break(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('¿Quieres que registre tu glucosa antes o después del desayuno?🤖 ',
                              reply_markup=keyboard2)
    await call.answer()
############## Before Breakfast
# Ask for before breakfast value when user presses the Antes button. If a record for the same
# # user_id and date already exists, warn user
@dp.callback_query_handler(text=['bef_break'], state=Form.ask)
async def gluc_bef_break(call: types.CallbackQuery, state: FSMContext):
    date_time  =str(call.message.date).split()
    user_id = str(call.from_user.id)
    x = check_ask('BeforeBreakfast', date_time, user_id, meal='antes del desayuno', meds=None)
    if x[0] == 0:
        await Form.edbb.set()
        await call.message.answer('¿Cuál fue tu lectura antes de desayunar?')
    elif x[0]==1:
        await Form.rwbb.set()
        await call.message.answer(x[1], reply_markup=x[2])
# Processing before breakfast value
@dp.message_handler(state=Form.edbb)
async def gluc_bef_break_process(message: types.Message, state: FSMContext):
    # Reset state
    await Form.ask.set()
    # Get info from user message
    table = 'BeforeBreakfast'
    date_time = str(message.date).split()
    value = int(message.text)
    user_id = message.from_user.id
    reply = write(table, date_time, user_id, meal='antes del desayuno', meds=None, value=value)
    await message.reply(reply)
    await message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)
@dp.callback_query_handler(text=['cancel'],state=[Form.rwbb, Form.rwab, Form.rwbl,
                                Form.rwal, Form.rwbd, Form.rwad, Form.rwam, Form.rwpm])
async def cancel_rewrite(call: types.CallbackQuery, state: FSMContext):
    # Reset state
    await Form.ask.set()
    reply = 'No modifiqué tu registro anterior. ¿Puedo ayudarte con algo más? 🤖'
    await call.message.answer(reply, reply_markup=keyboard1)
@dp.callback_query_handler(text=['rewriteBeforeBreakfast'],state=Form.rwbb)
async def rewrite_gluc_bef_break(call: types.CallbackQuery, state:FSMContext):
    date_time = str(call.message.date).split()
    date = date_time[0]
    user_id = str(call.from_user.id)
    delete_record('BeforeBreakfast', user_id,date)
    # Set new state
    await Form.edbb.set()
    # Ask for a value
    await call.message.answer('He eliminado tu registro anterior 🤖\n¿Cuál fue tu lectura antes del desayuno?')
    await call.answer()
############## After Breakfast
# Ask for after breakfast value when user presses the Después button. If a record for the same
# # user_id and date already exists, warn user
@dp.callback_query_handler(text=['aft_break'], state=Form.ask)
async def gluc_aft_break(call: types.CallbackQuery, state: FSMContext):
    date_time = str(call.message.date).split()
    user_id = str(call.from_user.id)
    x = check_ask('AfterBreakfast', date_time, user_id, meal='después del desayuno', meds=None)
    if x[0] == 0:
        await Form.edab.set()
        await call.message.answer('¿Cuál fue tu lectura después de desayunar?')
    elif x[0]==1:
        await Form.rwab.set()
        await call.message.answer(x[1], reply_markup=x[2])
# Processing after breakfast value
@dp.message_handler(state=Form.edab)
async def gluc_aft_break_process(message: types.Message, state: FSMContext):
    # Reset state
    await Form.ask.set()
    # Get info from user message
    table = 'AfterBreakfast'
    date_time = str(message.date).split()
    value = int(message.text)
    user_id = message.from_user.id
    reply = write(table, date_time, user_id, meal='después del desayuno', meds=None, value=value)
    await message.reply(reply)
    await message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)

# Delete old record and ask for new value
@dp.callback_query_handler(text=['rewriteAfterBreakfast'], state=Form.rwab)
async def rewrite_gluc_aft_break(call: types.CallbackQuery, state: FSMContext):
        date_time = str(call.message.date).split()
        date = date_time[0]
        user_id = str(call.from_user.id)
        delete_record('AfterBreakfast', user_id, date)
        # Set new state
        await Form.edab.set()
        # Ask for a value
        await call.message.answer('He eliminado tu registro anterior 🤖\n¿Cuál fue tu lectura después del desayuno?')
        await call.answer()

#####################  LUNCH FUNCTIONS #####################
############################################################
#### Antes o después Lunch keyboard
butt7 = InlineKeyboardButton(text='Antes', callback_data='bef_lunch')
butt8 = InlineKeyboardButton(text='Después', callback_data='aft_lunch')
keyboard3 = InlineKeyboardMarkup().add(butt7, butt8)
# This function is trigered when user presses the Desayuno button.
@dp.callback_query_handler(text=['gluc_comida'], state=Form.ask)
async def gluc_lunch(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('¿Quieres que registre tu glucosa antes o '
                              'después de comer?🤖 ', reply_markup=keyboard3)
    await call.answer()
####### Before Lunch
# Ask for before lunch value when user presses the Antes button. If a record for the same
# user_id and date already exists, warn user
@dp.callback_query_handler(text=['bef_lunch'], state=Form.ask)
async def gluc_bef_lunch(call: types.CallbackQuery, state: FSMContext):
    date_time  =str(call.message.date).split()
    user_id = str(call.from_user.id)
    x = check_ask('BeforeLunch', date_time, user_id, meal='antes de la comida', meds=None)
    if x[0] == 0:
        await Form.edbl.set()
        await call.message.answer('¿Cuál fue tu lectura antes de comer?')
    elif x[0]==1:
        await Form.rwbl.set()
        await call.message.answer(x[1], reply_markup=x[2])
# After receiving a value, write it into the database and display new help menu
@dp.message_handler(state=Form.edbl)
async def gluc_bef_lunch_process(message: types.Message, state: FSMContext):
    # Reset state
    await Form.ask.set()
    # Get info from user message
    table = 'BeforeLunch'
    date_time = str(message.date).split()
    value = int(message.text)
    user_id = message.from_user.id
    reply = write(table, date_time, user_id, meal='antes de la comida', meds=None, value=value)
    await message.reply(reply)
    await message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)
@dp.callback_query_handler(text=['rewriteBeforeLunch'],state=Form.rwbl)
async def rewrite_gluc_bef_lunch(call: types.CallbackQuery, state:FSMContext):
    date_time = str(call.message.date).split()
    date = date_time[0]
    user_id = str(call.from_user.id)
    delete_record('BeforeLunch', user_id,date)
    # Set new state
    await Form.edbl.set()
    # Ask for a value
    await call.message.answer('He eliminado tu registro anterior 🤖\n¿Cuál fue tu lectura antes del desayuno?')
    await call.answer()
############### After Lunch
# Ask for after lunch value when user presses the Después button. If a record for the same
# user_id and date already exists, warn user
@dp.callback_query_handler(text=['aft_lunch'], state=Form.ask)
async def gluc_aft_lunch(call: types.CallbackQuery, state: FSMContext):
    date_time = str(call.message.date).split()
    user_id = str(call.from_user.id)
    x = check_ask('AfterLunch', date_time, user_id, meal='después de la comida', meds=None)
    if x[0] == 0:
        await Form.edal.set()
        await call.message.answer('¿Cuál fue tu lectura después de comer?')
    elif x[0]==1:
        await Form.rwal.set()
        await call.message.answer(x[1], reply_markup=x[2])
# Processing after breakfast value
@dp.message_handler(state=Form.edal)
async def gluc_aft_lunch_process(message: types.Message, state: FSMContext):
    # Reset state
    await Form.ask.set()
    # Get info from user message
    table = 'AfterLunch'
    date_time = str(message.date).split()
    value = int(message.text)
    user_id = message.from_user.id
    reply = write(table, date_time, user_id, meal='después de la comida', meds=None, value=value)
    await message.reply(reply)
    await message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)
# Delete old record and ask for new value
@dp.callback_query_handler(text=['rewriteAfterLunch'], state=Form.rwal)
async def rewrite_gluc_aft_lunch(call: types.CallbackQuery, state: FSMContext):
        date_time = str(call.message.date).split()
        date = date_time[0]
        user_id = str(call.from_user.id)
        delete_record('AfterLunch', user_id, date)
        # Set new state
        await Form.edal.set()
        # Ask for a value
        await call.message.answer('He eliminado tu registro anterior 🤖\n¿Cuál fue tu lectura después de la comida?')
        await call.answer()
##################### DINNER FUNCTIONS ####################
###########################################################
# Antes o después keyboard Dinner
butt8 = InlineKeyboardButton(text='Antes', callback_data='bef_dinner')
butt9 = InlineKeyboardButton(text='Después', callback_data='aft_dinner')
keyboard4 = InlineKeyboardMarkup().add(butt8, butt9)
# This function is trigered when user presses the Cena button.
@dp.callback_query_handler(text=['gluc_cena'], state=Form.ask)
async def gluc_dinner(call: types.CallbackQuery):
    await call.message.answer('¿Quieres que registre tu glucosa '
                              'antes o después de cenar?🤖 ', reply_markup=keyboard4)
    await call.answer()
##########3 Before Dinner
# Ask for before dinner value when user presses the Antes button. If a record for the same
# # user_id and date already exists, warn user
@dp.callback_query_handler(text=['bef_dinner'], state=Form.ask)
async def gluc_bef_dinner(call: types.CallbackQuery, state: FSMContext):
    date_time  =str(call.message.date).split()
    user_id = str(call.from_user.id)
    x = check_ask('BeforeDinner', date_time, user_id, meal='antes de cenar', meds=None)
    if x[0] == 0:
        await Form.edbd.set()
        await call.message.answer('¿Cuál fue tu lectura antes de cenar?')
    elif x[0]==1:
        await Form.rwbd.set()
        await call.message.answer(x[1], reply_markup=x[2])
# Processing before dinner value
@dp.message_handler(state=Form.edbd)
async def gluc_bef_dinner_process(message: types.Message, state: FSMContext):
    # Reset state
    await Form.ask.set()
    # Get info from user message
    table = 'BeforeDinner'
    date_time = str(message.date).split()
    value = int(message.text)
    user_id = message.from_user.id
    reply = write(table, date_time, user_id, meal='antes de cenar', meds=None, value=value)
    await message.reply(reply)
    await message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)
@dp.callback_query_handler(text=['rewriteBeforeDinner'],state=Form.rwbd)
async def rewrite_gluc_bef_dinner(call: types.CallbackQuery, state:FSMContext):
    date_time = str(call.message.date).split()
    date = date_time[0]
    user_id = str(call.from_user.id)
    delete_record('BeforeDinner', user_id,date)
    # Set new state
    await Form.edbd.set()
    # Ask for a value
    await call.message.answer('He eliminado tu registro anterior 🤖\n¿Cuál fue tu lectura antes de cenar?')
    await call.answer()
############## After Dinner
# Ask for after dinner value when user presses the Después button. If a record for the same
# user_id and date already exists, warn user
@dp.callback_query_handler(text=['aft_dinner'], state=Form.ask)
async def gluc_aft_dinner(call: types.CallbackQuery, state: FSMContext):
    date_time = str(call.message.date).split()
    user_id = str(call.from_user.id)
    x = check_ask('AfterDinner', date_time, user_id, meal='después de cenar', meds=None)
    if x[0] == 0:
        await Form.edad.set()
        await call.message.answer('¿Cuál fue tu lectura después de cenar?')
    elif x[0]==1:
        await Form.rwad.set()
        await call.message.answer(x[1], reply_markup=x[2])
# Processing after breakfast value
@dp.message_handler(state=Form.edad)
async def gluc_aft_dinner_process(message: types.Message, state: FSMContext):
    # Reset state
    await Form.ask.set()
    # Get info from user message
    table = 'AfterDinner'
    date_time = str(message.date).split()
    value = int(message.text)
    user_id = message.from_user.id
    reply = write(table, date_time, user_id, meal='después de cenar', meds=None, value=value)
    await message.reply(reply)
    await message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)
# Delete old record and ask for new value
@dp.callback_query_handler(text=['rewriteAfterDinner'], state=Form.rwad)
async def rewrite_gluc_aft_break(call: types.CallbackQuery, state: FSMContext):
    date_time = str(call.message.date).split()
    date = date_time[0]
    user_id = str(call.from_user.id)
    delete_record('AfterDinner', user_id, date)
    # Set new state
    await Form.edad.set()
    # Ask for a value
    await call.message.answer('He eliminado tu registro anterior 🤖\n¿Cuál fue tu lectura después de cenar?')
    await call.answer()

################### MEDICINAS #####################
###################################################
# AM or PM Keyboard
butt10 = InlineKeyboardButton(text='Mañana', callback_data='AM')
butt11 = InlineKeyboardButton(text='Noche', callback_data='PM')
keyboard5 = InlineKeyboardMarkup().add(butt10, butt11)
# This function is trigered when user presses the Medicinas button.
@dp.callback_query_handler(text=['medicina'], state=Form.ask)
async def medicina(call: types.CallbackQuery):
    await call.message.answer('¿Quieres que registre tus '
                              'medicinas de la mañana o de la noche?🤖 ', reply_markup=keyboard5)
    await call.answer()
############## AM
# Ask for before breakfast value when user presses the Antes button. If a record for the same
# user_id and date already exists, warn user
@dp.callback_query_handler(text=['AM'], state=Form.ask)
async def meds_am(call: types.CallbackQuery, state: FSMContext):
    date_time  =str(call.message.date).split()
    user_id = str(call.from_user.id)
    x = check_ask('MorningMeds', date_time, user_id, meal=None, meds='matutinas')
    if x[0] == 2:
        await Form.edam.set()
        await call.message.answer(x[1])
        await call.answer()
        await call.message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)
        await call.answer()
    elif x[0]==1:
        await Form.rwam.set()
        await call.message.answer(x[1], reply_markup=x[2])
@dp.callback_query_handler(text=['rewriteMorningMeds'],state=Form.rwam)
async def rewrite_meds_am(call: types.CallbackQuery, state:FSMContext):
    date_time = str(call.message.date).split()
    date = date_time[0]
    user_id = str(call.from_user.id)
    delete_record('MorningMeds', user_id,date)
    # Set new state
    await Form.ask.set()
    # Enter new info
    reply = write('MorningMeds', date_time, user_id, meal=None, meds='matutinas', value=None)
    # Ask for a value
    await call.message.answer('¡Listo! He eliminado tu registro anterior 🤖\n'+reply)
    await call.message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)
############## AM
# Register time for morning meds. If a record for the same
# user_id and date already exists, warn user
@dp.callback_query_handler(text=['AM'], state=Form.ask)
async def meds_am(call: types.CallbackQuery, state: FSMContext):
    date_time  =str(call.message.date).split()
    user_id = str(call.from_user.id)
    x = check_ask('MorningMeds', date_time, user_id, meal=None, meds='matutinas')
    if x[0] == 2:
        await Form.edam.set()
        await call.message.answer(x[1])
        await call.answer()
        await call.message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)
        await call.answer()
    elif x[0]==1:
        await Form.rwam.set()
        await call.message.answer(x[1], reply_markup=x[2])
@dp.callback_query_handler(text=['rewriteMorningMeds'],state=Form.rwam)
async def rewrite_meds_am(call: types.CallbackQuery, state:FSMContext):
    date_time = str(call.message.date).split()
    date = date_time[0]
    user_id = str(call.from_user.id)
    delete_record('MorningMeds', user_id,date)
    # Set new state
    await Form.ask.set()
    # Enter new info
    reply = write('MorningMeds', date_time, user_id, meal=None, meds='matutinas', value=None)
    # Ask for a value
    await call.message.answer('¡Listo! He eliminado tu registro anterior 🤖\n'+reply)
    await call.message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)
############## PM
# Register time for evening meds. If a record for the same
# user_id and date already exists, warn user
@dp.callback_query_handler(text=['PM'], state=Form.ask)
async def meds_pm(call: types.CallbackQuery, state: FSMContext):
    date_time  =str(call.message.date).split()
    user_id = str(call.from_user.id)
    x = check_ask('EveningMeds', date_time, user_id, meal=None, meds='nocturnas')
    if x[0] == 2:
        await Form.edpm.set()
        await call.message.answer(x[1])
        await call.message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)
    elif x[0]==1:
        await Form.rwpm.set()
        await call.message.answer(x[1], reply_markup=x[2])
@dp.callback_query_handler(text=['rewriteEveningMeds'],state=Form.rwpm)
async def rewrite_meds_pm(call: types.CallbackQuery, state:FSMContext):
    date_time = str(call.message.date).split()
    date = date_time[0]
    user_id = str(call.from_user.id)
    delete_record('EveningMeds', user_id, date)
    # Set new state
    await Form.ask.set()
    # Enter new info
    reply = write('EveningMeds', date_time, user_id, meal=None, meds='nocturnas', value=None)
    # Ask for a value
    await call.message.answer('¡Listo! He eliminado tu registro anterior 🤖\n'+reply)
    await call.message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)

################### MORE OPTIONS ##########################
###########################################################
butt12 = InlineKeyboardButton(text='Registrar manualmente', callback_data='manual')
butt14 = InlineKeyboardButton(text='Instrucciones y aviso de privacidad', callback_data='instr')
keyboard6 = InlineKeyboardMarkup().add(butt12).add(butt14)
@dp.callback_query_handler(text=['more'], state=Form.ask)
async def more_options_menu(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('Mis creadores también me enseñaron a realizar estas tareas 🤖', reply_markup=keyboard6)
@dp.callback_query_handler(text=['manual'], state=Form.ask)
async def manual_registration(call: types.CallbackQuery, state: FSMContext):
    # Reset state
    await Form.manual.set()
    await call.message.answer('Ingresa el nuevo registro con el siguiente formato:\nXX AAAA-MM-DD VALOR\n'
                              'Por ejemplo, si tuviste 100 de glucosa el 9 de mayo del 2023 antes del desayuno, escribe'
                              ' AD 2023-05-09 100\nUsa la siguiente lista de claves:\n'
                              'AD, DD: antes y después del desayuno\nAL, DL: antes y después de la comida\n'
                              'AC, DC: antes y después de la cena\nAM, PM: toma de medicinas matutinas y nocturnas\n'
                              'Para regresar, escribe /cancelar')
    await call.answer()
@dp.message_handler(commands=['cancelar'], state=Form.manual)
async def cancel_manual(message: types.Message):
    # Reset state
    await Form.ask.set()
    await message.answer('¿Con qué otra cosa te puedo ayudar?🤖', reply_markup=keyboard1)
@dp.message_handler(lambda message: check_manual(message.text)[1], state=Form.manual)
async def process_manual_registration(message: types.Message):
    await Form.ask.set()
    words = message.text.split()
    key = words[0]
    date = words[1]
    date_time = [date,'-']
    val = words[2]
    user_id = message.from_user.id
    d1 = { 'AD':'BeforeBreakfast', 'DD':'AfterBreakfast', 'AL':'BeforeLunch',
          'DL':'AfterLunch', 'AC':'BeforeDinner', 'DC':'AfterDinner', 'AM':'MorningMeds',
           'PM':'EveningMeds'}
    d2 = {'AD':'antes de desayunar', 'DD':'después de desayunar', 'AL':'antes de comer',
          'DL':'después de comer', 'AC':'antes de cenar', 'DC':'después de cenar', 'AM':'matutinas',
          'PM':'nocturnas'}
    table = d1[key]
    meal = None
    meds = None
    value = None
    if key=='AM':
        meds = d2[key]
        date_time[1] = val
    elif key=='PM':
        meds = d2[key]
        date_time[1] = val
    else:
        meal = d2[key]
        value = val
    reply = write(table, date_time, user_id, meal=meal, meds=meds, value=value)
    await message.answer(reply + ', ' + date)
    await message.answer('¿Con qué otra cosa te puedo ayudar?🤖', reply_markup=keyboard1)


@dp.message_handler(lambda message: not check_manual(message.text)[1], state=Form.manual)
async def deny_manual_registration(message: types.Message):
    reply = check_manual(message.text)[0]
    await Form.ask.set()
    await message.answer('Solicitud de registro rechazada. ' + reply + '\n¿Con qué'
                            ' otra cosa te puedo ayudar?🤖', reply_markup=keyboard1 )
executor.start_polling(dp)


