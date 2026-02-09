# <p align = "center"> OpenAI API를 이용한 카카오톡 챗봇 </p>
* 기존 방식은 ChatGPT와 DALL·E 3를 사용하였다.
  * 이는 다음과 같은 단점들이 존재했다.  
> 1. 두 모델 모두 텍스트 프롬프트를 입력으로 받기 때문에, 경우를 나누어 입력 프롬프트를 받아야 한다.
> 2. DALL·E 3 모델은 텍스트 프롬프트 기반의 이미지 생성만을 지원한다.  
>     * 즉, 생성된 이미지의 유사성을 기대할 수 없으며, 이미지 편집 또한 불가능하다.

<br>
  
$\rightarrow$ 따라서, gpt-4.1 모델을 이용하여, 위 문제점들을 해결하였다. 
> * 이미지를 입력받을 수 있기에, 이미지 출력과의 구조적 유사성을 유지할 수 있다.
> * 또한, 입력 이미지에 대한 설명 캡션을 텍스트 프롬프트로 사용하여, 출력 이미지와의 연관성을 강화할 수 있다.

---
``` bash
interior/
├── utils/
│   ├── image_generator.py    # image_generator 함수
│   ├── asynchronous.py       # 비동기 처리를 위한 timeover 함수
│   └── kakao_response.py     # 카카오톡 챗봇 형식으로 변환하기 위한 함수
├── main.py                   # Lambda handler 함수
└── README.md
```
---
### 작동 원리 및 사용 예시
![그림123](https://github.com/user-attachments/assets/cdd0375d-e336-4bc6-ba92-dac2a5c39f03)

---
### 주요 처리 흐름
1. 입력 이미지 분석 (gpt-4.1-mini)
   > * 입력받은 평면도 이미지의 공간 구조와 배치를 설명하는 간단한 텍스트 캡션을 생성한다.
2. 이미지 생성 (gpt-4.1)
   > * 입력
   >   * "원본 이미지 + 텍스트 캡션 + 인테리어 스타일"
   > * 출력
   >   * 원본 구조를 유지한 상태에서 요청한 인테리어 스타일로 생성된 이미지
3. 이미지 전달 방식
   > * 생성된 이미지를 AWS S3에 업로드하고, 해당 URL을 카카오톡 챗봇의 이미지 응답으로 전달한다.
</br>

### 챗봇 상태 관리 및 함수 구성
1. image_generator 함수
   > * 이미지 처리의 전체 과정을 하나의 함수로 구성하여 end-to-end 파이프라인으로 실행한다.
   > * "이미지 설명 생성 $\rightarrow$ 이미지 생성 $\rightarrow$ S3 업로드 $\rightarrow$ URL 반환"
   > * Ex) image_generator(image_url, style)
2. botlog.txt 상태 관리
   > * 챗봇의 대화 흐름 관리를 위해 botlog.txt를 사용하여 현재 상태를 저장 및 갱신한다.
   > * 저장된 상태를 기반으로 다음 처리 단계를 분기하고, 함수 입력으로 활용한다.
   > * Ex) {START,,,} $\rightarrow$ ... $\rightarrow$ {DONE,image_url,style,image_url_s3}
