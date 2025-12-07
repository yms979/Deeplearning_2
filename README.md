## Discrete Flow Matching (DFM) 재현 실험 보고서
### 1. Introduction
생성형 ai분야에서 flow matching과 diffusion 모델이 연속적인 데이터 생성에서 높은 성능을 보여주었다. 하지만 텍스트와 같은 이산적(discrete) 데이터에 대한 적용은 낮은 성능과 느린 생성 시간이라는 단점을 가지고 있었다. 본 과제에서는 Meta AI가 Nuerips에서 제안한 discrete flow matching(DFM) 논문을 기반으로, 이산 데이터 생성을 위한 flow matching 프레임워크를 재현하고 검증한 결과를 보여주고 한다.

### 2. Purpose
본 과제를 수행하며 달성하고자 하는 목적는 두가지이다. 첫째는 DFM 모델의 학습-추론 과정을 재현하는 것이다. 이를 통해 추후 개인 연구에 DFM 모델을 활용하고자 한다. 둘째는 데이터 셋 변화에 따른 강건성 평가를 수행하고자 한다. 논문에서 제안한 모델과 데이터의 규모가 개인 실험에 활용하기엔 규모가 크다. 이에 개인이 활용가능한 자원(resource)에서도 작동하는 소규모 모델과 상대적으로 작은 규모의 데이터셋(wikiText-103)에서도 준수한 성능과 학습 안정성을 보이는 지 확인하고자 한다.

### 3. Experimantal Setup
목적을 달성하기 위해 논문의 실험 설정을 기반으로 하되, 컴퓨티 자원과 데이터 셋의 제약을 고려하여 다음과 같이 환경을 구성하였다.
  * Model Architecture: 논문의 Small Model(150M parameters, DiT acrchitecture) 설정을 참조하여 구성
  * Dataset: Wiki-103 (학과 서버의 용량 부족으로 인하여 OpenWebText를 다운 받지 못하였음)
  * Source Distribution: Masked Modeling (업로드된 참조 텍스트의 Mask 설정과 비교하기 위하 다음과 같이 설정하였다.)
  * Training Objective: 논문에서 정의된 Cross-Entropy 기반의 Posterior 학습 loss

### 4. Quantitative Analysis
Metric,User Result (WikiText),Reference (Facebook - Linear/Mask),Note
ELBO,45.61,53.2,학습 수렴도 지표
Perplexity (PPL),187.29,128.9,낮을수록 좋음
Entropy,7.93,N/A,다양성 지표 (≥6 권장)
