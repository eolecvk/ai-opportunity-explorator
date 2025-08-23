import json
import os
from typing import Dict, List, Any

class CatalogManager:
    def __init__(self):
        self.catalog_path = os.path.join(os.path.dirname(__file__), 'data', 'catalog.json')
        self.catalog_data = self._load_catalog()
    
    def _format_currency_range(self, min_cost: int, max_cost: int) -> str:
        """Format currency range with M USD for millions, K for thousands"""
        def format_single(value):
            if value >= 1000:
                return f"${value / 1000:.1f}M USD"
            else:
                return f"${value}K"
        
        min_formatted = format_single(min_cost)
        max_formatted = format_single(max_cost)
        return f"{min_formatted}-{max_formatted}"
    
    def _load_catalog(self) -> Dict[str, List[Dict]]:
        """Load the catalog data from JSON file"""
        try:
            with open(self.catalog_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Catalog file not found at {self.catalog_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing catalog JSON: {e}")
            return {}
    
    def get_available_industries(self) -> List[str]:
        """Get list of available industries in the catalog"""
        return list(self.catalog_data.keys())
    
    def get_projects_for_industry(self, industry: str) -> List[Dict[str, Any]]:
        """Get all projects for a specific industry"""
        return self.catalog_data.get(industry, [])
    
    def filter_projects_by_criteria(self, industry: str, company_size: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Filter and prioritize projects based on company size and priority
        Returns top N projects most suitable for the given criteria
        """
        projects = self.get_projects_for_industry(industry)
        if not projects:
            return []
        
        # Define priority scoring
        priority_scores = {
            'critical': 3,
            'high': 2,
            'medium': 1,
            'low': 0
        }
        
        # Define company size multipliers (larger companies can handle more complex/expensive projects)
        size_multipliers = {
            'startup': 0.5,
            'small': 0.7,
            'medium': 1.0,
            'large': 1.3,
            'enterprise': 1.5
        }
        
        size_multiplier = size_multipliers.get(company_size, 1.0)
        
        # Score each project
        scored_projects = []
        for project in projects:
            # Base priority score
            priority_score = priority_scores.get(project.get('priority', 'medium'), 1)
            
            # Adjust for company size (larger companies get higher scores for expensive projects)
            cost_score = 0
            impl_cost = project.get('implementation_cost', 500)
            if company_size in ['startup', 'small'] and impl_cost > 600:
                cost_score = -1  # Penalty for expensive projects for small companies
            elif company_size in ['large', 'enterprise'] and impl_cost > 800:
                cost_score = 1   # Bonus for complex projects for large companies
            
            # Calculate final score
            final_score = (priority_score + cost_score) * size_multiplier
            
            scored_projects.append({
                **project,
                'relevance_score': final_score
            })
        
        # Sort by score (descending) and return top N
        scored_projects.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_projects[:limit]
    
    def format_project_for_response(self, project: Dict[str, Any], company_size: str) -> Dict[str, Any]:
        """Format a catalog project for API response"""
        # Adjust cost estimates based on company size
        size_multipliers = {
            'startup': 0.7,
            'small': 0.8,
            'medium': 1.0,
            'large': 1.2,
            'enterprise': 1.4
        }
        
        multiplier = size_multipliers.get(company_size, 1.0)
        impl_cost = int(project.get('implementation_cost', 500) * multiplier)
        ongoing_cost = int(project.get('ongoing_cost', 100) * multiplier)
        
        # Estimate ROI range based on priority
        roi_estimates = {
            'critical': '250-400% ROI within 12-18 months',
            'high': '180-300% ROI within 10-15 months',
            'medium': '120-200% ROI within 12-18 months',
            'low': '100-150% ROI within 18-24 months'
        }
        
        # Estimate timeline based on complexity (implementation cost as proxy)
        if impl_cost < 300:
            timeline = '3-5 months'
        elif impl_cost < 600:
            timeline = '4-7 months'
        elif impl_cost < 1000:
            timeline = '6-10 months'
        else:
            timeline = '8-12 months'
        
        result = {
            'title': project.get('title', ''),
            'description': project.get('description', ''),
            'priority': project.get('priority', 'medium').title(),
            'expected_roi': roi_estimates.get(project.get('priority', 'medium'), '150% ROI within 15 months'),
            'timeline': timeline,
            'investment_range': self._format_currency_range(impl_cost, impl_cost + ongoing_cost),
            'business_value': self._generate_business_value(project, company_size),
            'implementation_notes': self._generate_implementation_notes(project)
        }
        
        # Add ROI calculator data if available
        if 'roi_calculator' in project:
            result['roi_calculator'] = project['roi_calculator']
            # Add implementation and ongoing costs to the variables for the formula
            result['roi_calculator']['implementation_cost'] = impl_cost * 1000  # Convert K to actual value
            result['roi_calculator']['ongoing_cost'] = ongoing_cost * 1000
        
        return result
    
    def _generate_business_value(self, project: Dict[str, Any], company_size: str) -> str:
        """Generate business value description based on project and company size"""
        title = project.get('title', '').lower()
        size_benefits = {
            'startup': 'rapid deployment, competitive advantage, scalable foundation',
            'small': 'operational efficiency, cost optimization, growth enablement', 
            'medium': 'process automation, competitive positioning, scalable operations',
            'large': 'enterprise-wide efficiency, advanced analytics, innovation leadership',
            'enterprise': 'transformational impact, industry leadership, comprehensive optimization'
        }
        
        base_benefit = size_benefits.get(company_size, 'operational improvements')
        
        # Add specific benefits based on project type
        if 'fraud' in title:
            return f'Fraud prevention, risk reduction, {base_benefit}'
        elif 'customer' in title:
            return f'Enhanced customer experience, retention improvement, {base_benefit}'
        elif 'risk' in title:
            return f'Risk mitigation, compliance enhancement, {base_benefit}'
        elif 'automation' in title or 'processing' in title:
            return f'Process automation, cost reduction, {base_benefit}'
        else:
            return f'Operational excellence, data-driven insights, {base_benefit}'
    
    def _generate_implementation_notes(self, project: Dict[str, Any]) -> str:
        """Generate implementation notes based on project characteristics"""
        cost = project.get('implementation_cost', 500)
        title = project.get('title', '').lower()
        
        complexity_notes = {
            'low': 'Standard APIs, minimal infrastructure changes, cloud-based deployment',
            'medium': 'System integration required, data pipeline setup, training and change management',
            'high': 'Complex integration, custom development, extensive data preparation and governance'
        }
        
        if cost < 400:
            complexity = 'low'
        elif cost < 800:
            complexity = 'medium'  
        else:
            complexity = 'high'
            
        base_note = complexity_notes[complexity]
        
        # Add specific technical requirements
        if 'ai' in title or 'machine learning' in title:
            return f'{base_note}, ML model development and training'
        elif 'data' in title or 'analytics' in title:
            return f'{base_note}, data warehouse integration'
        elif 'chatbot' in title or 'automation' in title:
            return f'{base_note}, workflow automation setup'
        else:
            return base_note