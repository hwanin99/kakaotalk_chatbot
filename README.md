<div align=center>
 
## OpenAI API로 ChatGPT와 DALLE-2를 가져와 카카오톡 챗봇 만들기
<a href="https://hwan-data.tistory.com/entry/ChatGPT-DALLE2-API%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%98%EC%97%AC-%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5-%EC%B9%B4%EC%B9%B4%EC%98%A4%EC%B1%97%EB%B4%87-%EB%A7%8C%EB%93%A4%EA%B8%B0"><img src="https://img.shields.io/badge/Blog-d14836?style=flat-square&logo=Tistory&logoColor=white&link=https://hwan-data.tistory.com/entry/ChatGPT-DALLE2-API%EB%A5%BC-%ED%99%9C%EC%9A%A9%ED%95%98%EC%97%AC-%EC%9D%B8%EA%B3%B5%EC%A7%80%EB%8A%A5-%EC%B9%B4%EC%B9%B4%EC%98%A4%EC%B1%97%EB%B4%87-%EB%A7%8C%EB%93%A4%EA%B8%B0"/></a> 

<img src="https://github.com/user-attachments/assets/0f5e915b-cdd0-4f70-9432-7e49def8966b" width="70%" height="70%"/>
</div>

<br>

>1. 카카오톡에 prompt 입력
>2. AWS API Gateway를 통해 AWS Lambda 함수로 전달
>3. AWS Lambda 함수에서 OpenAI API를 통해 ChatGPT/DALLE-2에게 입력 prompt에 대한 응답을 받는다.
</div>

---
### 주요사항
* 응답을 카카오톡 챗봇의 형식에 맞게 변환 (json 형식)
* DALLE-2는 한국어를 잘 이해하지 못하므로, 입력받은 prompt를 영어로 변역해서 받아야 한다.
* DALLE-2는 응답을 내보내는데 대부분 5초 이상이 소요된다. 그러나, 카카오톡 챗봇은 5초 이상 응답이 없으면 에러를 반환한다.
  * 이를 해결하기 위해, 비동기 처리를 해야 한다.
