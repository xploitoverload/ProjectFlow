"""NLP Processing Module - Natural Language Processing for Project Data"""

import logging
import re
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class SentimentScore(Enum):
    """Sentiment classification"""
    VERY_NEGATIVE = -2.0
    NEGATIVE = -1.0
    NEUTRAL = 0.0
    POSITIVE = 1.0
    VERY_POSITIVE = 2.0


@dataclass
class NLPResult:
    """Result of NLP processing"""
    text: str
    sentiment: SentimentScore
    sentiment_score: float  # -1.0 to 1.0
    entities: List[str]
    tags: List[str]
    keywords: List[str]
    summary: Optional[str]


class SimpleSentimentAnalyzer:
    """Simple lexicon-based sentiment analysis"""
    
    def __init__(self):
        # Positive and negative word lists
        self.positive_words = {
            'good', 'great', 'excellent', 'awesome', 'perfect', 'love', 'wonderful',
            'fantastic', 'amazing', 'brilliant', 'superb', 'outstanding', 'working',
            'fixed', 'resolved', 'solved', 'done', 'complete', 'success', 'successful'
        }
        
        self.negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'poor', 'worst',
            'broken', 'fail', 'failed', 'error', 'bug', 'issue', 'problem',
            'slow', 'crash', 'hang', 'freeze', 'stuck', 'confused', 'stuck'
        }
        
        self.intensifiers = {'very', 'really', 'extremely', 'absolutely'}
        self.negators = {'not', 'no', 'never', 'barely', 'hardly', 'scarcely'}
    
    def analyze(self, text: str) -> Tuple[SentimentScore, float]:
        """Analyze sentiment of text"""
        words = text.lower().split()
        
        sentiment_score = 0.0
        multiplier = 1.0
        
        for i, word in enumerate(words):
            # Remove punctuation
            clean_word = word.strip('.,!?;:')
            
            # Check for intensifiers
            if clean_word in self.intensifiers and i < len(words) - 1:
                multiplier = 1.5
            
            # Check for negators
            is_negated = False
            if i > 0 and words[i-1].lower() in self.negators:
                is_negated = True
            
            # Score word
            if clean_word in self.positive_words:
                score = 1.0 * multiplier
                if is_negated:
                    score = -score
                sentiment_score += score
            elif clean_word in self.negative_words:
                score = -1.0 * multiplier
                if is_negated:
                    score = -score
                sentiment_score += score
            
            multiplier = 1.0
        
        # Normalize
        if len(words) > 0:
            sentiment_score = sentiment_score / len(words)
        
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        # Convert to enum
        if sentiment_score >= 0.6:
            sentiment = SentimentScore.VERY_POSITIVE
        elif sentiment_score >= 0.2:
            sentiment = SentimentScore.POSITIVE
        elif sentiment_score >= -0.2:
            sentiment = SentimentScore.NEUTRAL
        elif sentiment_score >= -0.6:
            sentiment = SentimentScore.NEGATIVE
        else:
            sentiment = SentimentScore.VERY_NEGATIVE
        
        return sentiment, sentiment_score


class EntityExtractor:
    """Extract entities from text"""
    
    def __init__(self):
        self.entity_patterns = {
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'url': r'https?://[^\s]+',
            'mention': r'@[a-zA-Z0-9_]+',
            'issue_ref': r'#\d+',
            'code': r'`[^`]+`',
        }
    
    def extract(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text"""
        entities = {}
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                entities[entity_type] = matches
        
        return entities


class KeywordExtractor:
    """Extract keywords from text"""
    
    def __init__(self):
        self.stopwords = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'do', 'does', 'did', 'will', 'would', 'should', 'could',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it'
        }
    
    def extract(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extract keywords from text"""
        # Split into words
        words = text.lower().split()
        
        # Clean and filter
        keywords = []
        for word in words:
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word and clean_word not in self.stopwords and len(clean_word) > 2:
                keywords.append(clean_word)
        
        # Get unique and sort by frequency
        from collections import Counter
        keyword_counts = Counter(keywords)
        top_keywords = [word for word, count in keyword_counts.most_common(max_keywords)]
        
        return top_keywords


class TagAssigner:
    """Automatically assign tags based on content"""
    
    def __init__(self):
        self.tag_keywords = {
            'bug': ['bug', 'error', 'crash', 'broken', 'not working', 'fail'],
            'feature': ['feature', 'new', 'add', 'implement', 'functionality'],
            'documentation': ['doc', 'documentation', 'readme', 'guide', 'tutorial'],
            'performance': ['slow', 'optimize', 'speed', 'performance', 'lag'],
            'security': ['security', 'vulnerability', 'exploit', 'hacking', 'password'],
            'ui': ['ui', 'design', 'button', 'layout', 'visual', 'appearance'],
            'api': ['api', 'endpoint', 'request', 'response', 'integration'],
            'database': ['database', 'sql', 'query', 'index', 'migration'],
        }
    
    def assign_tags(self, text: str) -> List[str]:
        """Assign tags based on content"""
        text_lower = text.lower()
        assigned_tags = []
        
        for tag, keywords in self.tag_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    assigned_tags.append(tag)
                    break  # Found this tag
        
        return list(set(assigned_tags))  # Remove duplicates


class TextSummarizer:
    """Simple extractive text summarization"""
    
    @staticmethod
    def summarize(text: str, num_sentences: int = 2) -> str:
        """Summarize text to N sentences"""
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= num_sentences:
            return text
        
        # Score sentences by word frequency
        words = text.lower().split()
        word_freq = {}
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) > 3:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            score = 0
            for word in sentence.lower().split():
                clean_word = re.sub(r'[^\w]', '', word)
                score += word_freq.get(clean_word, 0)
            sentence_scores[i] = score
        
        # Get top sentences
        top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
        top_sentences.sort()  # Maintain original order
        
        summary = '. '.join([sentences[i] for i in top_sentences])
        return summary


class NLPProcessor:
    """Main NLP processor"""
    
    def __init__(self):
        self.sentiment_analyzer = SimpleSentimentAnalyzer()
        self.entity_extractor = EntityExtractor()
        self.keyword_extractor = KeywordExtractor()
        self.tag_assigner = TagAssigner()
        self.summarizer = TextSummarizer()
    
    def process(self, text: str) -> NLPResult:
        """Process text with all NLP tasks"""
        # Sentiment analysis
        sentiment, sentiment_score = self.sentiment_analyzer.analyze(text)
        
        # Entity extraction
        entities = self.entity_extractor.extract(text)
        entity_list = [e for ents in entities.values() for e in ents]
        
        # Keyword extraction
        keywords = self.keyword_extractor.extract(text)
        
        # Tag assignment
        tags = self.tag_assigner.assign_tags(text)
        
        # Summarization
        summary = self.summarizer.summarize(text) if len(text) > 200 else None
        
        return NLPResult(
            text=text,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            entities=entity_list,
            tags=tags,
            keywords=keywords,
            summary=summary,
        )
    
    def analyze_comments(self, comments: List[Dict]) -> Dict:
        """Analyze multiple comments"""
        results = {
            'total_comments': len(comments),
            'average_sentiment': 0.0,
            'sentiment_distribution': {},
            'top_keywords': {},
            'common_tags': {},
        }
        
        all_sentiment_scores = []
        all_keywords = []
        all_tags = []
        
        for comment in comments:
            text = comment.get('text', '')
            if not text:
                continue
            
            result = self.process(text)
            all_sentiment_scores.append(result.sentiment_score)
            all_keywords.extend(result.keywords)
            all_tags.extend(result.tags)
        
        if all_sentiment_scores:
            import statistics
            results['average_sentiment'] = statistics.mean(all_sentiment_scores)
        
        # Get sentiment distribution
        from collections import Counter
        sentiment_dist = Counter([s >= 0 for s in all_sentiment_scores])
        results['sentiment_distribution'] = {
            'positive': sentiment_dist.get(True, 0),
            'negative': sentiment_dist.get(False, 0),
        }
        
        # Top keywords
        keyword_counts = Counter(all_keywords)
        results['top_keywords'] = dict(keyword_counts.most_common(5))
        
        # Common tags
        tag_counts = Counter(all_tags)
        results['common_tags'] = dict(tag_counts.most_common(5))
        
        return results


# Global processor instance
nlp_processor = NLPProcessor()
