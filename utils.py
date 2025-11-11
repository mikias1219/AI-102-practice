"""
Utility functions for the Azure AI Agent Chat application
"""
import re
from datetime import datetime
from typing import Optional, Dict, Any


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """Format a datetime object as a readable timestamp"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%H:%M:%S")


def format_latency(latency: float) -> str:
    """Format latency in seconds as a readable string"""
    if latency < 1:
        return f"{latency*1000:.0f}ms"
    return f"{latency:.2f}s"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to a maximum length with ellipsis"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def extract_links(text: str) -> list[str]:
    """Extract URLs from text"""
    url_pattern = r'https?://[^\s]+'
    return re.findall(url_pattern, text)


def is_question(text: str) -> bool:
    """Check if text ends with a question mark or starts with question words"""
    question_words = ['what', 'how', 'when', 'where', 'why', 'who', 'which', 'can', 'could', 'should', 'would', 'is', 'are']
    text_lower = text.lower().strip()
    return text_lower.endswith('?') or any(text_lower.startswith(word) for word in question_words)


def format_message_for_display(message: Dict[str, Any], max_length: Optional[int] = None) -> str:
    """Format a message for display in the chat UI"""
    content = message.get('content', '')
    
    if max_length:
        content = truncate_text(content, max_length)
    
    return content


def get_emoji_for_response_type(response_text: str) -> str:
    """Get an appropriate emoji based on response type"""
    text_lower = response_text.lower()
    
    if any(word in text_lower for word in ['error', 'failed', 'cannot', 'unable']):
        return "⚠️"
    elif any(word in text_lower for word in ['success', 'done', 'complete', 'finished']):
        return "✅"
    elif any(word in text_lower for word in ['question', 'ask', '?']):
        return "❓"
    elif any(word in text_lower for word in ['code', 'python', 'javascript', 'function']):
        return "💻"
    else:
        return "💬"


def calculate_stats(messages: list[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics from message list"""
    stats = {
        'total_messages': len(messages),
        'user_messages': sum(1 for m in messages if m['role'] == 'user'),
        'agent_messages': sum(1 for m in messages if m['role'] == 'agent'),
        'avg_latency': 0.0,
        'total_latency': 0.0,
    }
    
    latencies = [m.get('latency', 0) for m in messages if m['role'] == 'agent' and 'latency' in m]
    if latencies:
        stats['total_latency'] = sum(latencies)
        stats['avg_latency'] = stats['total_latency'] / len(latencies)
    
    return stats


def export_chat_history(messages: list[Dict[str, Any]], format: str = 'txt') -> str:
    """Export chat history in different formats"""
    if format == 'txt':
        lines = []
        for msg in messages:
            role = msg['role'].upper()
            content = msg['content']
            timestamp = msg.get('timestamp', '')
            lines.append(f"[{timestamp}] {role}:\n{content}\n")
        return "\n".join(lines)
    
    elif format == 'markdown':
        lines = []
        for msg in messages:
            if msg['role'] == 'user':
                lines.append(f"**You:** {msg['content']}")
            else:
                lines.append(f"**Agent:** {msg['content']}")
        return "\n\n".join(lines)
    
    return str(messages)




