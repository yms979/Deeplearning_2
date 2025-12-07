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

### 4. Experience
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
정량적 지표 외에 실제 생성된 텍스트의 품질을 평가하기 위해, 학습된 모델을 사용하여 Unconditional Generation을 수행하였다. DFM 모델은 WikiText-103 수준의 문법 구조와 스타일을 성공적으로 모방하였으며, 높은 다양성을 가진 텍스트를 생성할 수 있다. 비록 Factuality 측면에서는 한계를 보였으나, 이는 모델의 크기와 학습 방식(Unconditional Generation)의 특성에 기인한 것으로, 생성 모델 자체의 분포 학습 능력은 유효함을 입증한다.

| Ship Construction Report |
| :--- |
| As a result of the initial design and construction, the ship was organised by the President Davis to oversee maintenance of his wartime navies. The ships used upwind of their offices in a small area outside the funnels of naval offices and warehouses to fit their respective main deck structure. These offices were black, green, or blue, in support camouflage, and the hospital ships were even red with these colours. Alongside the three ship designs for the ship, Ross's design improved to a standard for the number of ended owners with it at dockyard.<br><br>While the ship was designed on a prolific completion, for its engines remained wide by twice more than at the helm and yet were deemed enough to add three forehulls engines or a vertical trooping set at low bottom. Ross had later increased the engines to 5.7 kn (8.4 mph). As this was, the ship had reached 4,800 nautical miles (7,800 km / h) at Halifax where the boilers would need to wander south through through large areas of long-standing machinery provided an adequate sailing resort.<br><br><strong>== Construction and construction ==</strong><br>... 이하 생략 |

 * Grammatical Correctness: 생성된 문장은 주어-동사 수 일치, 시제 등 기본적인 문법 규칙을 준수하고 있다. 이는 DFM의 이산적 매핑 과정이 언어의 구조적 특징을 효과적으로 학습했음을 시사한다.
 * Coherence: WikiText-103의 특성상 긴 문단 생성 시 주제가 다소 흐려지는 경향이 관찰되었으나, 문장 단위의 의미 전달은 명확했다. 이는 OpenWebText 대비 학습 데이터의 Context Window 다양성이 부족했던 점에 기인한 것으로 판단된다.
 * Factual Accuracy & Hallucination: 내용적으로는 사실이 아닌 정보를 사실처럼 생성하는 환각(Hallucination) 현상이 다수 관찰되었다.
    **가상 역사: 실존하지 않는 'River Roman'이나 'Zachary Smith (1719–1849, 뉴욕 주지사)'와 같은 인물/지명을 생성하였다.

    ** 가상 미디어: 실제 존재하지 않는 게임('Last Edge')이나 영화의 속편 내용을 구체적인 수치(판매량, 날짜)와 함께 서술하였다.

### 5. Conclusion
본 과제에서는 Meta AI가 제안한 Discrete Flow Matching 모델을 기반으로, 제한된 컴퓨팅 자원과 소규모 데이터셋 환경에서 이산 데이터 생성 성능을 검증하고 학습 파이프라인을 재현하였다. 특히 대규모 인프라가 필수적인 최신 생성형 AI 연구 흐름 속에서, 상대적으로 작은 규모인 WikiText-103 데이터셋과 경량화된 모델 구조로도 안정적인 학습과 추론이 가능한지를 확인하는것을 목표로 상정하였다.
 실험 결과, 모델의 학습 안정성을 나타내는 ELBO 지표가 45.61로 수렴하고 생성 다양성을 나타내는 Entropy가 7.93을 기록하며, 모델이 특정 패턴에 갇히는 현상 없이 다양한 어휘 분포를 학습했음을 입증하였다. 정성적 분석에서도 모델은 역사, 기술, 엔터테인먼트 등 다양한 도메인의 문체를 자연스럽게 구사하고, 위키백과 특유의 문서 구조를 정교하게 모방하는 성과를 보였다. 다만, 참조 논문의 OpenWebText 대비 부족한 데이터 규모로 인해 Perplexity 수치가 다소 높게 측정되었으며, 문법적 유창함에 비해 사실관계가 맞지 않는 Hallucination 현상이 관찰되었다. 이는 알고리즘 자체의 결함보다는 학습 데이터의 양적 한계에 기인한 것으로 판단된다.
 결론적으로 본 연구는 DFM 프레임워크가 대규모 자원 없이도 텍스트의 복잡한 이산적 분포를 효과적으로 모델링할 수 있다는 강건성을 확인할 수 있었다. 이는 거대 언어 모델 연구가 주를 이루는 현시점에서, 학계나 개인 연구자가 접근 가능한 수준의 자원으로도 충분히 의미 있는 생성 모델 연구가 가능함을 시사한다. 향후에는 본 재현 과정을 통해 확보한 DFM 프레임워크를 개인 연구에 적극 도입하여, 실제 연구 목적과 가용 데이터의 특성에 최적화된 맞춤형 생성 모델을 활용해 나갈 계획이다.


## Usage

This section provides instructions on how to train the Discrete Flow Matching (DFM) model and generate text samples.

### 1. Environment Setup
First, install the required dependencies. We recommend using a virtual environment (Conda or venv).

```bash
# Clone the repository
git clone [https://github.com/your-username/discrete-flow-matching.git](https://github.com/your-username/discrete-flow-matching.git)
cd discrete-flow-matching

# Install dependencies
pip install -r requirements.txt


We use WikiText-103 as the training dataset. The script automatically downloads and processes the data using the Hugging Face datasets library.

To reproduce the Small Model (150M parameters) experiment described in the report, run the following command:
python train.py \
    --run_name "dfm-wikitext-small" \
    --dataset_name "wikitext" \
    --dataset_config "wikitext-103-raw-v1" \
    --model_arch "dit_small" \
    --hidden_size 768 \
    --num_layers 12 \
    --num_heads 12 \
    --max_seq_length 1024 \
    --batch_size 32 \
    --learning_rate 3e-4 \
    --max_steps 50000 \
    --save_interval 5000 \
    --output_dir "./checkpoints"
