"""
Department extraction utility - Maps roles to departments
"""

# Department mapping based on role prefixes
DEPARTMENT_MAPPING = {
    # Software & Development
    'software': 'Software',
    'frontend': 'Software',
    'backend': 'Software',
    'fullstack': 'Software',
    'web': 'Web Development',
    'mobile': 'Mobile',
    'android': 'Android',
    'ios': 'iOS',
    'cross_platform': 'Mobile',
    
    # Embedded & Hardware
    'embedded': 'Embedded',
    'firmware': 'Firmware',
    'bsp': 'BSP/Linux',
    'linux_bsp': 'BSP/Linux',
    'hardware': 'Hardware',
    'pcb': 'Hardware',
    'fpga': 'Hardware',
    'rf': 'Hardware',
    'power': 'Hardware',
    
    # Mechanical
    'mechanical': 'Mechanical',
    'cad': 'Mechanical',
    'thermal': 'Mechanical',
    'manufacturing': 'Manufacturing',
    
    # AI/ML & Data
    'ml': 'AI/ML',
    'machine_learning': 'AI/ML',
    'ai': 'AI/ML',
    'data_science': 'Data Science',
    'data_engineer': 'Data Engineering',
    
    # DevOps & Infrastructure
    'devops': 'DevOps',
    'cloud': 'Cloud/Infrastructure',
    'sre': 'DevOps',
    'infrastructure': 'Cloud/Infrastructure',
    'security': 'Security',
    
    # Quality Assurance
    'qa': 'QA',
    'test': 'QA',
    'automation': 'QA',
    'performance': 'QA',
    
    # Design & Product
    'design': 'Design',
    'ux': 'Design',
    'ui': 'Design',
    'product': 'Product',
    
    # Business & Sales
    'sales': 'Sales',
    'marketing': 'Marketing',
    'customer': 'Customer Success',
    'vendor': 'Vendor Management',
    'hr': 'HR',
    'finance': 'Finance',
    'operations': 'Operations',
    'admin': 'Administration',
    
    # Management
    'project_manager': 'Project Management',
    'program_manager': 'Program Management',
    'director': 'Leadership',
    'vp': 'Leadership',
    'cto': 'Leadership',
    'ceo': 'Leadership',
}

# Core team colors
DEPARTMENT_COLORS = {
    'Software': '#3B82F6',  # Blue
    'Web Development': '#6366F1',  # Indigo
    'Mobile': '#8B5CF6',  # Violet
    'Android': '#10B981',  # Green
    'iOS': '#6B7280',  # Gray
    'Embedded': '#F59E0B',  # Amber
    'Firmware': '#EF4444',  # Red
    'BSP/Linux': '#F97316',  # Orange
    'Hardware': '#EAB308',  # Yellow
    'Mechanical': '#84CC16',  # Lime
    'Manufacturing': '#22C55E',  # Green
    'AI/ML': '#EC4899',  # Pink
    'Data Science': '#D946EF',  # Fuchsia
    'Data Engineering': '#A855F7',  # Purple
    'DevOps': '#14B8A6',  # Teal
    'Cloud/Infrastructure': '#06B6D4',  # Cyan
    'Security': '#DC2626',  # Red
    'QA': '#7C3AED',  # Violet
    'Design': '#F472B6',  # Pink
    'Product': '#FB923C',  # Orange
    'Sales': '#22D3EE',  # Cyan
    'Marketing': '#C084FC',  # Purple
    'Customer Success': '#4ADE80',  # Green
    'Vendor Management': '#FBBF24',  # Amber
    'HR': '#F87171',  # Red
    'Finance': '#60A5FA',  # Blue
    'Operations': '#A78BFA',  # Violet
    'Administration': '#9CA3AF',  # Gray
    'Project Management': '#FB7185',  # Rose
    'Program Management': '#E879F9',  # Fuchsia
    'Leadership': '#FACC15',  # Yellow
}

def get_department_from_role(role: str) -> str:
    """
    Extract department from a role string.
    
    Examples:
        software_engineer_l1 -> Software
        hardware_team_lead -> Hardware
        android_engineer_l2 -> Android
        mechanical_designer_l3 -> Mechanical
        ml_engineer_l1 -> AI/ML
        sales_manager -> Sales
    """
    if not role:
        return None
    
    role_lower = role.lower()
    
    # Check each prefix in order (longer prefixes first for better matching)
    sorted_prefixes = sorted(DEPARTMENT_MAPPING.keys(), key=len, reverse=True)
    
    for prefix in sorted_prefixes:
        if role_lower.startswith(prefix):
            return DEPARTMENT_MAPPING[prefix]
    
    # Special cases for roles that contain department name anywhere
    for prefix, department in DEPARTMENT_MAPPING.items():
        if prefix in role_lower:
            return department
    
    # Default to General if no match
    return 'General'


def get_department_color(department: str) -> str:
    """Get the color for a department."""
    return DEPARTMENT_COLORS.get(department, '#6366F1')


def get_all_departments() -> list:
    """Get list of all unique departments."""
    return sorted(set(DEPARTMENT_MAPPING.values()))


def get_core_teams_config() -> list:
    """Get configuration for all core teams to be created."""
    departments = get_all_departments()
    return [
        {
            'name': f'{dept} Team',
            'department': dept,
            'color': get_department_color(dept),
            'is_core_team': True,
            'team_type': 'core'
        }
        for dept in departments
    ]
