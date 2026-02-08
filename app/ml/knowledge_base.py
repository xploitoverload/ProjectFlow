# app/ml/knowledge_base.py
"""
Knowledge Base & AI Chatbot System
Manages FAQ articles, knowledge base, AI chatbot with NLP and ticket deflection.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
import uuid
import numpy as np


class ArticleCategory(Enum):
    """Knowledge base article categories."""
    FAQ = "faq"
    TROUBLESHOOTING = "troubleshooting"
    TUTORIAL = "tutorial"
    BEST_PRACTICE = "best_practice"
    KNOWN_ISSUE = "known_issue"


class ChatbotIntentType(Enum):
    """Chatbot intent types."""
    GREETING = "greeting"
    FAQ = "faq"
    TROUBLESHOOTING = "troubleshooting"
    ESCALATION = "escalation"
    FEEDBACK = "feedback"
    OTHER = "other"


@dataclass
class KBArticle:
    """Knowledge base article."""
    article_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    category: ArticleCategory = ArticleCategory.FAQ
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    views: int = 0
    helpful_count: int = 0
    unhelpful_count: int = 0
    embedding: List[float] = field(default_factory=list)  # For semantic search
    
    def get_sentiment(self) -> str:
        """Get article sentiment (helpful vs unhelpful ratio)."""
        total = self.helpful_count + self.unhelpful_count
        if total == 0:
            return 'neutral'
        ratio = self.helpful_count / total
        if ratio > 0.8:
            return 'very_helpful'
        elif ratio > 0.6:
            return 'helpful'
        elif ratio > 0.4:
            return 'neutral'
        else:
            return 'unhelpful'
    
    def to_dict(self) -> Dict:
        return {
            'article_id': self.article_id,
            'title': self.title,
            'category': self.category.value,
            'tags': self.tags,
            'views': self.views,
            'sentiment': self.get_sentiment(),
            'created_at': self.created_at.isoformat()
        }


@dataclass
class ChatMessage:
    """Chat message in conversation."""
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    conversation_id: str = ""
    sender: str = "user"  # user, bot, admin
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    intent: Optional[ChatbotIntentType] = None
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'message_id': self.message_id,
            'sender': self.sender,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'intent': self.intent.value if self.intent else None,
            'confidence': round(self.confidence, 3)
        }


@dataclass
class Conversation:
    """Chatbot conversation."""
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    messages: List[ChatMessage] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    resolved: bool = False
    escalated: bool = False
    satisfaction_score: Optional[float] = None
    
    def to_dict(self) -> Dict:
        return {
            'conversation_id': self.conversation_id,
            'user_id': self.user_id,
            'message_count': len(self.messages),
            'started_at': self.started_at.isoformat(),
            'resolved': self.resolved,
            'escalated': self.escalated,
            'satisfaction_score': self.satisfaction_score
        }


class KnowledgeBaseAndChatbot:
    """
    Knowledge base and AI chatbot system with NLP and ticket deflection.
    """
    
    def __init__(self):
        """Initialize knowledge base and chatbot."""
        self.articles: Dict[str, KBArticle] = {}
        self.conversations: Dict[str, Conversation] = {}
        self.faqs: Dict[str, KBArticle] = {}
        self.common_intents: Dict[str, List[str]] = self._init_intent_patterns()
        self.stats = {
            'total_conversations': 0,
            'resolved_conversations': 0,
            'escalated_conversations': 0
        }
    
    def _init_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize intent pattern matching."""
        return {
            'greeting': ['hello', 'hi', 'hey', 'greetings'],
            'help': ['help', 'assist', 'support', 'how to'],
            'error': ['error', 'not working', 'broken', 'issue', 'problem'],
            'feedback': ['feedback', 'suggestion', 'complain', 'review'],
            'billing': ['billing', 'price', 'payment', 'invoice', 'cost']
        }
    
    def create_article(self, title: str, content: str, 
                      category: ArticleCategory = ArticleCategory.FAQ,
                      tags: List[str] = None) -> KBArticle:
        """Create knowledge base article."""
        article = KBArticle(
            title=title,
            content=content,
            category=category,
            tags=tags or [],
            keywords=self._extract_keywords(content)
        )
        
        # Generate embedding (simulate with random vector)
        article.embedding = np.random.rand(128).tolist()
        
        self.articles[article.article_id] = article
        
        if category == ArticleCategory.FAQ:
            self.faqs[article.article_id] = article
        
        return article
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simulate keyword extraction
        words = text.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'is', 'it', 'to', 'for'}
        keywords = [w for w in words if w not in stop_words and len(w) > 3][:10]
        return keywords
    
    def search_articles(self, query: str, limit: int = 5) -> List[Dict]:
        """Search knowledge base articles."""
        results = []
        
        # Simple keyword matching
        query_lower = query.lower()
        for article in self.articles.values():
            score = 0
            
            # Title matching (high weight)
            if query_lower in article.title.lower():
                score += 10
            
            # Keyword matching
            query_words = query_lower.split()
            for word in query_words:
                if word in article.keywords:
                    score += 5
                elif word in article.tags:
                    score += 3
            
            if score > 0:
                results.append((article, score))
        
        # Sort by score and return
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0].to_dict() for r in results[:limit]]
    
    def detect_intent(self, message: str) -> Tuple[ChatbotIntentType, float]:
        """Detect user intent from message."""
        message_lower = message.lower()
        
        # Check greeting
        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return ChatbotIntentType.GREETING, 0.95
        
        # Check for error/troubleshooting
        if any(word in message_lower for word in ['error', 'problem', 'not working', 'issue']):
            return ChatbotIntentType.TROUBLESHOOTING, 0.85
        
        # Check for FAQ
        if any(word in message_lower for word in ['how', 'what', 'where', 'when']):
            return ChatbotIntentType.FAQ, 0.75
        
        # Default to other
        return ChatbotIntentType.OTHER, 0.5
    
    def create_conversation(self, user_id: str = None) -> Conversation:
        """Create new chat conversation."""
        conversation = Conversation(user_id=user_id)
        self.conversations[conversation.conversation_id] = conversation
        self.stats['total_conversations'] += 1
        return conversation
    
    def add_message(self, conversation_id: str, sender: str, 
                   content: str) -> ChatMessage:
        """Add message to conversation."""
        if conversation_id not in self.conversations:
            raise ValueError("Conversation not found")
        
        conversation = self.conversations[conversation_id]
        
        # Detect intent for user messages
        intent, confidence = None, 0.0
        if sender == 'user':
            intent, confidence = self.detect_intent(content)
        
        message = ChatMessage(
            conversation_id=conversation_id,
            sender=sender,
            content=content,
            intent=intent,
            confidence=confidence
        )
        
        conversation.messages.append(message)
        return message
    
    def get_bot_response(self, conversation_id: str, user_message: str) -> str:
        """Generate bot response."""
        intent, confidence = self.detect_intent(user_message)
        
        # Search for relevant articles
        articles = self.search_articles(user_message, limit=1)
        
        if articles:
            article = articles[0]
            return f"I found a helpful article: {article['title']}. Would you like me to show you more details?"
        
        if intent == ChatbotIntentType.GREETING:
            return "Hello! How can I help you today?"
        elif intent == ChatbotIntentType.TROUBLESHOOTING:
            return "I understand you're having an issue. Can you provide more details?"
        elif intent == ChatbotIntentType.FAQ:
            return "I'm searching for the answer to your question. Let me help!"
        else:
            return "Thank you for your message. How can I assist you?"
    
    def mark_conversation_resolved(self, conversation_id: str, 
                                   satisfaction_score: float = 5.0) -> bool:
        """Mark conversation as resolved."""
        if conversation_id not in self.conversations:
            return False
        
        conversation = self.conversations[conversation_id]
        conversation.resolved = True
        conversation.ended_at = datetime.utcnow()
        conversation.satisfaction_score = satisfaction_score
        
        self.stats['resolved_conversations'] += 1
        
        return True
    
    def escalate_conversation(self, conversation_id: str) -> bool:
        """Escalate conversation to human agent."""
        if conversation_id not in self.conversations:
            return False
        
        conversation = self.conversations[conversation_id]
        conversation.escalated = True
        self.stats['escalated_conversations'] += 1
        
        return True
    
    def deflect_ticket(self, message: str) -> bool:
        """Check if issue can be deflected (solved by chatbot)."""
        # Search for relevant articles
        articles = self.search_articles(message, limit=1)
        
        if articles:
            article = articles[0]
            # If article exists and is helpful, can deflect
            return article.get('sentiment') in ['helpful', 'very_helpful']
        
        return False
    
    def get_conversation(self, conversation_id: str) -> Dict:
        """Get conversation details."""
        if conversation_id not in self.conversations:
            return {'error': 'Conversation not found'}
        
        conv = self.conversations[conversation_id]
        return {
            'conversation': conv.to_dict(),
            'messages': [m.to_dict() for m in conv.messages]
        }
    
    def record_feedback(self, article_id: str, helpful: bool) -> Dict:
        """Record article feedback."""
        if article_id not in self.articles:
            return {'error': 'Article not found'}
        
        article = self.articles[article_id]
        if helpful:
            article.helpful_count += 1
        else:
            article.unhelpful_count += 1
        
        return {
            'status': 'success',
            'helpful_count': article.helpful_count,
            'unhelpful_count': article.unhelpful_count,
            'sentiment': article.get_sentiment()
        }
    
    def get_stats(self) -> Dict:
        """Get knowledge base and chatbot statistics."""
        avg_satisfaction = 0
        if self.conversations:
            satisfied = [c.satisfaction_score for c in self.conversations.values() 
                        if c.satisfaction_score]
            if satisfied:
                avg_satisfaction = sum(satisfied) / len(satisfied)
        
        return {
            'total_articles': len(self.articles),
            'faqs': len(self.faqs),
            'total_conversations': self.stats['total_conversations'],
            'resolved_conversations': self.stats['resolved_conversations'],
            'resolution_rate': round(
                self.stats['resolved_conversations'] / max(self.stats['total_conversations'], 1), 3
            ),
            'escalated_conversations': self.stats['escalated_conversations'],
            'escalation_rate': round(
                self.stats['escalated_conversations'] / max(self.stats['total_conversations'], 1), 3
            ),
            'average_satisfaction': round(avg_satisfaction, 2),
            'total_messages': sum(len(c.messages) for c in self.conversations.values())
        }


# Global knowledge base and chatbot instance
kb_chatbot = KnowledgeBaseAndChatbot()
