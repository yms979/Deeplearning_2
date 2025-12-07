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

### 4. Result
#### 4.1 Quantitative Analysis
데이터셋의 규모 차이(WikiText-103 vs OpenWebText)로 인해 언어 모델의 일반화 성능 지표인 PPL은 다소 높았지만, Entropy와 ELBO 측면에서는 본 재현 실험이 논문의 성과를 충분히 뒷받침하고 있음을 확인하였다. 특히 소규모 데이터셋 환경에서도 모델이 Mode Collapse없이 안정적으로 학습됨을 입증하였다.

| Metric | **Ours** (WikiText-103) | **Reference** (OpenWebText) | **Performance Analysis** |
| :--- | :---: | :---: | :--- |
| **Entropy** | **7.93** | 7.7 (Avg.) | **Superior Diversity (+0.23)** |
| **ELBO** | **45.61** | 53.2 | **Better Convergence (-7.59)** |
| **Perplexity** | 187.29 | 128.9 | Expected gap due to data scale |

 * Elbo(Evidence Lower Bound): 본 실험 결과를 통하여 도출한 Elbo 값은 논문에 나온 수치(53.2)와 유사했다. 모델의 규모와 데이터셋의 차이가 있음에도 DFM의 Loss 최적화 성능이 재현되었음을 알 수 있었다.
 * Perplexity(PPL): 참조 모델(128.9-132.2)보다 다소 높게 측정되었다. 이는 WikiText 데이터셋의 규모가 OpenWebText보다 작아 모델의 일반화 성능이 상대적으로 낮게 측정된 것으로 보인다.
 * Entropy: 측정된 Entropy(7.93)은 논문에서 언급한 "Entropy >=6일 때 다양한 텍스트가 생성된다."는 기준을 충족한다. 이는 모델이 특정 토큰만을 생성하는 "Collapse" 현상 없이 다양한 어휘를 사용하고 있음을 알 수 있다.

#### 4.2 Qualitative Analysis
정량적 지표 외에 실제 생성된 텍스트의 품질을 평가하기 위해, 학습된 모델을 사용하여 Unconditional Generation을 수행하였다.

| Ship Construction Report |
| :--- |
| As a result of the initial design and construction, the ship was organised by the President Davis to oversee maintenance of his wartime navies. The ships used upwind of their offices in a small area outside the funnels of naval offices and warehouses to fit their respective main deck structure. These offices were black, green, or blue, in support camouflage, and the hospital ships were even red with these colours. Alongside the three ship designs for the ship, Ross's design improved to a standard for the number of ended owners with it at dockyard.<br><br>While the ship was designed on a prolific completion, for its engines remained wide by twice more than at the helm and yet were deemed enough to add three forehulls engines or a vertical trooping set at low bottom. Ross had later increased the engines to 5.7 kn (8.4 mph). As this was, the ship had reached 4,800 nautical miles (7,800 km / h) at Halifax where the boilers would need to wander south through through large areas of long-standing machinery provided an adequate sailing resort.<br><br><strong>== Construction and construction ==</strong><br>... 이하 생략 |
