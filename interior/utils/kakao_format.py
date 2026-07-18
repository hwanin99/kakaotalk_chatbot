# =========================================================
# 카카오 응답 포맷
# =========================================================
def textResponseFormat(bot_response):
    return {'version': '2.0', 'template': {
        'outputs': [{'simpleText': {'text': bot_response}}],
        'quickReplies': []
    }}


def imageResponseFormat(bot_response):
    return {'version': '2.0', 'template': {
        'outputs': [{'simpleImage': {'imageUrl': bot_response}}],
        'quickReplies': []
    }}


def imageWithTextFormat(image_url, alt_text, text):
    return {'version': '2.0', 'template': {
        'outputs': [
            {'simpleImage': {'imageUrl': image_url, 'altText': alt_text}},
            {'simpleText': {'text': text}}
        ]
    }}


def quickReplyFormat(text, label):
    return {'version': '2.0', 'template': {
        'outputs': [{'simpleText': {'text': text}}],
        'quickReplies': [
            {'action': 'message', 'label': label, 'messageText': label}
        ]
    }}


def timeover(msg="열심히 생성 중이에요!\n잠시만 기다려주세요."):
    return {'version': '2.0', 'template': {
        'outputs': [{'simpleText': {'text': msg}}],
        'quickReplies': [
            {'action': 'message', 'label': '이미지 불러오기', 'messageText': '이미지 불러오기'}
        ]
    }}
