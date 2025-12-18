"""
Advanced Analytics and Reporting Service
Comprehensive analytics, business intelligence, and reporting for Bloomberg-style valuation
"""

import asyncio
import logging
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
# Optional imports for advanced features
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False

from io import BytesIO
import base64
from jinja2 import Template
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsMetrics:
    """Comprehensive analytics metrics"""
    total_valuations: int
    average_valuation: float
    total_revenue: float
    user_engagement: float
    market_activity: float
    data_quality_score: float
    system_performance: float
    error_rate: float
    response_time: float
    uptime_percentage: float

@dataclass
class MarketAnalytics:
    """Market analytics and trends"""
    price_trends: Dict[str, Any]
    demand_analysis: Dict[str, Any]
    supply_analysis: Dict[str, Any]
    market_volatility: float
    competitive_analysis: Dict[str, Any]
    regional_analysis: Dict[str, Any]
    seasonal_patterns: Dict[str, Any]

@dataclass
class UserBehaviorAnalytics:
    """User behavior and engagement analytics"""
    active_users: int
    new_users: int
    user_retention: float
    session_duration: float
    feature_usage: Dict[str, Any]
    conversion_rates: Dict[str, Any]
    user_satisfaction: float
    support_tickets: int

@dataclass
class PerformanceKPIs:
    """Performance key performance indicators"""
    system_uptime: float
    response_time_p95: float
    error_rate: float
    throughput: float
    resource_utilization: Dict[str, float]
    scalability_metrics: Dict[str, Any]
    security_metrics: Dict[str, Any]

class AdvancedAnalyticsService:
    """Advanced analytics and reporting service"""
    
    def __init__(self):
        self.analytics_cache = {}
        self.report_templates = {}
        self.chart_configs = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize report templates and chart configurations"""
        # Report templates
        self.report_templates = {
            'executive_summary': self._get_executive_summary_template(),
            'market_analysis': self._get_market_analysis_template(),
            'user_analytics': self._get_user_analytics_template(),
            'performance_report': self._get_performance_report_template(),
            'financial_report': self._get_financial_report_template()
        }
        
        # Chart configurations
        self.chart_configs = {
            'color_scheme': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'],
            'chart_style': 'plotly_white',
            'font_family': 'Arial, sans-serif',
            'title_font_size': 16,
            'axis_font_size': 12
        }
    
    def _create_simple_chart(self, title: str, description: str) -> str:
        """Create a simple HTML chart fallback when advanced libraries are not available"""
        return f"""
        <div style="border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 5px; background: #f9f9f9;">
            <h3 style="color: #333; margin-top: 0;">{title}</h3>
            <p style="color: #666; margin-bottom: 0;">{description}</p>
            <div style="background: #e8f4fd; padding: 10px; margin-top: 10px; border-left: 4px solid #007bff;">
                <small>Advanced charting libraries not available. Install plotly and matplotlib for interactive charts.</small>
            </div>
        </div>
        """
    
    async def generate_comprehensive_analytics(self, 
                                             start_date: datetime, 
                                             end_date: datetime) -> Dict[str, Any]:
        """Generate comprehensive analytics for the specified period"""
        try:
            logger.info(f"Generating comprehensive analytics from {start_date} to {end_date}")
            
            # Generate all analytics components
            metrics = await self._calculate_analytics_metrics(start_date, end_date)
            market_analytics = await self._analyze_market_trends(start_date, end_date)
            user_analytics = await self._analyze_user_behavior(start_date, end_date)
            performance_kpis = await self._calculate_performance_kpis(start_date, end_date)
            
            # Generate visualizations
            charts = await self._generate_analytics_charts(metrics, market_analytics, user_analytics, performance_kpis)
            
            # Compile comprehensive report
            comprehensive_analytics = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'duration_days': (end_date - start_date).days
                },
                'metrics': asdict(metrics),
                'market_analytics': asdict(market_analytics),
                'user_analytics': asdict(user_analytics),
                'performance_kpis': asdict(performance_kpis),
                'charts': charts,
                'insights': await self._generate_insights(metrics, market_analytics, user_analytics, performance_kpis),
                'recommendations': await self._generate_recommendations(metrics, market_analytics, user_analytics, performance_kpis),
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info("Comprehensive analytics generated successfully")
            return comprehensive_analytics
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analytics: {e}")
            raise
    
    async def _calculate_analytics_metrics(self, start_date: datetime, end_date: datetime) -> AnalyticsMetrics:
        """Calculate comprehensive analytics metrics"""
        try:
            # Simulate data retrieval and calculation
            # In production, this would query the database
            await asyncio.sleep(0.1)  # Simulate processing time
            
            return AnalyticsMetrics(
                total_valuations=1250,
                average_valuation=1250000.0,
                total_revenue=15625000.0,
                user_engagement=0.78,
                market_activity=0.85,
                data_quality_score=0.92,
                system_performance=0.95,
                error_rate=0.02,
                response_time=1.2,
                uptime_percentage=99.8
            )
            
        except Exception as e:
            logger.error(f"Error calculating analytics metrics: {e}")
            raise
    
    async def _analyze_market_trends(self, start_date: datetime, end_date: datetime) -> MarketAnalytics:
        """Analyze market trends and patterns"""
        try:
            # Simulate market analysis
            await asyncio.sleep(0.1)
            
            return MarketAnalytics(
                price_trends={
                    'overall_trend': 'rising',
                    'monthly_change': 0.05,
                    'volatility': 0.12,
                    'price_range': [800000, 2000000]
                },
                demand_analysis={
                    'demand_level': 'high',
                    'growth_rate': 0.15,
                    'seasonal_patterns': 'Q4_peak',
                    'regional_variations': {'North': 0.8, 'South': 1.2, 'East': 0.9, 'West': 1.1}
                },
                supply_analysis={
                    'supply_level': 'medium',
                    'inventory_turnover': 0.6,
                    'new_listings': 45,
                    'sold_listings': 38
                },
                market_volatility=0.12,
                competitive_analysis={
                    'market_share': 0.25,
                    'competitor_count': 12,
                    'pricing_position': 'premium'
                },
                regional_analysis={
                    'top_regions': ['Texas', 'California', 'Florida'],
                    'regional_prices': {'Texas': 1200000, 'California': 1500000, 'Florida': 1100000}
                },
                seasonal_patterns={
                    'peak_season': 'Q4',
                    'low_season': 'Q1',
                    'seasonal_variation': 0.2
                }
            )
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {e}")
            raise
    
    async def _analyze_user_behavior(self, start_date: datetime, end_date: datetime) -> UserBehaviorAnalytics:
        """Analyze user behavior and engagement"""
        try:
            # Simulate user behavior analysis
            await asyncio.sleep(0.1)
            
            return UserBehaviorAnalytics(
                active_users=450,
                new_users=85,
                user_retention=0.72,
                session_duration=18.5,
                feature_usage={
                    'valuation_engine': 0.95,
                    'market_data': 0.78,
                    'reports': 0.65,
                    'admin_portal': 0.45
                },
                conversion_rates={
                    'trial_to_paid': 0.35,
                    'visitor_to_trial': 0.12,
                    'feature_adoption': 0.68
                },
                user_satisfaction=4.2,
                support_tickets=23
            )
            
        except Exception as e:
            logger.error(f"Error analyzing user behavior: {e}")
            raise
    
    async def _calculate_performance_kpis(self, start_date: datetime, end_date: datetime) -> PerformanceKPIs:
        """Calculate performance key performance indicators"""
        try:
            # Simulate performance analysis
            await asyncio.sleep(0.1)
            
            return PerformanceKPIs(
                system_uptime=99.8,
                response_time_p95=1.2,
                error_rate=0.02,
                throughput=150.0,
                resource_utilization={
                    'cpu': 0.65,
                    'memory': 0.72,
                    'disk': 0.45,
                    'network': 0.38
                },
                scalability_metrics={
                    'max_concurrent_users': 500,
                    'peak_load_handled': 750,
                    'scaling_events': 3
                },
                security_metrics={
                    'security_score': 0.95,
                    'vulnerabilities': 0,
                    'incidents': 0,
                    'compliance_score': 0.98
                }
            )
            
        except Exception as e:
            logger.error(f"Error calculating performance KPIs: {e}")
            raise
    
    async def _generate_analytics_charts(self, 
                                      metrics: AnalyticsMetrics,
                                      market_analytics: MarketAnalytics,
                                      user_analytics: UserBehaviorAnalytics,
                                      performance_kpis: PerformanceKPIs) -> Dict[str, str]:
        """Generate analytics charts and visualizations"""
        try:
            charts = {}
            
            # Revenue trend chart
            charts['revenue_trend'] = await self._create_revenue_trend_chart()
            
            # Market analysis chart
            charts['market_analysis'] = await self._create_market_analysis_chart(market_analytics)
            
            # User engagement chart
            charts['user_engagement'] = await self._create_user_engagement_chart(user_analytics)
            
            # Performance metrics chart
            charts['performance_metrics'] = await self._create_performance_metrics_chart(performance_kpis)
            
            # Valuation distribution chart
            charts['valuation_distribution'] = await self._create_valuation_distribution_chart()
            
            # Regional analysis chart
            charts['regional_analysis'] = await self._create_regional_analysis_chart(market_analytics)
            
            return charts
            
        except Exception as e:
            logger.error(f"Error generating analytics charts: {e}")
            return {}
    
    async def _create_revenue_trend_chart(self) -> str:
        """Create revenue trend chart"""
        try:
            if not PLOTLY_AVAILABLE:
                return self._create_simple_chart("Revenue Trend", "Revenue data visualization")
            
            # Simulate revenue data
            dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='ME')
            revenue = [1000000 + i * 50000 + np.random.normal(0, 20000) for i in range(len(dates))]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=dates,
                y=revenue,
                mode='lines+markers',
                name='Revenue',
                line=dict(color='#1f77b4', width=3)
            ))
            
            fig.update_layout(
                title='Revenue Trend Analysis',
                xaxis_title='Month',
                yaxis_title='Revenue ($)',
                template='plotly_white',
                font=dict(family="Arial, sans-serif", size=12)
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id="revenue_trend")
            
        except Exception as e:
            logger.error(f"Error creating revenue trend chart: {e}")
            return self._create_simple_chart("Revenue Trend", "Revenue data visualization")
    
    async def _create_market_analysis_chart(self, market_analytics: MarketAnalytics) -> str:
        """Create market analysis chart"""
        try:
            if not PLOTLY_AVAILABLE:
                return self._create_simple_chart("Market Analysis", "Market trends, demand analysis, supply analysis, and regional distribution")
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('Price Trends', 'Demand Analysis', 'Supply Analysis', 'Regional Analysis'),
                specs=[[{"type": "scatter"}, {"type": "bar"}],
                       [{"type": "bar"}, {"type": "pie"}]]
            )
            
            # Price trends
            fig.add_trace(
                go.Scatter(x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                          y=[100, 105, 110, 108, 115, 120],
                          mode='lines+markers',
                          name='Price Index'),
                row=1, col=1
            )
            
            # Demand analysis
            fig.add_trace(
                go.Bar(x=['North', 'South', 'East', 'West'],
                      y=[0.8, 1.2, 0.9, 1.1],
                      name='Demand Level'),
                row=1, col=2
            )
            
            # Supply analysis
            fig.add_trace(
                go.Bar(x=['New Listings', 'Sold Listings', 'Active Listings'],
                      y=[45, 38, 67],
                      name='Supply Metrics'),
                row=2, col=1
            )
            
            # Regional analysis
            fig.add_trace(
                go.Pie(labels=['Texas', 'California', 'Florida', 'Others'],
                      values=[35, 25, 20, 20],
                      name='Regional Distribution'),
                row=2, col=2
            )
            
            fig.update_layout(
                title='Market Analysis Dashboard',
                template='plotly_white',
                font=dict(family="Arial, sans-serif", size=12),
                height=600
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id="market_analysis")
            
        except Exception as e:
            logger.error(f"Error creating market analysis chart: {e}")
            return self._create_simple_chart("Market Analysis", "Market trends, demand analysis, supply analysis, and regional distribution")
    
    async def _create_user_engagement_chart(self, user_analytics: UserBehaviorAnalytics) -> str:
        """Create user engagement chart"""
        try:
            if not PLOTLY_AVAILABLE:
                return self._create_simple_chart("User Engagement", "Feature usage analysis and user satisfaction metrics")
            
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Feature Usage', 'User Metrics'),
                specs=[[{"type": "bar"}, {"type": "indicator"}]]
            )
            
            # Feature usage
            features = list(user_analytics.feature_usage.keys())
            usage = list(user_analytics.feature_usage.values())
            
            fig.add_trace(
                go.Bar(x=features, y=usage, name='Feature Usage'),
                row=1, col=1
            )
            
            # User metrics gauge
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=user_analytics.user_satisfaction,
                    title={'text': "User Satisfaction"},
                    gauge={'axis': {'range': [None, 5]},
                          'bar': {'color': "darkblue"},
                          'steps': [{'range': [0, 2], 'color': "lightgray"},
                                   {'range': [2, 4], 'color': "gray"}],
                          'threshold': {'line': {'color': "red", 'width': 4},
                                      'thickness': 0.75, 'value': 4.5}}),
                row=1, col=2
            )
            
            fig.update_layout(
                title='User Engagement Analytics',
                template='plotly_white',
                font=dict(family="Arial, sans-serif", size=12),
                height=400
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id="user_engagement")
            
        except Exception as e:
            logger.error(f"Error creating user engagement chart: {e}")
            return self._create_simple_chart("User Engagement", "Feature usage analysis and user satisfaction metrics")
    
    async def _create_performance_metrics_chart(self, performance_kpis: PerformanceKPIs) -> str:
        """Create performance metrics chart"""
        try:
            if not PLOTLY_AVAILABLE:
                return self._create_simple_chart("Performance Metrics", "System uptime, response time, resource utilization, and security metrics")
            
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('System Uptime', 'Response Time', 'Resource Utilization', 'Security Score'),
                specs=[[{"type": "indicator"}, {"type": "scatter"}],
                       [{"type": "bar"}, {"type": "indicator"}]]
            )
            
            # System uptime
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=performance_kpis.system_uptime,
                    title={'text': "System Uptime (%)"},
                    gauge={'axis': {'range': [None, 100]},
                          'bar': {'color': "darkgreen"},
                          'steps': [{'range': [0, 95], 'color': "lightgray"},
                                   {'range': [95, 100], 'color': "lightgreen"}],
                          'threshold': {'line': {'color': "red", 'width': 4},
                                      'thickness': 0.75, 'value': 99}}),
                row=1, col=1
            )
            
            # Response time
            fig.add_trace(
                go.Scatter(x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
                          y=[1.1, 1.2, 1.0, 1.3, 1.1],
                          mode='lines+markers',
                          name='Response Time (s)'),
                row=1, col=2
            )
            
            # Resource utilization
            resources = list(performance_kpis.resource_utilization.keys())
            utilization = list(performance_kpis.resource_utilization.values())
            
            fig.add_trace(
                go.Bar(x=resources, y=utilization, name='Resource Utilization'),
                row=2, col=1
            )
            
            # Security score
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=performance_kpis.security_metrics['security_score'] * 100,
                    title={'text': "Security Score (%)"},
                    gauge={'axis': {'range': [None, 100]},
                          'bar': {'color': "darkblue"},
                          'steps': [{'range': [0, 80], 'color': "lightgray"},
                                   {'range': [80, 100], 'color': "lightblue"}],
                          'threshold': {'line': {'color': "red", 'width': 4},
                                      'thickness': 0.75, 'value': 90}}),
                row=2, col=2
            )
            
            fig.update_layout(
                title='Performance Metrics Dashboard',
                template='plotly_white',
                font=dict(family="Arial, sans-serif", size=12),
                height=600
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id="performance_metrics")
            
        except Exception as e:
            logger.error(f"Error creating performance metrics chart: {e}")
            return self._create_simple_chart("Performance Metrics", "System uptime, response time, resource utilization, and security metrics")
    
    async def _create_valuation_distribution_chart(self) -> str:
        """Create valuation distribution chart"""
        try:
            if not PLOTLY_AVAILABLE:
                return self._create_simple_chart("Valuation Distribution", "Distribution analysis of crane valuations")
            
            # Simulate valuation data
            valuations = np.random.normal(1250000, 300000, 1000)
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=valuations,
                nbinsx=30,
                name='Valuation Distribution',
                marker_color='#1f77b4'
            ))
            
            fig.update_layout(
                title='Valuation Distribution Analysis',
                xaxis_title='Valuation Amount ($)',
                yaxis_title='Frequency',
                template='plotly_white',
                font=dict(family="Arial, sans-serif", size=12)
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id="valuation_distribution")
            
        except Exception as e:
            logger.error(f"Error creating valuation distribution chart: {e}")
            return self._create_simple_chart("Valuation Distribution", "Distribution analysis of crane valuations")
    
    async def _create_regional_analysis_chart(self, market_analytics: MarketAnalytics) -> str:
        """Create regional analysis chart"""
        try:
            if not PLOTLY_AVAILABLE:
                return self._create_simple_chart("Regional Analysis", "Regional price analysis and market distribution")
            
            regions = list(market_analytics.regional_analysis['regional_prices'].keys())
            prices = list(market_analytics.regional_analysis['regional_prices'].values())
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=regions,
                y=prices,
                name='Average Regional Prices',
                marker_color='#ff7f0e'
            ))
            
            fig.update_layout(
                title='Regional Price Analysis',
                xaxis_title='Region',
                yaxis_title='Average Price ($)',
                template='plotly_white',
                font=dict(family="Arial, sans-serif", size=12)
            )
            
            return fig.to_html(include_plotlyjs='cdn', div_id="regional_analysis")
            
        except Exception as e:
            logger.error(f"Error creating regional analysis chart: {e}")
            return self._create_simple_chart("Regional Analysis", "Regional price analysis and market distribution")
    
    async def _generate_insights(self, 
                               metrics: AnalyticsMetrics,
                               market_analytics: MarketAnalytics,
                               user_analytics: UserBehaviorAnalytics,
                               performance_kpis: PerformanceKPIs) -> List[str]:
        """Generate actionable insights from analytics data"""
        try:
            insights = []
            
            # Revenue insights
            if metrics.total_revenue > 15000000:
                insights.append("Revenue exceeded target by 15%, indicating strong market demand")
            elif metrics.total_revenue < 10000000:
                insights.append("Revenue below target, consider marketing initiatives")
            
            # User engagement insights
            if user_analytics.user_retention > 0.7:
                insights.append("High user retention rate indicates strong product-market fit")
            else:
                insights.append("User retention below target, focus on user experience improvements")
            
            # Market insights
            if market_analytics.market_volatility < 0.1:
                insights.append("Low market volatility indicates stable pricing environment")
            else:
                insights.append("High market volatility requires careful risk management")
            
            # Performance insights
            if performance_kpis.system_uptime > 99.5:
                insights.append("Excellent system reliability with 99.8% uptime")
            else:
                insights.append("System uptime below target, investigate infrastructure issues")
            
            # Data quality insights
            if metrics.data_quality_score > 0.9:
                insights.append("High data quality score ensures accurate valuations")
            else:
                insights.append("Data quality below target, review data collection processes")
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []
    
    async def _generate_recommendations(self, 
                                     metrics: AnalyticsMetrics,
                                     market_analytics: MarketAnalytics,
                                     user_analytics: UserBehaviorAnalytics,
                                     performance_kpis: PerformanceKPIs) -> List[str]:
        """Generate actionable recommendations from analytics data"""
        try:
            recommendations = []
            
            # Revenue recommendations
            if metrics.total_revenue < 15000000:
                recommendations.append("Implement targeted marketing campaigns to increase user acquisition")
                recommendations.append("Consider premium pricing tiers for advanced features")
            
            # User engagement recommendations
            if user_analytics.user_retention < 0.8:
                recommendations.append("Enhance user onboarding experience to improve retention")
                recommendations.append("Implement user feedback system to identify pain points")
            
            # Market recommendations
            if market_analytics.demand_analysis['demand_level'] == 'high':
                recommendations.append("Scale infrastructure to handle increased demand")
                recommendations.append("Expand market data sources for better coverage")
            
            # Performance recommendations
            if performance_kpis.response_time_p95 > 2.0:
                recommendations.append("Optimize database queries and implement caching")
                recommendations.append("Consider horizontal scaling for better performance")
            
            # Security recommendations
            if performance_kpis.security_metrics['security_score'] < 0.95:
                recommendations.append("Conduct security audit and implement additional safeguards")
                recommendations.append("Enhance monitoring and alerting systems")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def generate_executive_report(self, 
                                      start_date: datetime, 
                                      end_date: datetime) -> str:
        """Generate executive summary report"""
        try:
            analytics = await self.generate_comprehensive_analytics(start_date, end_date)
            
            # Generate executive summary
            executive_summary = {
                'period': analytics['period'],
                'key_metrics': {
                    'total_valuations': analytics['metrics']['total_valuations'],
                    'total_revenue': analytics['metrics']['total_revenue'],
                    'user_engagement': analytics['metrics']['user_engagement'],
                    'system_uptime': analytics['performance_kpis']['system_uptime']
                },
                'top_insights': analytics['insights'][:3],
                'key_recommendations': analytics['recommendations'][:3],
                'generated_at': datetime.now().isoformat()
            }
            
            return json.dumps(executive_summary, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating executive report: {e}")
            return ""
    
    async def generate_market_report(self, 
                                   start_date: datetime, 
                                   end_date: datetime) -> str:
        """Generate market analysis report"""
        try:
            analytics = await self.generate_comprehensive_analytics(start_date, end_date)
            
            market_report = {
                'period': analytics['period'],
                'market_analytics': analytics['market_analytics'],
                'charts': {
                    'market_analysis': analytics['charts'].get('market_analysis', ''),
                    'regional_analysis': analytics['charts'].get('regional_analysis', '')
                },
                'market_insights': [insight for insight in analytics['insights'] if 'market' in insight.lower()],
                'generated_at': datetime.now().isoformat()
            }
            
            return json.dumps(market_report, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating market report: {e}")
            return ""
    
    async def generate_user_analytics_report(self, 
                                           start_date: datetime, 
                                           end_date: datetime) -> str:
        """Generate user analytics report"""
        try:
            analytics = await self.generate_comprehensive_analytics(start_date, end_date)
            
            user_report = {
                'period': analytics['period'],
                'user_analytics': analytics['user_analytics'],
                'charts': {
                    'user_engagement': analytics['charts'].get('user_engagement', '')
                },
                'user_insights': [insight for insight in analytics['insights'] if 'user' in insight.lower()],
                'generated_at': datetime.now().isoformat()
            }
            
            return json.dumps(user_report, indent=2)
            
        except Exception as e:
            logger.error(f"Error generating user analytics report: {e}")
            return ""
    
    def _get_executive_summary_template(self) -> str:
        """Get executive summary report template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Executive Summary - Crane Intelligence Analytics</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #1a1a1a; color: white; padding: 20px; }
                .metric { display: inline-block; margin: 10px; padding: 15px; background: #f5f5f5; border-radius: 5px; }
                .value { font-size: 24px; font-weight: bold; color: #00ff85; }
                .insight { background: #e8f4fd; padding: 10px; margin: 5px 0; border-left: 4px solid #007bff; }
                .recommendation { background: #fff3cd; padding: 10px; margin: 5px 0; border-left: 4px solid #ffc107; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Executive Summary - Crane Intelligence Analytics</h1>
                <p>Period: {{ period.start_date }} to {{ period.end_date }}</p>
            </div>
            
            <div class="section">
                <h2>Key Metrics</h2>
                <div class="metric">
                    <div>Total Valuations</div>
                    <div class="value">{{ metrics.total_valuations }}</div>
                </div>
                <div class="metric">
                    <div>Total Revenue</div>
                    <div class="value">${{ "%.0f"|format(metrics.total_revenue) }}</div>
                </div>
                <div class="metric">
                    <div>User Engagement</div>
                    <div class="value">{{ "%.1f"|format(metrics.user_engagement * 100) }}%</div>
                </div>
                <div class="metric">
                    <div>System Uptime</div>
                    <div class="value">{{ "%.1f"|format(metrics.system_uptime) }}%</div>
                </div>
            </div>
            
            <div class="section">
                <h2>Key Insights</h2>
                {% for insight in insights %}
                <div class="insight">{{ insight }}</div>
                {% endfor %}
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                {% for recommendation in recommendations %}
                <div class="recommendation">{{ recommendation }}</div>
                {% endfor %}
            </div>
        </body>
        </html>
        """
    
    def _get_market_analysis_template(self) -> str:
        """Get market analysis report template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Market Analysis Report - Crane Intelligence</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #1a1a1a; color: white; padding: 20px; }
                .chart-container { margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Market Analysis Report</h1>
                <p>Period: {{ period.start_date }} to {{ period.end_date }}</p>
            </div>
            
            <div class="chart-container">
                {{ charts.market_analysis|safe }}
            </div>
            
            <div class="chart-container">
                {{ charts.regional_analysis|safe }}
            </div>
        </body>
        </html>
        """
    
    def _get_user_analytics_template(self) -> str:
        """Get user analytics report template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>User Analytics Report - Crane Intelligence</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #1a1a1a; color: white; padding: 20px; }
                .chart-container { margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>User Analytics Report</h1>
                <p>Period: {{ period.start_date }} to {{ period.end_date }}</p>
            </div>
            
            <div class="chart-container">
                {{ charts.user_engagement|safe }}
            </div>
        </body>
        </html>
        """
    
    def _get_performance_report_template(self) -> str:
        """Get performance report template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Performance Report - Crane Intelligence</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #1a1a1a; color: white; padding: 20px; }
                .chart-container { margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Performance Report</h1>
                <p>Period: {{ period.start_date }} to {{ period.end_date }}</p>
            </div>
            
            <div class="chart-container">
                {{ charts.performance_metrics|safe }}
            </div>
        </body>
        </html>
        """
    
    def _get_financial_report_template(self) -> str:
        """Get financial report template"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Financial Report - Crane Intelligence</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background: #1a1a1a; color: white; padding: 20px; }
                .chart-container { margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Financial Report</h1>
                <p>Period: {{ period.start_date }} to {{ period.end_date }}</p>
            </div>
            
            <div class="chart-container">
                {{ charts.revenue_trend|safe }}
            </div>
        </body>
        </html>
        """

# Global instance
advanced_analytics_service = AdvancedAnalyticsService()
