import numpy as np
import pandas as pd
import re

thai_area_code = {
    "02": "Bangkok (Krung Thep Maha Nakhon), Nonthaburi, Pathum Thani, Samut Prakan, Phutthamonthon (Nakhon Pathom)",
    "032": "Phetchaburi, Prachuap Khiri Khan, Ratchaburi",
    "034": "Kanchanaburi, Nakhon Pathom (except Phutthamonthon), Samut Sakhon, Samut Songkhram",
    "035": "Ang Thong, Phra Nakhon Si Ayutthaya, Suphan Buri",
    "036": "Lop Buri, Saraburi, Sing Buri",
    "037": "Nakhon Nayok, Prachin Buri, Sa Kaeo",
    "038": "Chachoengsao, Chon Buri, Rayong",
    "039": "Chanthaburi, Trat",
    "042": "Bueng Kan, Loei, Mukdahan, Nakhon Phanom, Nong Bua Lamphu, Nong Khai, Sakon Nakhon, Udon Thani",
    "043": "Kalasin, Khon Kaen, Maha Sarakham, Roi Et, Nam Nao (Phetchabun)",
    "044": "Buri Ram, Chaiyaphum, Nakhon Ratchasima, Surin",
    "045": "Amnat Charoen, Si Sa Ket, Ubon Ratchathani, Yasothon",
    "052": "Chiang Mai, Chiang Rai, Lamphun, Mae Hong Son",
    "053": "Chiang Mai, Chiang Rai, Lamphun, Mae Hong Son",
    "054": "Lampang, Nan, Phayao, Phrae",
    "055": "Kamphaeng Phet, Phitsanulok, Sukhothai, Tak, Uttaradit, Sam Ngam, Wachirabarami (Phichit)",
    "056": "Chai Nat, Nakhon Sawan, Phetchabun (except Nam Nao), Phichit (except Sam Ngam & Wachirabarami), Uthai Thani",
    "073": "Narathiwat, Pattani, Yala",
    "074": "Phatthalung, Satun, Songkhla",
    "075": "Krabi, Nakhon Si Thammarat, Trang",
    "076": "Phang Nga, Phuket",
    "077": "Chumphon, Ranong, Surat Thani",
}

phone_list_bkk = ["02"]
phone_list_nonbkk = [k for k, v in thai_area_code.items() if k != "02"]
phone_list_mobile = [
    "060",
    "061",
    "062",
    "063",
    "064",
    "065",
    "066",
    "068",
    "080",
    "081",
    "082",
    "083",
    "084",
    "085",
    "086",
    "087",
    "088",
    "089",
    "090",
    "091",
    "092",
    "093",
    "094",
    "095",
    "096",
    "097",
    "098",
    "099",
    "099 ",
]


def get_possible_extension(text):
    non_mobile = text[:9]
    if is_bkk_office_number(non_mobile) or is_nonbkk_office_number(non_mobile):
        ext = text[9:]
        return ext
    else:
        return ""


def prepare_phone_out(phone_no_extension, extension):
    if len(extension) > 0:
        return f"{phone_no_extension}-{extension}"
    else:
        return phone_no_extension


def add_leading_zero(text):
    if ((len(text) == 9) or (len(text) == 8)) and (text[0] != "0"):
        return f"0{text}"
    else:
        return text


def update_old_mobile(text):
    leading = "08"
    num = text[1:]
    return f"{leading}{num}"


def keep_only_number(text):
    txt = re.sub("[^0-9.]+", "", text)
    return txt


def remove_66(txt):
    if is_phone_with66(txt):
        txt = txt.replace("66", "", 1)
        return txt
    else:
        return txt


def finalize_phone(text, extension):
    num_extension = len(extension)
    if has_extension(num_extension):
        phone_no_extension = text[:-num_extension]
    else:
        phone_no_extension = text
    if is_bkk_office_number(phone_no_extension):
        phone_type = "office"
        phone_num = prepare_phone_out(phone_no_extension, extension)
    elif is_nonbkk_office_number(phone_no_extension):
        phone_type = "office"
        phone_num = prepare_phone_out(phone_no_extension, extension)
    elif is_mobile_number(text):
        phone_type = "mobile"
        phone_num = text
    elif is_old_mobile_number(text):
        phone_type = "mobile"
        phone_num = update_old_mobile(text)
    else:
        phone_type = "other"
        phone_num = np.nan
    return phone_type, phone_num


def is_old_mobile_number(text):
    old_nums = ["09", "01"]
    if (text[:2] in old_nums) and (len(text) == 9):
        return True
    else:
        return False


def is_mobile_number(text):
    if (text[:3] in phone_list_mobile) and (len(text) == 10):
        return True
    else:
        return False


def is_nonbkk_office_number(text):
    if (text[:3] in phone_list_nonbkk) and (len(text) == 9):
        return True
    else:
        return False


def is_bkk_office_number(text):
    if (text[:2] == "02") and (len(text) == 9):
        return True
    else:
        return False


def is_phone_with66(text):
    if (text[:2] == "66") and (len(text) == 11):
        return True
    elif (text[:2] == "66") and (len(text) == 10):
        return True
    else:
        return False


def has_extension(n):
    if n > 0:
        return True
    else:
        return False


def try_convert_as_int(x):
    try:
        output = str(int(float(x)))
    except Exception as e:
        print(f"failed to convert {x} to float>int>str")
        return ""
    else:
        return output


def format_phone(col):
    phone_type, phone_num = "other", np.nan
    if pd.isna(col):
        return phone_type, phone_num

    text = str(col).strip()
    text = keep_only_number(text)
    text = remove_66(text)
    text = try_convert_as_int(text)
    if len(text) < 7:
        return phone_type, phone_num
    text = add_leading_zero(text)
    ext = get_possible_extension(text)
    phone_type, phone_num = finalize_phone(text, ext)
    return phone_type, phone_num


if __name__ == "__main__":
    input_val = 943350770
    print(f"Input {input_val}",format_phone(943350770))
    
    input_val = "09-4597386"
    print(f"Input {input_val}",format_phone("09-4597386"))
    
    input_val = "01-3636342"
    print(f"Input {input_val}",format_phone("01-3636342"))
    
    input_val = "05-1622430"
    print(f"Input {input_val}",format_phone("05-1622430"))

    
    input_val = "0231531447128"
    print(f"Input {input_val}",format_phone("0231531447128"))
    
    input_val = " "
    print(f"Input {input_val}",format_phone(" "))
    
    input_val = None
    print(f"Input {input_val}",format_phone(None))
    
    input_val = "02-7205978-87"
    print(f"Input {input_val}",format_phone("02-7205978-87"))
    
    input_val = "022482000 160"
    print(f"Input {input_val}",format_phone("022482000 160"))
    # bad one
    
    input_val = "6683ฮ091545"
    print(f"Input {input_val}",format_phone("6683ฮ091545"))
    # mobile
    
    input_val = "66830091545"
    print(f"Input {input_val}",format_phone("66830091545"))
    
    input_val = "+66830091545"
    print(f"Input {input_val}",format_phone("+66830091545"))
    
    input_val = "083-009-1545"
    print(f"Input {input_val}",format_phone("083-009-1545"))
    
    input_val = "83-009-1545"
    print(f"Input {input_val}",format_phone("83-009-1545"))
    
    input_val = "+830091545"
    print(f"Input {input_val}",format_phone("+830091545"))
    # bkk
    
    input_val = "6625377653"
    print(f"Input {input_val}",format_phone("6625377653"))
    
    input_val = "+6625377653"
    print(f"Input {input_val}",format_phone("+6625377653"))
    
    input_val = "02-537-7653"
    print(f"Input {input_val}",format_phone("02-537-7653"))
    
    input_val = "2-537-7653"
    print(f"Input {input_val}",format_phone("2-537-7653"))
    
    input_val = "+25377653"
    print(f"Input {input_val}",format_phone("+25377653"))
    # non-bkk
    
    input_val = "6635343240"
    print(f"Input {input_val}",format_phone("6635343240"))
    
    input_val = "+6635343240"
    print(f"Input {input_val}",format_phone("+6635343240"))
    
    input_val = "03-534-3240"
    print(f"Input {input_val}",format_phone("03-534-3240"))
    
    input_val = "3-534-3240"
    print(f"Input {input_val}",format_phone("3-534-3240"))
    
    input_val = "+35343240"
    print(f"Input {input_val}",format_phone("+35343240"))
