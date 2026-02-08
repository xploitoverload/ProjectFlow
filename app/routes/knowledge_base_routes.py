# app/routes/knowledge_base_routes.py
"""
Knowledge Base & Chatbot API Routes
Endpoints for articles, FAQs, chatbot, and ticket deflection.
"""

from flask import Blueprint, request, jsonify
from functools import wraps
import logging

from app.ml.knowledge_base import (
    kb_chatbot,
    ArticleCategory,
    ChatbotIntentType
)

logger = logging.getLogger(__name__)

# Create blueprint
kb_bp = Blueprint('knowledge_base', __name__, url_prefix='/api/v1/kb')


def require_auth(f):
    """Require authentication for endpoint."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# KNOWLEDGE BASE ARTICLE ROUTES
# ============================================================================

@kb_bp.route('/articles', methods=['GET', 'POST'])
@require_auth
def articles():
    """List or create articles."""
    if request.method == 'POST':
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        category_str = data.get('category', 'faq').upper()
        tags = data.get('tags', [])
        
        try:
            category = ArticleCategory[category_str]
        except KeyError:
            return jsonify({'error': 'Invalid category'}), 400
        
        article = kb_chatbot.create_article(title, content, category, tags)
        return jsonify(article.to_dict()), 201
    
    # GET - list articles
    articles_list = [a.to_dict() for a in kb_chatbot.articles.values()]
    return jsonify({
        'total': len(articles_list),
        'articles': articles_list
    })


@kb_bp.route('/articles/<article_id>', methods=['GET'])
@require_auth
def get_article(article_id):
    """Get article details."""
    if article_id not in kb_chatbot.articles:
        return jsonify({'error': 'Article not found'}), 404
    
    article = kb_chatbot.articles[article_id]
    article.views += 1  # Increment view count
    
    return jsonify({
        'article_id': article.article_id,
        'title': article.title,
        'content': article.content,
        'category': article.category.value,
        'tags': article.tags,
        'views': article.views,
        'sentiment': article.get_sentiment(),
        'created_at': article.created_at.isoformat()
    })


@kb_bp.route('/articles/<article_id>/feedback', methods=['POST'])
@require_auth
def article_feedback(article_id):
    """Record article feedback."""
    data = request.get_json()
    helpful = data.get('helpful', True)
    
    result = kb_chatbot.record_feedback(article_id, helpful)
    
    if 'error' in result:
        return jsonify(result), 404
    
    return jsonify(result)


# ============================================================================
# FAQ ROUTES
# ============================================================================

@kb_bp.route('/faqs', methods=['GET'])
@require_auth
def list_faqs():
    """List all FAQs."""
    faqs = [a.to_dict() for a in kb_chatbot.faqs.values()]
    
    return jsonify({
        'total': len(faqs),
        'faqs': faqs
    })


@kb_bp.route('/faqs/search', methods=['GET', 'POST'])
@require_auth
def search_faqs():
    """Search FAQs."""
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('query')
    else:
        query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'query required'}), 400
    
    results = kb_chatbot.search_articles(query)
    
    return jsonify({
        'query': query,
        'results': len(results),
        'articles': results
    })


# ============================================================================
# CHATBOT ROUTES
# ============================================================================

@kb_bp.route('/chat/start', methods=['POST'])
@require_auth
def start_conversation():
    """Start new chat conversation."""
    data = request.get_json()
    user_id = data.get('user_id')
    
    conversation = kb_chatbot.create_conversation(user_id)
    
    # Send greeting
    greeting = kb_chatbot.get_bot_response(conversation.conversation_id, "hello")
    kb_chatbot.add_message(conversation.conversation_id, 'bot', greeting)
    
    return jsonify({
        'conversation_id': conversation.conversation_id,
        'message': greeting
    }), 201


@kb_bp.route('/chat/<conversation_id>/message', methods=['POST'])
@require_auth
def send_message(conversation_id):
    """Send message in conversation."""
    data = request.get_json()
    user_message = data.get('message')
    
    if not user_message:
        return jsonify({'error': 'message required'}), 400
    
    # Add user message
    user_msg = kb_chatbot.add_message(conversation_id, 'user', user_message)
    
    # Get bot response
    bot_response = kb_chatbot.get_bot_response(conversation_id, user_message)
    bot_msg = kb_chatbot.add_message(conversation_id, 'bot', bot_response)
    
    return jsonify({
        'user_message': user_msg.to_dict(),
        'bot_message': bot_msg.to_dict(),
        'messages': [m.to_dict() for m in kb_chatbot.conversations[conversation_id].messages]
    }), 200


@kb_bp.route('/chat/<conversation_id>', methods=['GET'])
@require_auth
def get_conversation(conversation_id):
    """Get conversation details."""
    result = kb_chatbot.get_conversation(conversation_id)
    
    if 'error' in result:
        return jsonify(result), 404
    
    return jsonify(result)


@kb_bp.route('/chat/<conversation_id>/resolve', methods=['POST'])
@require_auth
def resolve_conversation(conversation_id):
    """Mark conversation as resolved."""
    data = request.get_json()
    satisfaction_score = data.get('satisfaction_score', 5.0)
    
    success = kb_chatbot.mark_conversation_resolved(conversation_id, satisfaction_score)
    
    if not success:
        return jsonify({'error': 'Conversation not found'}), 404
    
    return jsonify({
        'status': 'success',
        'conversation_id': conversation_id,
        'satisfaction_score': satisfaction_score
    })


@kb_bp.route('/chat/<conversation_id>/escalate', methods=['POST'])
@require_auth
def escalate_conversation(conversation_id):
    """Escalate conversation to human agent."""
    success = kb_chatbot.escalate_conversation(conversation_id)
    
    if not success:
        return jsonify({'error': 'Conversation not found'}), 404
    
    return jsonify({
        'status': 'success',
        'conversation_id': conversation_id,
        'escalated': True,
        'message': 'Conversation escalated to human agent'
    })


# ============================================================================
# INTENT & NLP ROUTES
# ============================================================================

@kb_bp.route('/intent/detect', methods=['POST'])
@require_auth
def detect_intent():
    """Detect intent from message."""
    data = request.get_json()
    message = data.get('message')
    
    if not message:
        return jsonify({'error': 'message required'}), 400
    
    intent, confidence = kb_chatbot.detect_intent(message)
    
    return jsonify({
        'intent': intent.value,
        'confidence': round(confidence, 3)
    })


@kb_bp.route('/deflection/check', methods=['POST'])
@require_auth
def check_ticket_deflection():
    """Check if ticket can be deflected."""
    data = request.get_json()
    message = data.get('message')
    
    if not message:
        return jsonify({'error': 'message required'}), 400
    
    can_deflect = kb_chatbot.deflect_ticket(message)
    articles = kb_chatbot.search_articles(message, limit=3)
    
    return jsonify({
        'can_deflect': can_deflect,
        'suggested_articles': articles
    })


# ============================================================================
# SEARCH ROUTES
# ============================================================================

@kb_bp.route('/search', methods=['GET', 'POST'])
@require_auth
def search():
    """Search knowledge base."""
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('query')
        limit = data.get('limit', 10)
    else:
        query = request.args.get('q')
        limit = request.args.get('limit', 10, type=int)
    
    if not query:
        return jsonify({'error': 'query required'}), 400
    
    results = kb_chatbot.search_articles(query, limit=limit)
    
    return jsonify({
        'query': query,
        'results_count': len(results),
        'articles': results
    })


# ============================================================================
# STATISTICS & ANALYTICS ROUTES
# ============================================================================

@kb_bp.route('/stats', methods=['GET'])
@require_auth
def kb_stats():
    """Get knowledge base statistics."""
    stats = kb_chatbot.get_stats()
    return jsonify(stats)


@kb_bp.route('/conversations', methods=['GET'])
@require_auth
def list_conversations():
    """List all conversations."""
    user_id = request.args.get('user_id')
    status = request.args.get('status')  # resolved, escalated, open
    
    conversations = []
    for conv in kb_chatbot.conversations.values():
        if user_id and conv.user_id != user_id:
            continue
        if status == 'resolved' and not conv.resolved:
            continue
        if status == 'escalated' and not conv.escalated:
            continue
        if status == 'open' and (conv.resolved or conv.escalated):
            continue
        
        conversations.append(conv.to_dict())
    
    return jsonify({
        'total': len(conversations),
        'conversations': conversations
    })


@kb_bp.route('/health', methods=['GET'])
def kb_health():
    """Health check for knowledge base."""
    stats = kb_chatbot.get_stats()
    return jsonify({
        'status': 'healthy',
        'stats': stats
    })
