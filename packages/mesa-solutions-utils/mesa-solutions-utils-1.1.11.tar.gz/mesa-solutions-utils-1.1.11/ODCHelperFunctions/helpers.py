import math
import smtplib
import ssl
from os.path import basename
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
import struct


def dictfetchall(cursor):
    "Return all rows from a cursor as a Python dictionary"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def build_email_message(message_object):
    """Creates message structure to pass to email

    Keyword arguments:
    message_object -- Dictionary that holds message information
    message = {
        'subject' : 'string',
        'from' : 'string',
        'to' : 'string',
        'text': 'string',
        'file': (csv file_type)
        }
    """
    message = MIMEMultipart()

    message["subject"] = message_object["subject"]
    message["from"] = message_object["from"]
    message["to"] = message_object["to"]

    text = message_object["text"]

    if text:
        message.attach(MIMEText(text))
    try:
        file = message_object['file']
        with open(file, "rb") as file_attachment:
            part = MIMEApplication(file_attachment.read(), Name=basename(file))
        part['Content-Disposition'] = f'attachment; filenames={basename(file)}'
        message.attach(part)
    except:
        print('No file found')

    return message


def send_email(smtp_config, message):
    """ Sends email to destination based off smtp_config

    Keyword arguments:
    smtp_config -- Dictionary that holds smpt account information
        smtp_config = {
            'username' : 'string',
            'password' : 'string',
            'server' : 'string',
            'port': int,
            }
    
    message - object returned from build_email_message
    """
    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_config['server'], smtp_config['port']) as server:
            server.starttls(context=context)
            server.login(user=smtp_config['username'], password=smtp_config['password'])
            server.sendmail(from_addr=message['from'], to_addrs=message['to'], msg=message.as_string())

def decode_analogs(analogs, analog_points, filter=[]):
    """ Returns decoded analog values from analog_bin
    Send in analogs (required from query: encode (ENCODE(mab.alg_bin::bytea,'hex'))) and points from mesard_analogs_combined (required: point, point name, unit, and point type)
    Optional value filter specifies the point(s) to be returned, if not specified, all points returned
    Returns the analogs sent in + bin alg str key (decoded points). If error = true, bin alg str point = 0, point name = ERROR, val = error code
    """
    try:
        j=0
        points = {}
        # index by point name and point number
        while j < len(analog_points):
            points[analog_points[j]['point']] = analog_points[j]
            j+=1
        
        # filter may be list of strings, make sure to fix type
        if (len(filter) > 0):
            filter = [int(i) for i in filter]
        
        # decode sent in binary analogs and return each point for the analog as well as any errors
        for row in analogs:
            status = decode_binary(row['encode'], points, filter)
            del row['encode']
            if(status[0] == 1):
                row['bin_decoded'] = status[1]
            else:
                row['bin_decoded'] = {'point': 0, 'point_name': 'ERROR', 'val': status[1], 'units': 'N/A'}
        return(analogs)
    except Exception as err:
        return(err)

def decode_binary(bin_alg_string, points, filter):
    try: 
        all_alg_vals = []
        i = 0
        while i < len(bin_alg_string):
            alg_id = int(bin_alg_string[i : i + 4], 16)
            # we indexed points by point number, so here we are getting the data type for a specific point. Need to know datatype to understand
                # how many bytes the info took up
            data_type = points[alg_id]["point_type"]
            if data_type == "float":
                interval = 12
                alg_value = convert_float(bin_alg_string[i + 4 : i + interval])[0]
                is_sentinel = __is_sentinel_f32(alg_value)
                i += interval
            elif data_type == "float64":
                interval = 20
                alg_value = convert_float(bin_alg_string[i + 4 : i + interval])[0]
                is_sentinel = __is_sentinel_f64(alg_value)
                i += interval
            else:
                interval = 12
                alg_value = int(bin_alg_string[i + 4 : i + interval], 16)
                is_sentinel = __is_sentinel_u32(alg_value)
                i += interval
            # if sentinel is true (error validating data) ignore data
            if (is_sentinel == False):
                # filter = [] means return all, else only return the points we want
                if (filter == []):
                    alg = {'point': alg_id, 'point_name': points[alg_id]['point_name'], 'point_label': points[alg_id]['point_label'], 'val': alg_value, 'units': points[alg_id]['unit']} 
                    all_alg_vals.append(alg)
                elif (alg_id in filter):
                    alg = {'point': alg_id, 'point_name': points[alg_id]['point_name'], 'point_label': points[alg_id]['point_label'], 'val': alg_value, 'units': points[alg_id]['unit']} 
                    all_alg_vals.append(alg)
        return 1, all_alg_vals
    except Exception as exception:
        # we dont want the function to stop if error, so we send in the error with all of the data
        return 3, exception

# is_sentinel functions are used for data validation
def __is_sentinel_u32(num):
    if num >= math.pow(2, 32) - 8 and num <= math.pow(2, 32) - 1:
        return True
    else:
        return False

def __is_sentinel_f32(num):
    f32_sent = math.pow(2, 127) * (2 - math.pow(2, -23))
    if num == f32_sent:
        return True
    else:
        return False

def __is_sentinel_f64(num):
    f32_sent = math.pow(2, 1023) * (2 - math.pow(2, -52))
    if num == f32_sent:
        return True
    else:
        return False

def convert_float(byte_string):
    buff = []
    buff.append(int(byte_string[0:2], 16))
    buff.append(int(byte_string[2:4], 16))
    buff.append(int(byte_string[4:6], 16))
    buff.append(int(byte_string[6:8], 16))
    buff = bytearray(buff)
    val = struct.unpack(">f", buff)
    return val