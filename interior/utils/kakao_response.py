#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# 카카오채널에 메세지 전송
def textResponseFormat(bot_response):
    response = {'version': '2.0', 'template': {
        'outputs': [{'simpleText': {'text': bot_response}}],
        'quickReplies': []
    }}
    return response


def imageResponseFormat(bot_response):
    response = {'version': '2.0', 'template': {
        'outputs': [{'simpleImage': {'imageUrl': bot_response}}],
        'quickReplies': []
    }}
    return response

