import segno
import base64
from io import BytesIO

def generate_lesion_qr(lesion):
    info = f"Распад №{lesion.lesion_id}\nПрошло времени: {lesion.pass_time}\n\n"
    info += "Состав распада:\n"
    for helplesion in lesion.lesion_helps.all():
        help = helplesion.help
        info += f"{help.name}\n"
        info += f"\tКоличество: {helplesion.quantity}\n"
        info += f"\tОставшееся количество: {helplesion.remaining_quantity}\n"
    qr = segno.make(info)
    buffer = BytesIO()
    qr.save(buffer, kind='png')
    buffer.seek(0)
    qr_image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return qr_image_base64