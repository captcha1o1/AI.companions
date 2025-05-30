"""Memory management functionality for the AI companions."""

import os
import json
from datetime import datetime
from difflib import SequenceMatcher
import re

class MemoryManager:
    def __init__(self, character="yuki"):
        self.character = character
        # Create memory directory if it doesn't exist
        self.memory_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "memories")
        os.makedirs(self.memory_dir, exist_ok=True)
        self.memory_file = os.path.join(self.memory_dir, f"{character}_memory.json")
        self.memories = []
        self.categories = {
            'personal': [],
            'emotions': [],
            'activities': [],
            'time': [],
            'location': []
        }
        self.load_memory()
    
    def set_character(self, character):
        """Change the current character and load their memories"""
        if self.character != character:
            self.save_memory()  # Save current character's memories
            self.character = character
            self.memory_file = os.path.join(self.memory_dir, f"{character}_memory.json")
        self.load_memory()
    
    def load_memory(self):
        """Load memories from JSON file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memories = data.get('memories', [])
                    self.categories = data.get('categories', self.categories)
        except Exception as e:
            print(f"Warning: Could not load memory file for {self.character}: {e}")
            self.memories = []
            self.categories = {
                'personal': [],
                'emotions': [],
                'activities': [],
                'time': [],
                'location': []
            }
    
    def save_memory(self):
        """Save memories to JSON file"""
        try:
            data = {
                'memories': self.memories,
                'categories': self.categories,
                'last_updated': datetime.now().isoformat(),
                'character': self.character
            }
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Could not save memory for {self.character}: {e}")
    
    def add_memory(self, user_input, ai_response):
        """Add a new memory with enhanced categorization"""
        # Extract topics and emotions
        topics = self.extract_topics(user_input + " " + ai_response)
        emotions = self.detect_emotions(user_input + " " + ai_response)
        
        # Calculate importance score
        importance = self.calculate_importance(user_input, ai_response, topics, emotions)
        
        memory = {
            'user': user_input,
            'ai': ai_response,
            'timestamp': datetime.now().isoformat(),
            'keywords': self.extract_keywords(user_input + " " + ai_response),
            'topics': topics,
            'emotions': emotions,
            'importance': importance,
            'recency_score': 1.0  # New memories get highest recency score
        }
        
        # Update recency scores for all memories
        self.update_recency_scores()
        
        # Add to memories and categorize
        self.memories.append(memory)
        self.categorize_memory(memory)
        
        # Keep only most important and recent memories
        self.prune_memories()
        
        self.save_memory()
    
    def find_relevant_memories(self, query, limit=5):
        """Find memories relevant to the current query with enhanced scoring"""
        if not self.memories:
            return []
        
        # Calculate similarity scores with multiple factors
        scored_memories = []
        query_topics = self.extract_topics(query)
        query_emotions = self.detect_emotions(query)
        
        for memory in self.memories:
            # Text similarity (40% weight)
            text_similarity = max(
                SequenceMatcher(None, query.lower(), memory['user'].lower()).ratio(),
                SequenceMatcher(None, query.lower(), memory['ai'].lower()).ratio()
            )
            
            # Topic similarity (30% weight)
            topic_similarity = self.calculate_topic_similarity(query_topics, memory['topics'])
            
            # Emotion similarity (20% weight)
            emotion_similarity = self.calculate_emotion_similarity(query_emotions, memory['emotions'])
            
            # Memory importance and recency (10% weight)
            importance_score = (memory['importance'] + memory['recency_score']) / 2
            
            # Calculate final score
            final_score = (
                text_similarity * 0.4 +
                topic_similarity * 0.3 +
                emotion_similarity * 0.2 +
                importance_score * 0.1
            )
            
            if final_score > 0.2:  # Lower threshold to include more relevant memories
                scored_memories.append((memory, final_score))
        
        # Sort by final score and return top matches
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, _ in scored_memories[:limit]]
    
    def extract_keywords(self, text):
        """Extract important keywords from text"""
        # Remove special characters and convert to lowercase
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = text.split()
        
        # Common words to filter out
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall',
            'should', 'can', 'could', 'may', 'might', 'must', 'i', 'you', 'he',
            'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'
        }
        
        # Extract meaningful words and phrases
        keywords = []
        for i, word in enumerate(words):
            if word not in common_words and len(word) > 3:
                keywords.append(word)
                # Add two-word phrases
                if i < len(words) - 1:
                    phrase = f"{word} {words[i+1]}"
                    if len(phrase) > 6:
                        keywords.append(phrase)
        
        return list(set(keywords))  # Remove duplicates
    
    def extract_topics(self, text):
        """Extract topics from text"""
        topics = []
        text = text.lower()
        
        # Personal topics
        personal_patterns = [
            r'\b(i|me|my|mine|you|your|yours|we|us|our|ours)\b',
            r'\b(name|age|birthday|family|friend|home|work|school)\b'
        ]
        
        # Activity topics
        activity_patterns = [
            r'\b(play|work|study|read|write|draw|paint|sing|dance|cook|eat|sleep)\b',
            r'\b(game|movie|music|book|art|sport|exercise|travel)\b'
        ]
        
        # Time topics
        time_patterns = [
            r'\b(today|tomorrow|yesterday|morning|afternoon|evening|night)\b',
            r'\b(week|month|year|hour|minute|second|time|date)\b'
        ]
        
        # Location topics
        location_patterns = [
            r'\b(home|school|work|office|park|beach|city|town|country)\b',
            r'\b(room|house|building|street|road|place|location)\b'
        ]
        
        # Check each category
        if any(re.search(pattern, text) for pattern in personal_patterns):
            topics.append('personal')
        if any(re.search(pattern, text) for pattern in activity_patterns):
            topics.append('activities')
        if any(re.search(pattern, text) for pattern in time_patterns):
            topics.append('time')
        if any(re.search(pattern, text) for pattern in location_patterns):
            topics.append('location')
            
        return topics
    
    def detect_emotions(self, text):
        """Detect emotions in text"""
        emotions = []
        text = text.lower()
        
        # Emotion patterns
        emotion_patterns = {
            'happy': [r'\b(happy|joy|excited|glad|cheerful|delighted|pleased)\b',
                     r'\b(smile|laugh|fun|great|wonderful|amazing|awesome)\b'],
            'sad': [r'\b(sad|unhappy|depressed|down|blue|miserable|gloomy)\b',
                   r'\b(cry|tear|upset|disappointed|sorry|regret)\b'],
            'angry': [r'\b(angry|mad|furious|annoyed|irritated|upset|frustrated)\b',
                     r'\b(hate|dislike|terrible|awful|horrible)\b'],
            'neutral': [r'\b(okay|fine|alright|normal|usual|regular|typical)\b']
        }
        
        # Check each emotion
        for emotion, patterns in emotion_patterns.items():
            if any(re.search(pattern, text) for pattern in patterns):
                emotions.append(emotion)
                
        return emotions if emotions else ['neutral']
    
    def calculate_importance(self, user_input, ai_response, topics, emotions):
        """Calculate importance score for a memory"""
        score = 0.5  # Base score
        
        # Length factor (0-0.2)
        length = len(user_input) + len(ai_response)
        score += min(length / 1000, 0.2)
        
        # Topic factor (0-0.2)
        if 'personal' in topics:
            score += 0.2
        if 'emotions' in topics:
            score += 0.1
            
        # Emotion factor (0-0.1)
        if 'happy' in emotions or 'sad' in emotions or 'angry' in emotions:
            score += 0.1
            
        return min(score, 1.0)  # Cap at 1.0
    
    def calculate_topic_similarity(self, query_topics, memory_topics):
        """Calculate similarity between query and memory topics"""
        if not query_topics or not memory_topics:
            return 0.0
            
        common_topics = set(query_topics) & set(memory_topics)
        return len(common_topics) / max(len(query_topics), len(memory_topics))
    
    def calculate_emotion_similarity(self, query_emotions, memory_emotions):
        """Calculate similarity between query and memory emotions"""
        if not query_emotions or not memory_emotions:
            return 0.0
            
        common_emotions = set(query_emotions) & set(memory_emotions)
        return len(common_emotions) / max(len(query_emotions), len(memory_emotions))
    
    def update_recency_scores(self):
        """Update recency scores for all memories"""
        current_time = datetime.now()
        for memory in self.memories:
            memory_time = datetime.fromisoformat(memory['timestamp'])
            hours_old = (current_time - memory_time).total_seconds() / 3600
            
            # Exponential decay: newer memories have higher scores
            memory['recency_score'] = max(0.1, 1.0 * (0.95 ** hours_old))
    
    def categorize_memory(self, memory):
        """Categorize memory into appropriate categories"""
        for topic in memory['topics']:
            if topic in self.categories:
                self.categories[topic].append(memory)
    
    def prune_memories(self):
        """Prune memories to keep only the most important and recent ones"""
        if len(self.memories) <= 100:  # Keep all if under limit
            return
            
        # Sort memories by importance and recency
        self.memories.sort(key=lambda x: (x['importance'] + x['recency_score']) / 2, reverse=True)
        
        # Keep top 80 most important memories
        important_memories = self.memories[:80]
        
        # Keep 20 most recent memories
        recent_memories = sorted(self.memories, key=lambda x: x['timestamp'], reverse=True)[:20]
        
        # Combine and remove duplicates
        self.memories = list({m['timestamp']: m for m in important_memories + recent_memories}.values())
        
        # Rebuild categories
        self.categories = {
            'personal': [],
            'emotions': [],
            'activities': [],
            'time': [],
            'location': []
        }
        for memory in self.memories:
            self.categorize_memory(memory) 