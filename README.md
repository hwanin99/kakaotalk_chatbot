## OpenAI API로 ChatGPT와 DALLE-2를 가져와 카카오톡 챗봇 만들기
### 작동원리
1. 카카오톡에 prompt 입력
2. AWS API Gateway를 통해 AWS Lambda 함수로 전달
3. AWS Lambda 함수에서 OpenAI API를 통해 ChatGPT/DALLE-2에게 입력 prompt에 대한 응답을 받는다.
![image](https://github.com/user-attachments/assets/0f5e915b-cdd0-4f70-9432-7e49def8966b)
---
### 주요사항
* 응답을 카카오톡 챗봇의 형식에 맞게 변환 (json 형식)
* DALLE-2는 한국어를 잘 이해하지 못하므로, 입력받은 prompt를 영어로 변역해서 받아야 한다.
* DALLE-2는 응답을 내보내는데 대부분 5초 이상이 소요된다. 그러나, 카카오톡 챗봇은 5초 이상 응답이 없으면 에러를 반환한다.
  * 이를 해결하기 위해, 비동기 처리를 해야 한다.
