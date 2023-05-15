from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from databasefunc_v2 import *
import re

def check_ask(table, date_time, user_id, meal=None, meds=None):
    #date_time = str(call.message.date).split()
    date = date_time[0]
    time = date_time[1]
    #user_id = str(call.from_user.id)
    if check_record(table, user_id, date) == True:
        cancel_butt = InlineKeyboardButton(text='Cancelar', callback_data='cancel')
        rewrite = InlineKeyboardButton(text='Reescribir', callback_data='rewrite'+table)
        new_keyboard = InlineKeyboardMarkup().add(cancel_butt, rewrite)
        old_record = retrieve(table, user_id,date)[0]
        if meal == None:
            # Message for meds
            reply = '🚨🚨🚨🚨\nYa existe el siguiente registro para toma de medicinas ' + meds +':\n' \
                    + str(old_record[2]) + ', hora: ' + str(old_record[3]) + \
                    '\n¿Quiere reescribir este registro?'
            #await call.message.answer(reply, reply_markup=new_keyboard)
        else:
            # Message for meals
            reply = '🚨🚨🚨🚨\nYa existe el siguiente registro ' + meal + ':\n' \
                    + str(old_record[2]) + ', valor: ' + str(old_record[4]) + \
                    ' mg/dl.' + '\n¿Quiere reescribir este registro?'
            #await call.message.answer(reply, reply_markup=new_keyboard)
        # Record already exists. This tells what state you have to set next depending on the meal
        return([1, reply, new_keyboard])
    else:
        if meds==None:
            #await call.message.answer('¿Cuál fue tu lectura ' + meal + '?')
            return([0, '', '']) #Meal record didn't exist. Ask for value
        else:
            write_to_db(table, user_id, date, time, value=None)
            reply = '¡Listo! Hice la siguiente anotación en mi base de datos 🤖\nTomaste' \
                    ' tus medicinas' + meds + ' a las ' + str(time)
            #await call.message.answer(reply)
            #await call.message.answer('¿Con qué te puedo ayudar?🤖', reply_markup=keyboard1)
            return([2, reply, '']) #Medicine record didn't exist. New record was written to the database
def write(table, date_time, user_id, meal=None, meds=None, value=None):
    date = date_time[0]
    time = date_time[1]
    write_to_db(table, user_id, date, time, value=value)
    # Message for meals
    if meds==None:
        reply = '¡Listo! Hice la siguiente anotación en ' \
                'mi base de datos 🤖\n' + str(date) + ', ' + str(value) + ' mg/dl ' + str(meal)
        return(reply)
    # Message for meds
    else:
        reply = 'Hice la siguiente anotación en mi base de datos 🤖\nTomaste' \
                ' tus medicinas ' + str(meds) + ' a las ' + str(time)
    return(reply)
# Check if a manual registry is well written
def check_manual(s:str):
    keys = ['AD', 'DD', 'AL','DL', 'AC', 'DC', 'AM', 'PM']
    words = s.split()
    if len(words) != 3:
        return(['Formato incorrecto',False])
    elif words[0].upper() not in keys:
        return(['Clave inválida',False])
    r1 = '[0-9]{4}[\-]([0]{1}[0-9]{1}|[1]{1}[0-2]{1})[\-]([0-2]{1}[0-9]{1}|[3]{1}[0,1]{1})'
    r2 = '[0-9:]+'
    if not re.match(r1, words[1]):
        return(['Formato de fecha incorrecto',False])
    elif not re.match(r2,words[2]):
        return(['Formato de valor/hora incorrecto',False])
    else:
        return(['Solicitud válida',True])
