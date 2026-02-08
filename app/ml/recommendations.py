"""Smart Recommendations Engine - Content and Collaborative Filtering"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import statistics

logger = logging.getLogger(__name__)


@dataclass
class Recommendation:
    """A recommendation item"""
    id: str
    title: str
    description: str
    type: str  # template, assignment, resolution, etc
    confidence_score: float  # 0.0 - 1.0
    reason: str
    metadata: Dict
    timestamp: datetime


class ContentBasedRecommender:
    """Content-based recommendations"""
    
    @staticmethod
    def extract_issue_features(issue: Dict) -> Dict[str, Any]:
        """Extract features from issue for similarity"""
        return {
            'priority': issue.get('priority', 'medium'),
            'type': issue.get('type', 'bug'),
            'status': issue.get('status', 'open'),
            'tags': set(issue.get('tags', [])),
            'components': set(issue.get('components', [])),
        }
    
    @staticmethod
    def calculate_similarity(features1: Dict, features2: Dict) -> float:
        """Calculate similarity between two issue feature sets"""
        similarity = 0.0
        weights = {
            'priority': 0.2,
            'type': 0.3,
            'tags': 0.2,
            'components': 0.25,
        }
        
        # Priority match
        if features1.get('priority') == features2.get('priority'):
            similarity += weights['priority']
        
        # Type match
        if features1.get('type') == features2.get('type'):
            similarity += weights['type']
        
        # Tag overlap
        tags1 = features1.get('tags', set())
        tags2 = features2.get('tags', set())
        if tags1 and tags2:
            overlap = len(tags1 & tags2) / len(tags1 | tags2)
            similarity += overlap * weights['tags']
        
        # Component overlap
        comps1 = features1.get('components', set())
        comps2 = features2.get('components', set())
        if comps1 and comps2:
            overlap = len(comps1 & comps2) / len(comps1 | comps2)
            similarity += overlap * weights['components']
        
        return min(similarity, 1.0)
    
    def recommend_similar_issues(self, issue: Dict, all_issues: List[Dict], top_n: int = 5) -> List[Recommendation]:
        """Recommend similar issues"""
        recommendations = []
        issue_features = self.extract_issue_features(issue)
        
        similarities = []
        for other_issue in all_issues:
            if other_issue['id'] == issue['id']:
                continue
            
            other_features = self.extract_issue_features(other_issue)
            similarity = self.calculate_similarity(issue_features, other_features)
            similarities.append((other_issue, similarity))
        
        # Sort by similarity and get top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        for other_issue, similarity in similarities[:top_n]:
            if similarity > 0.3:  # Minimum threshold
                rec = Recommendation(
                    id=other_issue['id'],
                    title=other_issue.get('title', ''),
                    description=f"Similar issue with {similarity*100:.0f}% match",
                    type='similar_issue',
                    confidence_score=similarity,
                    reason="Content-based similarity",
                    metadata={'original_issue_id': issue['id']},
                    timestamp=datetime.now(),
                )
                recommendations.append(rec)
        
        return recommendations
    
    def recommend_project_templates(self, project: Dict, template_library: List[Dict]) -> List[Recommendation]:
        """Recommend project templates based on project type"""
        recommendations = []
        
        project_type = project.get('type', 'general')
        project_tags = set(project.get('tags', []))
        
        for template in template_library:
            template_type = template.get('type', 'general')
            template_tags = set(template.get('tags', []))
            
            # Match on type and tags
            score = 0.0
            if template_type == project_type:
                score += 0.5
            
            if template_tags and project_tags:
                overlap = len(template_tags & project_tags) / len(template_tags | project_tags)
                score += overlap * 0.5
            
            if score > 0.3:
                rec = Recommendation(
                    id=template['id'],
                    title=template.get('name', ''),
                    description=template.get('description', ''),
                    type='project_template',
                    confidence_score=score,
                    reason="Matches project characteristics",
                    metadata={'project_id': project['id']},
                    timestamp=datetime.now(),
                )
                recommendations.append(rec)
        
        return sorted(recommendations, key=lambda x: x.confidence_score, reverse=True)


class CollaborativeRecommender:
    """Collaborative filtering recommendations"""
    
    @staticmethod
    def build_user_issue_matrix(users: List[Dict], issues: List[Dict]) -> Dict:
        """Build user-issue interaction matrix"""
        matrix = {}
        
        for user in users:
            user_id = user['id']
            matrix[user_id] = {}
            
            # Track issues user has worked on
            for issue in issues:
                assignees = set(issue.get('assignees', []))
                if user_id in assignees:
                    # Score: time spent, comments, resolution
                    score = 1.0
                    if issue.get('status') == 'closed':
                        score += 0.5
                    if issue.get('comment_count', 0) > 0:
                        score += 0.3
                    
                    matrix[user_id][issue['id']] = score
        
        return matrix
    
    def find_similar_users(self, user_id: str, user_issue_matrix: Dict, top_n: int = 5) -> List[Tuple[str, float]]:
        """Find similar users based on issue work"""
        if user_id not in user_issue_matrix:
            return []
        
        user_issues = set(user_issue_matrix[user_id].keys())
        if not user_issues:
            return []
        
        similarities = []
        for other_user_id, other_issues in user_issue_matrix.items():
            if other_user_id == user_id:
                continue
            
            other_issue_set = set(other_issues.keys())
            if not other_issue_set:
                continue
            
            # Jaccard similarity
            overlap = len(user_issues & other_issue_set)
            union = len(user_issues | other_issue_set)
            similarity = overlap / union if union > 0 else 0
            
            if similarity > 0:
                similarities.append((other_user_id, similarity))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]
    
    def recommend_team_members(self, user_id: str, project_type: str, all_users: List[Dict], 
                              user_issue_matrix: Dict, top_n: int = 5) -> List[Recommendation]:
        """Recommend team members for collaboration"""
        recommendations = []
        
        similar_users = self.find_similar_users(user_id, user_issue_matrix, top_n=10)
        
        # Get unique users who specialize in this project type
        for other_user_id, similarity in similar_users:
            user = next((u for u in all_users if u['id'] == other_user_id), None)
            if not user:
                continue
            
            # Score based on specialization and collaboration history
            specialization = project_type in user.get('specializations', [])
            score = similarity * 0.6 + (0.4 if specialization else 0)
            
            if score > 0.2:
                rec = Recommendation(
                    id=user['id'],
                    title=user.get('name', user['id']),
                    description=f"Good fit for team (Similarity: {similarity*100:.0f}%)",
                    type='team_member',
                    confidence_score=min(score, 1.0),
                    reason="Collaborative history and expertise",
                    metadata={'user_id': other_user_id, 'project_type': project_type},
                    timestamp=datetime.now(),
                )
                recommendations.append(rec)
        
        return recommendations[:top_n]


class RecommendationEngine:
    """Main recommendation engine"""
    
    def __init__(self):
        self.content_recommender = ContentBasedRecommender()
        self.collaborative_recommender = CollaborativeRecommender()
    
    def get_issue_recommendations(self, issue: Dict, all_issues: List[Dict], 
                                 all_users: List[Dict] = None) -> Dict[str, List[Recommendation]]:
        """Get all recommendations for an issue"""
        recommendations = {
            'similar_issues': [],
            'suggested_assignees': [],
        }
        
        # Content-based similar issues
        recommendations['similar_issues'] = self.content_recommender.recommend_similar_issues(
            issue, all_issues
        )
        
        # Collaborative filtering for assignees
        if all_users:
            user_issue_matrix = self.collaborative_recommender.build_user_issue_matrix(
                all_users, all_issues
            )
            
            # Get issue type/tags for context
            project_type = issue.get('type', 'general')
            recommendations['suggested_assignees'] = self.collaborative_recommender.recommend_team_members(
                issue.get('created_by', ''), project_type, all_users, user_issue_matrix
            )
        
        return recommendations
    
    def get_project_recommendations(self, project: Dict, 
                                   template_library: List[Dict] = None) -> Dict[str, List[Recommendation]]:
        """Get all recommendations for a project"""
        recommendations = {
            'templates': [],
        }
        
        if template_library:
            recommendations['templates'] = self.content_recommender.recommend_project_templates(
                project, template_library
            )
        
        return recommendations
    
    def get_personalized_recommendations(self, user_id: str, context: Dict) -> List[Recommendation]:
        """Get personalized recommendations for a user"""
        recommendations = []
        
        # Could include:
        # - Suggested issues based on skills
        # - Recommended projects
        # - Team collaboration suggestions
        # - Learning resources
        
        return recommendations


# Global recommender instance
recommendation_engine = RecommendationEngine()
