"""
Ad Attack Prevention Module
Comprehensive protection against advertising-related attacks and frauds
Includes ad fraud detection, malicious ad blocking, and compliance
"""

import logging
import re
import json
from functools import wraps
from flask import request, abort
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)


class AdFraudDetection:
    """Detect and prevent advertising fraud"""
    
    # Click fraud indicators
    CLICK_FRAUD_PATTERNS = {
        'rapid_clicks': 'Multiple clicks from same IP within seconds',
        'bot_ua': 'Bot/crawler user agents',
        'invalid_referer': 'Invalid or missing referer',
        'vpn_proxy': 'VPN/Proxy IP addresses',
        'same_device_id': 'Same device ID with different IPs',
        'impossible_geography': 'Impossible geographic movements',
    }
    
    # Impression fraud patterns
    IMPRESSION_FRAUD_PATTERNS = {
        'hidden_ads': 'Ad placement in hidden elements',
        'stacked_ads': 'Multiple ads stacked on same position',
        'small_viewports': 'Ads in very small viewports',
        'off_screen': 'Ads completely off-screen',
        'cookie_stuffing': 'Cookie stuffing attacks',
    }
    
    # Malware patterns
    MALWARE_PATTERNS = {
        'script_injection': 'Malicious script injection',
        'redirect_hijacking': 'Redirect hijacking',
        'click_injection': 'Click injection attacks',
        'silent_install': 'Silent software installation',
        'data_theft': 'Data theft payloads',
    }
    
    # Bot patterns
    BOT_USER_AGENTS = [
        'bot', 'crawler', 'spider', 'scraper', 'curl', 'wget',
        'ahrefsbot', 'baiduspider', 'yandexbot', 'googlebot',
        'headless', 'phantomjs', 'selenium', 'scrapy'
    ]
    
    # VPN/Proxy IP ranges (known VPN providers)
    KNOWN_VPN_PROVIDERS = [
        '104.21.0.0/16',  # Cloudflare
        '34.64.0.0/10',   # Google Cloud
        '52.0.0.0/8',     # AWS
    ]

    @staticmethod
    def detect_click_fraud(click_data):
        """Detect click fraud patterns"""
        fraud_score = 0
        fraud_details = []
        
        # Check rapid clicks from same IP
        if 'ip_address' in click_data and 'timestamp' in click_data:
            click_history = click_data.get('click_history', [])
            recent_clicks = [c for c in click_history 
                           if (datetime.now() - c.get('timestamp', datetime.now())).seconds < 5]
            
            if len(recent_clicks) > 3:
                fraud_score += 25
                fraud_details.append('Rapid clicks detected (>3 in 5 seconds)')
        
        # Check user agent
        user_agent = click_data.get('user_agent', '').lower()
        for bot_ua in AdFraudDetection.BOT_USER_AGENTS:
            if bot_ua in user_agent:
                fraud_score += 30
                fraud_details.append(f'Bot user agent detected: {bot_ua}')
                break
        
        # Check referer validity
        referer = click_data.get('referer', '')
        if not referer or referer.startswith('direct'):
            fraud_score += 10
            fraud_details.append('Invalid or missing referer')
        
        # Check for VPN/Proxy
        ip_address = click_data.get('ip_address', '')
        if AdFraudDetection._is_vpn_proxy(ip_address):
            fraud_score += 20
            fraud_details.append('VPN/Proxy IP detected')
        
        return {
            'is_fraud': fraud_score >= 50,
            'score': fraud_score,
            'details': fraud_details
        }
    
    @staticmethod
    def detect_impression_fraud(impression_data):
        """Detect impression fraud patterns"""
        fraud_score = 0
        fraud_details = []
        
        # Check if ad is visible on page
        if impression_data.get('visibility_ratio', 0) < 0.5:
            fraud_score += 30
            fraud_details.append('Ad not fully visible (visibility < 50%)')
        
        # Check if ad is in viewport
        if not impression_data.get('in_viewport', False):
            fraud_score += 40
            fraud_details.append('Ad not in viewport')
        
        # Check for stacked ads
        if impression_data.get('layering_index', 1) > 1:
            fraud_score += 25
            fraud_details.append('Ad layering detected')
        
        # Check viewport size
        viewport_size = impression_data.get('viewport_size', 0)
        if viewport_size < 10000:  # Less than 100x100
            fraud_score += 20
            fraud_details.append(f'Suspiciously small viewport: {viewport_size}')
        
        # Check for cookie stuffing
        if impression_data.get('suspicious_cookies', False):
            fraud_score += 35
            fraud_details.append('Suspicious cookie patterns detected')
        
        return {
            'is_fraud': fraud_score >= 50,
            'score': fraud_score,
            'details': fraud_details
        }
    
    @staticmethod
    def detect_malware(ad_data):
        """Detect malware and malicious content in ads"""
        malware_score = 0
        malware_details = []
        
        # Check ad content for suspicious patterns
        ad_content = str(ad_data.get('content', ''))
        
        # Script injection patterns
        if re.search(r'<script[^>]*>', ad_content, re.IGNORECASE):
            malware_score += 30
            malware_details.append('Script tag detected in ad')
        
        # Suspicious event handlers
        suspicious_handlers = ['onerror', 'onload', 'onclick', 'onmouseover']
        for handler in suspicious_handlers:
            if handler in ad_content.lower():
                malware_score += 20
                malware_details.append(f'Suspicious event handler: {handler}')
        
        # Redirect patterns
        if re.search(r'(location\.href|window\.open|redirect)', ad_content, re.IGNORECASE):
            malware_score += 25
            malware_details.append('Redirect code detected')
        
        # Check for data exfiltration patterns
        if re.search(r'(navigator|screen|document|localStorage|sessionStorage)', 
                    ad_content, re.IGNORECASE):
            malware_score += 15
            malware_details.append('Data access patterns detected')
        
        # Check for known malware domains
        malware_domains = ad_data.get('domains', [])
        if AdFraudDetection._check_malware_domains(malware_domains):
            malware_score += 50
            malware_details.append('Known malware domain detected')
        
        return {
            'is_malware': malware_score >= 50,
            'score': malware_score,
            'details': malware_details
        }
    
    @staticmethod
    def _is_vpn_proxy(ip_address):
        """Check if IP is from VPN/Proxy"""
        # This would connect to a VPN detection service in production
        # For now, using known ranges
        try:
            from ipaddress import ip_address as parse_ip, ip_network
            
            ip = parse_ip(ip_address)
            
            for network in AdFraudDetection.KNOWN_VPN_PROVIDERS:
                if ip in ip_network(network):
                    return True
        except Exception as e:
            logger.error(f"VPN check error: {e}")
        
        return False
    
    @staticmethod
    def _check_malware_domains(domains):
        """Check domains against malware databases"""
        # This would connect to DNSBL or malware DB in production
        malware_db = [
            'malware.com', 'phishing.net', 'c2.malware.org'
        ]
        
        for domain in domains:
            if domain.lower() in malware_db:
                return True
        
        return False


class AdBlocking:
    """Block malicious and unwanted ads"""
    
    # Malicious ad domain blocklist
    AD_BLOCKLIST = [
        r'.*ads\..*\.com',
        r'.*doubleclick\..*',
        r'.*tracking\..*',
        r'.*analytics\..*\.io',
    ]
    
    # Whitelist for legitimate ad networks
    AD_WHITELIST = [
        'google.com',
        'facebook.com',
        'amazon.com',
    ]

    @staticmethod
    def should_block_ad(ad_data):
        """Determine if ad should be blocked"""
        ad_domain = ad_data.get('domain', '')
        
        # Check blocklist
        for blocked_pattern in AdBlocking.AD_BLOCKLIST:
            if re.match(blocked_pattern, ad_domain, re.IGNORECASE):
                return True, "Domain matches blocklist pattern"
        
        # Check content for policy violations
        content = str(ad_data.get('content', ''))
        
        # Prohibited content types
        prohibited_keywords = [
            'cryptocurrency scam', 'fake lottery', 'work from home scheme',
            'miracle cure', 'cheap drugs', 'illegal services'
        ]
        
        for keyword in prohibited_keywords:
            if keyword.lower() in content.lower():
                return True, f"Prohibited content: {keyword}"
        
        return False, "Ad approved"


class AdComplianceChecker:
    """Ensure ad compliance with regulations"""
    
    # IAB standards compliance
    REQUIRED_AD_DISCLOSURES = [
        'ad', 'advertisement', 'sponsored', 'promoted',
        'affiliate', 'partner content'
    ]

    @staticmethod
    def check_transparency(ad_data):
        """Check if ad has required transparency labels"""
        issues = []
        
        # Check for disclosure label
        has_disclosure = False
        for disclosure in AdComplianceChecker.REQUIRED_AD_DISCLOSURES:
            if disclosure.lower() in str(ad_data.get('label', '')).lower():
                has_disclosure = True
                break
        
        if not has_disclosure:
            issues.append("Missing 'Ad' or 'Sponsored' label")
        
        return {
            'compliant': len(issues) == 0,
            'issues': issues
        }
    
    @staticmethod
    def check_gdpr_compliance(ad_data):
        """Check GDPR compliance for ads"""
        issues = []
        
        # Check for consent tracking
        if not ad_data.get('has_consent_check', False):
            issues.append("No consent check for tracking")
        
        # Check for privacy policy link
        if not ad_data.get('privacy_policy_link'):
            issues.append("Missing privacy policy link")
        
        # Check for user data handling disclosure
        if ad_data.get('uses_tracking', False):
            if not ad_data.get('tracking_disclosure'):
                issues.append("Tracking used but not disclosed")
        
        return {
            'gdpr_compliant': len(issues) == 0,
            'issues': issues
        }
    
    @staticmethod
    def check_ccpa_compliance(ad_data):
        """Check CCPA compliance for ads"""
        issues = []
        
        # Check for "Do Not Sell My Personal Information" link
        if not ad_data.get('dnsmpi_link'):
            issues.append("Missing CCPA 'Do Not Sell' link")
        
        # Check for data collection disclosure
        if ad_data.get('collects_personal_data', False):
            if not ad_data.get('personal_data_disclosure'):
                issues.append("Personal data collection not disclosed")
        
        return {
            'ccpa_compliant': len(issues) == 0,
            'issues': issues
        }
    
    @staticmethod
    def check_coppa_compliance(ad_data):
        """Check COPPA compliance (Children's Online Privacy Protection)"""
        issues = []
        
        # Check if targeting children
        if ad_data.get('targets_children', False):
            # Stricter requirements for children's content
            if not ad_data.get('parent_consent_required'):
                issues.append("Parent consent required for children's ads")
            
            if ad_data.get('collects_personal_data'):
                issues.append("Cannot collect personal data from children")
        
        return {
            'coppa_compliant': len(issues) == 0,
            'issues': issues
        }


class AdViewabilityMonitoring:
    """Monitor ad viewability metrics"""

    @staticmethod
    def calculate_viewability_score(impression_data):
        """Calculate IAB viewability score"""
        score = 0
        
        # In viewport (50% requirement)
        if impression_data.get('in_viewport', False):
            if impression_data.get('visibility_ratio', 0) >= 0.5:
                score += 40
        
        # Duration viewed (1 second for display, 2 seconds for video)
        duration = impression_data.get('view_duration', 0)
        if duration >= 1:
            score += 30
        
        # Page placement
        if not impression_data.get('in_popup', False):
            score += 20
        
        # Ad size appropriate
        if impression_data.get('viewport_size', 0) >= 10000:
            score += 10
        
        return score
    
    @staticmethod
    def is_viewable(impression_data):
        """Check if ad meets viewability standards"""
        viewability_score = AdViewabilityMonitoring.calculate_viewability_score(impression_data)
        
        # IAB standard: 50% visible for 1 second
        return {
            'is_viewable': viewability_score >= 50,
            'score': viewability_score,
            'meets_iab_standard': (
                impression_data.get('visibility_ratio', 0) >= 0.5 and
                impression_data.get('view_duration', 0) >= 1
            )
        }


class AdSecurityScorer:
    """Score overall ad security"""

    @staticmethod
    def score_ad(ad_data, impression_data=None, click_data=None):
        """Generate comprehensive security score for ad"""
        total_score = 100
        security_issues = []
        
        # Malware check
        malware_detection = AdFraudDetection.detect_malware(ad_data)
        if malware_detection['is_malware']:
            total_score -= malware_detection['score']
            security_issues.extend(malware_detection['details'])
        
        # Click fraud (if click data provided)
        if click_data:
            click_fraud = AdFraudDetection.detect_click_fraud(click_data)
            if click_fraud['is_fraud']:
                total_score -= click_fraud['score']
                security_issues.extend(click_fraud['details'])
        
        # Impression fraud (if impression data provided)
        if impression_data:
            impression_fraud = AdFraudDetection.detect_impression_fraud(impression_data)
            if impression_fraud['is_fraud']:
                total_score -= impression_fraud['score']
                security_issues.extend(impression_fraud['details'])
        
        # Compliance checks
        transparency = AdComplianceChecker.check_transparency(ad_data)
        if not transparency['compliant']:
            total_score -= 10
            security_issues.extend(transparency['issues'])
        
        gdpr_check = AdComplianceChecker.check_gdpr_compliance(ad_data)
        if not gdpr_check['gdpr_compliant']:
            total_score -= 10
            security_issues.extend(gdpr_check['issues'])
        
        return {
            'security_score': max(0, total_score),  # Between 0-100
            'is_safe': total_score >= 70,
            'issues': security_issues,
            'recommendation': 'BLOCK' if total_score < 30 
                            else 'REVIEW' if total_score < 70 
                            else 'ALLOW'
        }


def validate_ad_request(f):
    """Decorator to validate ad requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Validate ad request parameters
        ad_data = {
            'content': request.args.get('content', ''),
            'domain': request.args.get('domain', ''),
            'referer': request.referrer,
            'user_agent': request.headers.get('User-Agent', ''),
        }
        
        # Check for ad fraud
        if AdFraudDetection.detect_malware(ad_data)['is_malware']:
            logger.warning(f"Malicious ad blocked: {ad_data['domain']}")
            abort(403)
        
        # Check if ad should be blocked
        should_block, reason = AdBlocking.should_block_ad(ad_data)
        if should_block:
            logger.warning(f"Ad blocked: {reason}")
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function
