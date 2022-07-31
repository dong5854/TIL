#-*- coding: utf-8 -*-
from collections import Counter
from collections import defaultdict
from scipy.sparse import csr_matrix
import numpy as np
from sklearn.preprocessing import normalize
from konlpy.tag import Komoran
import crawling
from crawling.textrank import KeywordSummarizer
from crawling.textrank import KeysentenceSummarizer

sents = [
  '오패산터널 총격전 용의자 검거 서울 연합뉴스 경찰 관계자들이 19일 오후 서울 강북구 오패산 터널 인근에서 사제 총기를 발사해 경찰을 살해한 용의자 성모씨를 검거하고 있다 성씨는 검거 당시 서바이벌 게임에서 쓰는 방탄조끼에 헬멧까지 착용한 상태였다', 
  '서울 연합뉴스 김은경 기자 사제 총기로 경찰을 살해한`인 성모 46 씨는 주도면밀했다', 
  '경찰에 따르면 성씨는 19일 오후 강북경찰서 인근 부동산 업소 밖에서 부동산업자 이모 67 씨가 나오기를 기다렸다 이씨와는 평소에도 말다툼을 자주 한 것으로 알려졌다', 
  '이씨가 나와 걷기 시작하자 성씨는 따라가면서 미리 준비해온 사제 총기를 이씨에게 발사했다 총알이 빗나가면서 이씨는 도망갔다 그 빗나간 총알은 지나가던 행인 71 씨의 배를 스쳤다', 
  '성씨는 강북서 인근 치킨집까지 이씨 뒤를 쫓으며 실랑이하다 쓰러뜨린 후 총기와 함께 가져온 망치로 이씨 머리를 때렸다', 
  '이 과정에서 오후 6시 20분께 강북구 번동 길 위에서 사람들이 싸우고 있다 총소리가 났다 는 등의 신고가 여러건 들어왔다', 
  '5분 후에 성씨의 전자발찌가 훼손됐다는 신고가 보호관찰소 시스템을 통해 들어왔다 성범죄자로 전자발찌를 차고 있던 성씨는 부엌칼로 직접 자신의 발찌를 끊었다', 
  '용의자 소지 사제총기 2정 서울 연합뉴스 임헌정 기자 서울 시내에서 폭행 용의자가 현장 조사를 벌이던 경찰관에게 사제총기를 발사해 경찰관이 숨졌다 19일 오후 6시28분 강북구 번동에서 둔기로 맞았다 는 폭행 피해 신고가 접수돼 현장에서 조사하던 강북경찰서 번동파출소 소속 김모 54 경위가 폭행 용의자 성모씨가 쏜 사제총기에 맞고 쓰러진 뒤 병원에 옮겨졌으나 숨졌다 사진은 용의자가 소지한 사제총기', 
  '신고를 받고 번동파출소에서 김창호 54 경위 등 경찰들이 오후 6시 29분께 현장으로 출동했다 성씨는 그사이 부동산 앞에 놓아뒀던 가방을 챙겨 오패산 쪽으로 도망간 후였다', 
  '김 경위는 오패산 터널 입구 오른쪽의 급경사에서 성씨에게 접근하다가 오후 6시 33분께 풀숲에 숨은 성씨가 허공에 난사한 10여발의 총알 중 일부를 왼쪽 어깨 뒷부분에 맞고 쓰러졌다', 
  '김 경위는 구급차가 도착했을 때 이미 의식이 없었고 심폐소생술을 하며 병원으로 옮겨졌으나 총알이 폐를 훼손해 오후 7시 40분께 사망했다', 
  '김 경위는 외근용 조끼를 입고 있었으나 총알을 막기에는 역부족이었다', 
  '머리에 부상을 입은 이씨도 함께 병원으로 이송됐으나 생명에는 지장이 없는 것으로 알려졌다', 
  '성씨는 오패산 터널 밑쪽 숲에서 오후 6시 45분께 잡혔다', 
  '총격현장 수색하는 경찰들 서울 연합뉴스 이효석 기자 19일 오후 서울 강북구 오패산 터널 인근에서 경찰들이 폭행 용의자가 사제총기를 발사해 경찰관이 사망한 사건을 조사 하고 있다', 
  '총 때문에 쫓던 경관들과 민간인들이 몸을 숨겼는데 인근 신발가게 직원 이모씨가 다가가 성씨를 덮쳤고 이어 현장에 있던 다른 상인들과 경찰이 가세해 체포했다', 
  '성씨는 경찰에 붙잡힌 직후 나 자살하려고 한 거다 맞아 죽어도 괜찮다 고 말한 것으로 전해졌다', 
  '성씨 자신도 경찰이 발사한 공포탄 1발 실탄 3발 중 실탄 1발을 배에 맞았으나 방탄조끼를 입은 상태여서 부상하지는 않았다', 
  '경찰은 인근을 수색해 성씨가 만든 사제총 16정과 칼 7개를 압수했다 실제 폭발할지는 알 수 없는 요구르트병에 무언가를 채워두고 심지를 꽂은 사제 폭탄도 발견됐다', 
  '일부는 숲에서 발견됐고 일부는 성씨가 소지한 가방 안에 있었다'
]

def keywords(sents):
    
    komoran = Komoran()
    def komoran_tokenize(sent):
        words = komoran.pos(sent, join=True)
        words = [w for w in words if ('/NN' in w or '/XR' in w or '/VA' in w or '/VV' in w)]
        return words

    keyword_extractor = KeywordSummarizer(
        tokenize = komoran_tokenize,
        window = -1,
        verbose = False
    )

    keywords = keyword_extractor.summarize(sents, topk=30)

    #중요한 단어일수록 점수 높음!
    #def komoran_tokenize(sent):
    #    return komoran.pos(sent, join=True)

    #keyword_extractor = KeywordSummarizer(tokenize = komoran_tokenize, window = -1)
    #keywords = keyword_extractor.summarize(sents, topk=30)

    #이상한 ㄴ같은거 걸러냄
    def komoran_tokenize(sent):
        words = komoran.pos(sent, join=True)
        words = [w for w in words if ('/NN' in w or '/XR' in w or '/VA' in w or '/VV' in w)]
        return words

    keyword_extractor = KeywordSummarizer(tokenize = komoran_tokenize, window = 2)
    keywords = keyword_extractor.summarize(sents, topk=30)

    #키워드로 이끌어낸 keysents
    summarizer = KeysentenceSummarizer(tokenize = komoran_tokenize, min_sim = 0.3)
    keysents = summarizer.summarize(sents, topk=2)
    #print(keywords)

    #문장위치로 중요도 다르게 설정
    bias = np.ones(len(sents))
    bias[-1] = 10
    keysents = summarizer.summarize(sents, topk=3, bias=bias)


    #단어그래프 만들기위해
    def scan_vocabulary(sents, tokenize, min_count=2):
        counter = Counter(w for sent in sents for w in tokenize(sent))
        counter = {w:c for w,c in counter.items() if c >= min_count}
        idx_to_vocab = [w for w, _ in sorted(counter.items(), key=lambda x:-x[1])]
        vocab_to_idx = {vocab:idx for idx, vocab in enumerate(idx_to_vocab)}
        return idx_to_vocab, vocab_to_idx

    #두 단어 간의 유사도 정의를 위해
    def cooccurrence(tokens, vocab_to_idx, window=2, min_cooccurrence=2):
        counter = defaultdict(int)
        for s, tokens_i in enumerate(tokens):
            vocabs = [vocab_to_idx[w] for w in tokens_i if w in vocab_to_idx]
            n = len(vocabs)
            for i, v in enumerate(vocabs):
                if window <= 0:
                    b, e = 0, n
                else:
                    b = max(0, i - window)
                    e = min(i + window, n)
                for j in range(b, e):
                    if i == j:
                        continue
                    counter[(v, vocabs[j])] += 1
                    counter[(vocabs[j], v)] += 1
        counter = {k:v for k,v in counter.items() if v >= min_cooccurrence}
        n_vocabs = len(vocab_to_idx)
        return dict_to_mat(counter, n_vocabs, n_vocabs)

    def dict_to_mat(d, n_rows, n_cols):
        rows, cols, data = [], [], []
        for (i, j), v in d.items():
            rows.append(i)
            cols.append(j)
            data.append(v)
        return csr_matrix((data, (rows, cols)), shape=(n_rows, n_cols))

    #불필요한 단어 제거하기 위해
    def word_graph(sents, tokenize=None, min_count=2, window=2, min_cooccurrence=2):
        idx_to_vocab, vocab_to_idx = scan_vocabulary(sents, tokenize, min_count)
        tokens = [tokenize(sent) for sent in sents]
        g = cooccurrence(tokens, vocab_to_idx, window, min_cooccurrence)
        return g, idx_to_vocab

    #pagerank를 학습하는 함수
    def pagerank(x, df=0.85, max_iter=30):
        assert 0 < df < 1

        # initialize
        A = normalize(x, axis=0, norm='l1')
        R = np.ones(A.shape[0]).reshape(-1,1)
        bias = (1 - df) * np.ones(A.shape[0]).reshape(-1,1)

        # iteration
        for _ in range(max_iter):
            R = df * (A * R) + bias

        return R

    def textrank_keyword(sents, tokenize, min_count, window, min_cooccurrence, df=0.85, max_iter=30, topk=30):
        g, idx_to_vocab = word_graph(sents, tokenize, min_count, window, min_cooccurrence)
        R = pagerank(g, df, max_iter).reshape(-1)
        idxs = R.argsort()[-topk:]
        keywords = [(idx_to_vocab[idx], R[idx]) for idx in reversed(idxs)]
        return keywords

    keywords_l = []
    for i in keywords:
        k = i[0].split("/")[0]
        k_val = round(round(i[1],2) * 100)
        k_list = [k,k_val]
        if(len(str(k_list[0]))> 1):
            keywords_l.append(k_list)


    return keywords_l