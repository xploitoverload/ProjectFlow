/**
 * Atlassian Intelligence (AI) Features
 * AI JQL Builder, Bulk Move, Field Suggestions, Smart Recommendations, AI Assistant
 */

class AtlassianIntelligence {
    constructor() {
        this.aiEnabled = true;
        this.conversationHistory = [];
        this.suggestions = [];
        
        this.init();
    }

    async init() {
        console.log('Atlassian Intelligence initialized');
    }

    // AI JQL BUILDER - Natural Language to JQL
    async convertNaturalLanguageToJQL(query) {
        // Simulate AI processing
        const patterns = {
            'bugs assigned to me': 'type = Bug AND assignee = currentUser()',
            'show me bugs assigned to me': 'type = Bug AND assignee = currentUser()',
            'my open issues': 'assignee = currentUser() AND resolution = Unresolved',
            'high priority tasks': 'type = Task AND priority = High',
            'issues in current sprint': 'sprint = currentSprint()',
            'overdue issues': 'duedate < now() AND resolution = Unresolved',
            'recently updated': 'updated >= -7d',
            'created this week': 'created >= startOfWeek()',
            'in progress stories': 'type = Story AND status = "In Progress"'
        };

        const lowerQuery = query.toLowerCase();
        
        for (const [pattern, jql] of Object.entries(patterns)) {
            if (lowerQuery.includes(pattern)) {
                return {
                    jql: jql,
                    confidence: 0.95,
                    explanation: `Converted "${query}" to JQL query`
                };
            }
        }

        // Fallback - parse components
        let jql = [];
        
        if (lowerQuery.includes('bug')) jql.push('type = Bug');
        else if (lowerQuery.includes('story')) jql.push('type = Story');
        else if (lowerQuery.includes('task')) jql.push('type = Task');
        
        if (lowerQuery.includes('me') || lowerQuery.includes('my')) {
            jql.push('assignee = currentUser()');
        }
        
        if (lowerQuery.includes('high priority')) jql.push('priority = High');
        if (lowerQuery.includes('open')) jql.push('resolution = Unresolved');
        
        return {
            jql: jql.length > 0 ? jql.join(' AND ') : 'project = PROJ',
            confidence: 0.75,
            explanation: `Interpreted query: "${query}"`
        };
    }

    renderAIJQLBuilder(container) {
        const html = `
            <div class="ai-jql-builder">
                <div class="ai-header">
                    <div class="ai-icon">
                        <i data-lucide="sparkles"></i>
                    </div>
                    <h3>AI JQL Builder</h3>
                    <span class="ai-badge">Beta</span>
                </div>

                <div class="ai-input-container">
                    <textarea class="ai-query-input" id="aiJQLInput" 
                              placeholder="Describe what you're looking for... (e.g., 'show me all high priority bugs assigned to me')"
                              rows="3"></textarea>
                    <button class="btn-primary ai-generate-btn" onclick="atlassianAI.generateJQL()">
                        <i data-lucide="sparkles"></i>
                        Generate JQL
                    </button>
                </div>

                <div class="ai-result" id="aiJQLResult" style="display: none;">
                    <div class="result-header">
                        <span class="confidence-badge">95% confidence</span>
                    </div>
                    <div class="jql-output">
                        <code id="generatedJQL"></code>
                        <button class="btn-icon copy-jql-btn" onclick="atlassianAI.copyJQL()">
                            <i data-lucide="copy"></i>
                        </button>
                    </div>
                    <div class="ai-explanation" id="aiExplanation"></div>
                    <button class="btn-secondary use-jql-btn" onclick="atlassianAI.useGeneratedJQL()">
                        Use this query
                    </button>
                </div>

                <div class="ai-examples">
                    <label>Try these examples:</label>
                    <div class="example-chips">
                        <button class="example-chip" onclick="atlassianAI.fillExample('show me bugs assigned to me')">
                            Bugs assigned to me
                        </button>
                        <button class="example-chip" onclick="atlassianAI.fillExample('high priority tasks in current sprint')">
                            High priority in sprint
                        </button>
                        <button class="example-chip" onclick="atlassianAI.fillExample('issues created this week')">
                            Created this week
                        </button>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    // AI BULK MOVE - Intelligent issue moving
    async analyzeIssuesForBulkMove(issueKeys) {
        // Simulate AI analysis
        await this.simulateAIProcessing();
        
        return {
            suggestions: [
                {
                    targetProject: 'PROJ-2',
                    reason: 'These issues are related to backend work which is tracked in PROJ-2',
                    issues: issueKeys.slice(0, 3),
                    confidence: 0.92
                },
                {
                    targetProject: 'BUGS',
                    reason: 'These are bug reports that should be in the BUGS project',
                    issues: issueKeys.slice(3),
                    confidence: 0.88
                }
            ]
        };
    }

    renderAIBulkMove(container, selectedIssues) {
        const html = `
            <div class="ai-bulk-move">
                <div class="ai-magic-header">
                    <i data-lucide="sparkles"></i>
                    <h3>AI Bulk Move</h3>
                </div>

                <div class="ai-analyzing" id="aiAnalyzing">
                    <div class="ai-spinner"></div>
                    <p>Analyzing ${selectedIssues.length} issues...</p>
                </div>

                <div class="ai-suggestions" id="aiSuggestions" style="display: none;">
                    <div class="suggestion-card">
                        <div class="suggestion-header">
                            <span class="confidence-badge">92% confidence</span>
                            <h4>Move to PROJ-2</h4>
                        </div>
                        <p class="suggestion-reason">
                            These issues are related to backend work which is tracked in PROJ-2
                        </p>
                        <div class="affected-issues">
                            <span>3 issues will be moved</span>
                        </div>
                        <button class="btn-primary" onclick="atlassianAI.executeBulkMove('PROJ-2', [1,2,3])">
                            <i data-lucide="arrow-right"></i>
                            Move Issues
                        </button>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();

        // Simulate analysis
        setTimeout(() => {
            document.getElementById('aiAnalyzing').style.display = 'none';
            document.getElementById('aiSuggestions').style.display = 'block';
            if (window.lucide) lucide.createIcons();
        }, 2000);
    }

    // AI FIELD SUGGESTIONS
    async suggestAssignee(issueData) {
        await this.simulateAIProcessing();
        
        return {
            suggested: 'John Doe',
            reason: 'John has expertise in authentication systems (mentioned in description)',
            confidence: 0.89
        };
    }

    async suggestPriority(issueData) {
        await this.simulateAIProcessing();
        
        const keywords = ['urgent', 'critical', 'asap', 'blocker'];
        const description = (issueData.description || '').toLowerCase();
        
        for (const keyword of keywords) {
            if (description.includes(keyword)) {
                return {
                    suggested: 'High',
                    reason: `Description contains "${keyword}" indicating urgency`,
                    confidence: 0.91
                };
            }
        }
        
        return {
            suggested: 'Medium',
            reason: 'No urgency indicators found',
            confidence: 0.75
        };
    }

    async suggestLabels(issueData) {
        await this.simulateAIProcessing();
        
        return {
            suggested: ['backend', 'api', 'security'],
            reason: 'Based on issue title and description keywords',
            confidence: 0.87
        };
    }

    renderAISuggestionBadge(field, suggestion) {
        return `
            <div class="ai-suggestion-badge" onclick="atlassianAI.applySuggestion('${field}', '${suggestion.suggested}')">
                <i data-lucide="sparkles"></i>
                <span>AI suggests: ${suggestion.suggested}</span>
                <span class="confidence">${Math.round(suggestion.confidence * 100)}%</span>
            </div>
        `;
    }

    // SMART RECOMMENDATIONS
    async getProjectTemplateRecommendations(projectType) {
        await this.simulateAIProcessing();
        
        return [
            {
                name: 'Agile Software Development',
                reason: 'Perfect for iterative development with sprints',
                confidence: 0.93,
                features: ['Sprint planning', 'Backlog management', 'Velocity tracking']
            },
            {
                name: 'Kanban Board',
                reason: 'Continuous flow for ongoing work',
                confidence: 0.85,
                features: ['WIP limits', 'Flow metrics', 'Cycle time tracking']
            }
        ];
    }

    async getWorkflowRecommendations(projectKey) {
        await this.simulateAIProcessing();
        
        return [
            {
                name: 'Simplified Workflow',
                reason: 'Based on your team size and project complexity',
                states: ['To Do', 'In Progress', 'Done'],
                confidence: 0.88
            }
        ];
    }

    renderSmartRecommendations(container) {
        const html = `
            <div class="smart-recommendations">
                <div class="recommendations-header">
                    <i data-lucide="lightbulb"></i>
                    <h3>Smart Recommendations</h3>
                </div>

                <div class="recommendation-card">
                    <div class="rec-badge">
                        <i data-lucide="sparkles"></i>
                        <span>AI Recommended</span>
                    </div>
                    <h4>Agile Software Development Template</h4>
                    <p>Perfect for iterative development with sprints</p>
                    <ul class="features-list">
                        <li><i data-lucide="check"></i> Sprint planning</li>
                        <li><i data-lucide="check"></i> Backlog management</li>
                        <li><i data-lucide="check"></i> Velocity tracking</li>
                    </ul>
                    <button class="btn-primary" onclick="atlassianAI.applyTemplate('agile')">
                        Use Template
                    </button>
                </div>
            </div>
        `;

        container.innerHTML = html;
        if (window.lucide) lucide.createIcons();
    }

    // AI ASSISTANT CHATBOT
    openAIAssistant() {
        const panel = document.createElement('div');
        panel.className = 'ai-assistant-panel';
        panel.innerHTML = `
            <div class="assistant-header">
                <div class="assistant-title">
                    <i data-lucide="sparkles"></i>
                    <h3>AI Assistant</h3>
                </div>
                <button class="btn-icon" onclick="atlassianAI.closeAssistant()">
                    <i data-lucide="x"></i>
                </button>
            </div>

            <div class="chat-messages" id="aiChatMessages">
                <div class="ai-message">
                    <div class="message-avatar">
                        <i data-lucide="bot"></i>
                    </div>
                    <div class="message-content">
                        <p>Hi! I'm your Jira AI assistant. I can help you:</p>
                        <ul>
                            <li>Find issues and create JQL queries</li>
                            <li>Suggest field values</li>
                            <li>Analyze workflows</li>
                            <li>Answer questions about your projects</li>
                        </ul>
                        <p>What would you like to know?</p>
                    </div>
                </div>
            </div>

            <div class="chat-input-container">
                <input type="text" class="chat-input" id="aiChatInput" 
                       placeholder="Ask me anything about Jira..."
                       onkeypress="if(event.key==='Enter') atlassianAI.sendChatMessage()">
                <button class="btn-primary send-btn" onclick="atlassianAI.sendChatMessage()">
                    <i data-lucide="send"></i>
                </button>
            </div>
        `;

        document.body.appendChild(panel);
        if (window.lucide) lucide.createIcons();
    }

    async sendChatMessage() {
        const input = document.getElementById('aiChatInput');
        const message = input.value.trim();
        if (!message) return;

        // Add user message
        this.addChatMessage('user', message);
        input.value = '';

        // Simulate AI response
        await this.simulateAIProcessing();
        
        const response = this.generateChatResponse(message);
        this.addChatMessage('ai', response);
    }

    addChatMessage(sender, content) {
        const messagesContainer = document.getElementById('aiChatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = sender === 'user' ? 'user-message' : 'ai-message';
        
        messageDiv.innerHTML = sender === 'user' ? `
            <div class="message-content">
                <p>${content}</p>
            </div>
            <div class="message-avatar user-avatar">
                <span>You</span>
            </div>
        ` : `
            <div class="message-avatar">
                <i data-lucide="bot"></i>
            </div>
            <div class="message-content">
                <p>${content}</p>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        if (window.lucide) lucide.createIcons();
    }

    generateChatResponse(query) {
        const lowerQuery = query.toLowerCase();
        
        if (lowerQuery.includes('how many') || lowerQuery.includes('count')) {
            return 'You currently have 23 open issues assigned to you. Would you like me to show them?';
        }
        if (lowerQuery.includes('overdue')) {
            return 'You have 3 overdue issues. The oldest is PROJ-45 which is 5 days overdue.';
        }
        if (lowerQuery.includes('sprint')) {
            return 'Sprint 3 is currently active with 18 issues remaining. The sprint ends in 4 days.';
        }
        
        return `I understand you're asking about "${query}". Let me analyze that for you...`;
    }

    // AI SUMMARY GENERATION
    async generateSummary(text) {
        await this.simulateAIProcessing();
        
        // Simple extractive summary
        const sentences = text.split(/[.!?]+/).filter(s => s.trim());
        const summary = sentences.slice(0, 2).join('. ') + '.';
        
        return {
            summary: summary,
            originalLength: text.length,
            summaryLength: summary.length,
            compressionRatio: Math.round((summary.length / text.length) * 100)
        };
    }

    // Helper Methods
    async simulateAIProcessing() {
        return new Promise(resolve => setTimeout(resolve, 1500));
    }

    async generateJQL() {
        const input = document.getElementById('aiJQLInput');
        const query = input.value.trim();
        
        if (!query) {
            alert('Please enter a description');
            return;
        }

        const result = await this.convertNaturalLanguageToJQL(query);
        
        document.getElementById('generatedJQL').textContent = result.jql;
        document.getElementById('aiExplanation').textContent = result.explanation;
        document.getElementById('aiJQLResult').style.display = 'block';
        
        const badge = document.querySelector('.confidence-badge');
        badge.textContent = `${Math.round(result.confidence * 100)}% confidence`;
    }

    fillExample(example) {
        document.getElementById('aiJQLInput').value = example;
    }

    copyJQL() {
        const jql = document.getElementById('generatedJQL').textContent;
        navigator.clipboard.writeText(jql);
        alert('JQL copied to clipboard!');
    }

    useGeneratedJQL() {
        const jql = document.getElementById('generatedJQL').textContent;
        console.log('Using JQL:', jql);
        alert('JQL applied to navigator');
    }

    executeBulkMove(targetProject, issueIds) {
        alert(`Moving ${issueIds.length} issues to ${targetProject}`);
    }

    applySuggestion(field, value) {
        alert(`Applied AI suggestion: ${field} = ${value}`);
    }

    applyTemplate(templateId) {
        alert(`Applying template: ${templateId}`);
    }

    closeAssistant() {
        const panel = document.querySelector('.ai-assistant-panel');
        if (panel) panel.remove();
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.atlassianAI = new AtlassianIntelligence();
});
