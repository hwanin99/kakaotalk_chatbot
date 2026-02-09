#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# 응답시간 초과시 먼저 답변
def timeover(msg="열심히 생성 중이에요!\n잠시만 기다려주세요."):
    response = {'version': '2.0', 'template': {
        'outputs': [
            {'simpleText': {'text': msg}}
        ],
        'quickReplies': [
            {
                'action': 'message',
                'label': '이미지 불러오기',
                'messageText': '이미지 불러오기'
            }
        ]
    }}
    
    return response

