"""关键词提取器 - 从文本中提取高频关键词"""

import re
import math
from collections import Counter
from analyzers.base import BaseAnalyzer


class KeywordExtractor(BaseAnalyzer):
    """基于TF-IDF的关键词提取器"""

    name = "keyword_extractor"
    description = "关键词提取与频率统计"

    # 常见英文停用词
    STOP_WORDS_EN = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "need", "dare", "ought",
        "used", "to", "of", "in", "for", "on", "with", "at", "by", "from",
        "as", "into", "through", "during", "before", "after", "above", "below",
        "between", "out", "off", "over", "under", "again", "further", "then",
        "once", "here", "there", "when", "where", "why", "how", "all", "both",
        "each", "few", "more", "most", "other", "some", "such", "no", "nor",
        "not", "only", "own", "same", "so", "than", "too", "very", "just",
        "because", "but", "and", "or", "if", "while", "about", "up", "down",
        "it", "its", "this", "that", "these", "those", "i", "me", "my", "we",
        "our", "you", "your", "he", "him", "his", "she", "her", "they", "them",
        "their", "what", "which", "who", "whom", "new", "like", "also", "get",
        "got", "make", "made", "use", "using", "one", "two", "first", "last",
        "long", "great", "little", "just", "know", "take", "people", "time",
        "way", "day", "may", "come", "good", "now", "find", "way", "many",
    }

    # 常见中文停用词
    STOP_WORDS_CN = {
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
        "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
        "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
        "什么", "怎么", "如何", "可以", "能", "把", "被", "让", "给", "从",
        "对", "与", "为", "以", "及", "等", "但", "而", "或", "如果", "因为",
        "所以", "虽然", "但是", "然后", "这个", "那个", "已经", "正在", "通过",
        "进行", "使用", "支持", "实现", "包括", "提供", "基于", "其中", "关于",
    }

    def __init__(self, config=None, logger=None, top_n=20):
        super().__init__(config, logger)
        self.top_n = top_n
        self.stop_words = self.STOP_WORDS_EN | self.STOP_WORDS_CN

    def analyze(self, items):
        """
        从数据项中提取关键词

        Args:
            items: 数据项列表

        Returns:
            list[dict]: 关键词列表，包含词频和TF-IDF分数
        """
        if not items:
            return []

        # 提取所有文档
        documents = []
        for item in items:
            text = " ".join([
                str(item.get("title", "")),
                str(item.get("description", "")),
            ])
            tokens = self._tokenize(text)
            documents.append(tokens)

        if not documents:
            return []

        # 计算TF-IDF
        keywords = self._compute_tfidf(documents)

        if self.logger:
            self.logger.info("[keyword] 提取到 {} 个关键词".format(len(keywords)))

        return keywords

    def _tokenize(self, text):
        """分词"""
        # 转小写
        text = text.lower()

        # 提取英文单词（至少2个字符）
        en_tokens = re.findall(r'\b[a-z]{2,}\b', text)

        # 提取中文词（简单的双字组合）
        cn_tokens = re.findall(r'[\u4e00-\u9fff]{2,}', text)

        # 合并并过滤停用词
        all_tokens = en_tokens + cn_tokens
        filtered = [t for t in all_tokens if t not in self.stop_words]

        return filtered

    def _compute_tfidf(self, documents):
        """计算TF-IDF"""
        # 计算文档频率
        doc_freq = Counter()
        for doc in documents:
            unique_tokens = set(doc)
            for token in unique_tokens:
                doc_freq[token] += 1

        total_docs = len(documents)

        # 计算全局词频
        global_freq = Counter()
        for doc in documents:
            global_freq.update(doc)

        # 计算TF-IDF
        results = []
        for word, freq in global_freq.most_common(self.top_n * 3):
            tf = freq / sum(global_freq.values())
            idf = math.log((total_docs + 1) / (doc_freq.get(word, 0) + 1)) + 1
            tfidf = tf * idf

            results.append({
                "keyword": word,
                "frequency": freq,
                "tfidf_score": round(tfidf, 6),
                "doc_frequency": doc_freq.get(word, 0),
            })

        # 按TF-IDF排序
        results.sort(key=lambda x: x["tfidf_score"], reverse=True)

        return results[:self.top_n]

    def extract_from_text(self, text, top_n=None):
        """从单段文本中提取关键词"""
        n = top_n or self.top_n
        tokens = self._tokenize(text)
        freq = Counter(tokens)
        return [
            {"keyword": word, "frequency": count}
            for word, count in freq.most_common(n)
        ]
