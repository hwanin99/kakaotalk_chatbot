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
│   ├── responseOpenAI.py     # 전체 응답 함수
│   └── kakao_response.py     # 카카오톡 챗봇 형식으로 변환하기 위한 함수
├── lambda_handler.py                   # 메인 Lambda handler 함수
└── README.md
```
---
### 작동 원리 및 사용 예시
<p align="center">
  <img src="https://github.com/user-attachments/assets/66255e58-9aed-432d-afa7-322ce69fc8a5" height="350" />
  <img src="https://github.com/user-attachments/assets/b9af3d09-8b11-4122-9cb3-12e3bf9f622a" height="350" />
</p>

---
### 주요 처리 흐름
1. 입력 이미지 분석 (GPT-4.1-mini)
   > * 입력된 평면도 이미지를 분석하여 공간 구조, 방 배치, 주요 특징을 설명하는 이미지 캡션을 생성한다.
   > * 이미지에 대한 캡션을 포함하지 않은 프롬프트는 성능이 확연히 떨어짐을 확인할 수 있었다.
   > * <img width="1862" height="989" alt="image" src="https://github.com/user-attachments/assets/20a6e5fc-c636-4229-a543-3e6c5e54adbf" />

2. 인테리어 이미지 생성 (GPT-4.1)
   > * 입력
   >   * "원본 평면도 이미지"
   >   * "이미지 캡션"
   >   * "사용자 입력 인테리어 스타일"
   > * 출력
   >   * 원본 공간 구조를 유지하면서 요청한 인테리어 스타일이 적용된 이미지
   >   * <img width="1163" height="247" alt="image" src="https://github.com/user-attachments/assets/2f2202a4-8962-43ae-84cd-04580fd9143d" />

3. 생성 이미지 전달
   > * 생성된 이미지를 AWS S3에 업로드한 후, 업로드된 이미지의 URL을 카카오톡 챗봇을 통해 사용자에게 전달한다.
</br>

### 챗봇 상태 관리 및 함수 구성
1. image_generate() 함수
   > * 이미지 생성에 필요한 전체 과정을 하나의 함수로 구성하여 End-to-End 파이프라인으로 수행한다.
   > * 처리 순서
   >   * "이미지 캡션 생성 $\rightarrow$ 이미지 생성 $\rightarrow$ AWS S3 업로드 $\rightarrow$ 이미지 URL 반환"
   > * 예시  
   >   * image_generator(image_url, style, user_id)

2. S3 기반 상태(State) 관리
   > * 사용자별 상태 정보를 S3에 저장하여 대화 진행 상태를 관리한다.
   > * 저장된 상태(State)를 기반으로 현재 대화 단계를 판단하고, 다음 처리 로직을 수행한다.
   > * 이미지 생성 진행 상태(GENERATING), 완료(DONE), 실패(ERROR)를 관리하여 비동기 이미지 생성 과정을 처리한다.
   > * 상태 예시
   >   * {START,,,} $\rightarrow$ ... $\rightarrow$ {DONE,image_url,style,image_url_s3}
