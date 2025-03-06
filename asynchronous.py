# 응답시간 초과시 먼저 답변
def timeover():
    response = {'version': '2.0', 'template': {
        'outputs': [
            {
                'simpleText': {
                    'text': "앗 죄송합니다! 아직 생각 중이에요.\n잠시 후 아래 말풍선을 눌러주세요."
                }
            }
        ], 'quickReplies': [
            # 생각이 다 끝남? 버튼생성
            {
                'action': 'message',
                'label': '생각 다 했니?',
                'messageText': '생각 다 했니?'
            }
        ]
    }}
    return response
