"""
Protocol Education CI System - Streamlit Web Interface
User-friendly web application for the intelligence system
Enhanced: Added Ofsted deep analysis and vacancy display
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os

from processor_premium import PremiumSchoolProcessor
from exporter import IntelligenceExporter
from cache import IntelligenceCache
from models import ContactType

# Page configuration
st.set_page_config(
    page_title="Protocol Education Research Assistant",
    page_icon="",  # Removed emoji
    layout="wide"
)

# Initialize components
@st.cache_resource
def get_processor():
    return PremiumSchoolProcessor()

@st.cache_resource
def get_exporter():
    return IntelligenceExporter()

@st.cache_resource
def get_cache():
    return IntelligenceCache()

processor = get_processor()
exporter = get_exporter()
cache = get_cache()

# Custom CSS - Clean white background
st.markdown("""
<style>
    .stApp {
        background-color: white;
    }
    .contact-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .competitor-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        display: inline-block;
        margin-right: 0.5rem;
    }
    .confidence-high { color: #00cc00; }
    .confidence-medium { color: #ff9900; }
    .confidence-low { color: #ff0000; }
</style>
""", unsafe_allow_html=True)

# Define all display functions first
def display_school_intelligence(intel):
    """Display school intelligence in Streamlit"""
    
    # Header metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Data Quality", f"{intel.data_quality_score:.0%}")
    with col2:
        st.metric("Contacts Found", len(intel.contacts))
    with col3:
        st.metric("Competitors", len(intel.competitors))
    with col4:
        st.metric("Processing Time", f"{intel.processing_time:.1f}s")
    
    # School info
    st.subheader(f"{intel.school_name}")
    if intel.website:
        st.write(f"[{intel.website}]({intel.website})")
    
    # Tabs for different sections - ENHANCED with new tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Contacts", "Competitors", "Intelligence", "Financial Data", 
        "Ofsted Analysis", "Vacancies", "Raw Data"
    ])
    
    with tab1:
        display_contacts(intel.contacts)
    
    with tab2:
        display_competitors(intel)
    
    with tab3:
        display_conversation_intel(intel)
    
    with tab4:
        display_financial_data(intel)
    
    with tab5:
        display_ofsted_analysis(intel)
    
    with tab6:
        display_vacancies(intel)
    
    with tab7:
        # Show raw data for debugging
        st.json({
            'school_name': intel.school_name,
            'data_quality_score': intel.data_quality_score,
            'sources_checked': intel.sources_checked,
            'contacts_count': len(intel.contacts),
            'competitors_count': len(intel.competitors),
            'has_ofsted_enhanced': hasattr(intel, 'ofsted_enhanced'),
            'has_vacancy_data': hasattr(intel, 'vacancy_data')
        })

def display_contacts(contacts):
    """Display contact information"""
    
    if not contacts:
        st.warning("No contacts found")
        return
    
    # Group by role
    for role in ContactType:
        role_contacts = [c for c in contacts if c.role == role]
        
        if role_contacts:
            st.write(f"**{role.value.replace('_', ' ').title()}**")
            
            for contact in role_contacts:
                confidence_class = (
                    "confidence-high" if contact.confidence_score > 0.8
                    else "confidence-medium" if contact.confidence_score > 0.5
                    else "confidence-low"
                )
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{contact.full_name}**")
                    if contact.email:
                        st.write(f"{contact.email}")
                    if contact.phone:
                        st.write(f"{contact.phone}")
                
                with col2:
                    st.markdown(
                        f'<span class="{confidence_class}">Confidence: {contact.confidence_score:.0%}</span>',
                        unsafe_allow_html=True
                    )
                
                st.divider()

def display_competitors(intel):
    """Display competitor analysis"""
    
    if not intel.competitors:
        st.info("No competitors detected")
        return
    
    st.write("**Detected Competitors:**")
    
    for comp in intel.competitors:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(
                f'<span class="competitor-badge">{comp.agency_name}</span>',
                unsafe_allow_html=True
            )
            st.write(f"Type: {comp.presence_type}")
            
            if comp.weaknesses:
                st.write("Weaknesses:")
                for weakness in comp.weaknesses:
                    st.write(f"  • {weakness}")
        
        with col2:
            st.metric("Confidence", f"{comp.confidence_score:.0%}")
    
    if intel.win_back_strategy:
        st.write("**Win-back Strategy:**")
        st.info(intel.win_back_strategy)
    
    if intel.protocol_advantages:
        st.write("**Protocol Advantages:**")
        for advantage in intel.protocol_advantages:
            st.write(f"✓ {advantage}")

def display_conversation_intel(intel):
    """Display conversation intelligence"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        if intel.ofsted_rating:
            st.write(f"**Ofsted Rating:** {intel.ofsted_rating}")
        
        if intel.recent_achievements:
            st.write("**Recent Achievements:**")
            for achievement in intel.recent_achievements[:5]:
                st.write(f"• {achievement}")
    
    with col2:
        if intel.upcoming_events:
            st.write("**Upcoming Events:**")
            for event in intel.upcoming_events[:5]:
                st.write(f"• {event}")
        
        if intel.leadership_changes:
            st.write("**Leadership Changes:**")
            for change in intel.leadership_changes[:3]:
                st.write(f"• {change}")
    
    if intel.conversation_starters:
        st.write("**Top Conversation Starters:**")
        
        # Show top 5 conversation starters
        for i, starter in enumerate(intel.conversation_starters[:5], 1):
            with st.expander(f"{i}. {starter.topic} (Relevance: {starter.relevance_score:.0%})"):
                st.write(starter.detail)
                if hasattr(starter, 'source_url') and starter.source_url:
                    st.caption(f"Source: {starter.source_url}")

def display_financial_data(intel):
    """Display financial data and recruitment costs - NOW TRUST-AWARE"""
    
    if hasattr(intel, 'financial_data') and intel.financial_data:
        financial = intel.financial_data
        
        if financial.get('error'):
            st.warning(f"Could not retrieve financial data: {financial['error']}")
            return
        
        # Entity info (School or Trust)
        if 'entity_found' in financial:
            entity = financial['entity_found']
            
            # Show if we found trust-level data
            if entity['type'] == 'Trust':
                st.info(f"🏢 Found trust-level financial data for **{entity['name']}** which manages {entity.get('schools_in_trust', 'multiple')} schools including {financial['school_searched']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Entity:** {entity['name']}")
                st.write(f"**Type:** {entity['type']}")
            with col2:
                st.write(f"**URN:** {entity['urn']}")
                st.write(f"**Schools:** {entity.get('schools_in_trust', 'N/A')}")
            with col3:
                st.write(f"**Match Confidence:** {entity.get('confidence', 0):.0%}")
                if entity['type'] == 'Trust':
                    st.write("**Economies of Scale:** ✅")
        
        st.divider()
        
        # Financial data
        if 'financial' in financial and financial['financial']:
            fin_data = financial['financial']
            
            # Recruitment cost estimates (PROMINENT DISPLAY)
            if 'recruitment_estimates' in fin_data:
                st.subheader("🎯 Annual Recruitment Costs")
                
                estimates = fin_data['recruitment_estimates']
                
                if 'total_trust' in estimates:  # Trust-level data
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Trust Total",
                            f"£{estimates['total_trust']:,}",
                            help="Total recruitment spend across all schools"
                        )
                    with col2:
                        st.metric(
                            "Per School Average",
                            f"£{estimates['per_school_avg']:,}",
                            help="Average recruitment cost per school in trust"
                        )
                    with col3:
                        st.metric(
                            "Savings vs Independent",
                            estimates['economies_of_scale_saving'],
                            help="Cost savings from trust-wide recruitment"
                        )
                    
                    if estimates.get('explanation'):
                        st.success(f"💡 {estimates['explanation']}")
                
                else:  # School-level data
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Low Estimate", f"£{estimates['low']:,}")
                    with col2:
                        st.metric("**Best Estimate**", f"£{estimates['midpoint']:,}")
                    with col3:
                        st.metric("High Estimate", f"£{estimates['high']:,}")
            
            # Supply costs
            if 'supply_staff_costs' in fin_data or (fin_data.get('per_school_estimates', {}).get('avg_supply')):
                st.subheader("💰 Supply Staff Costs")
                
                if 'per_school_estimates' in fin_data and fin_data['per_school_estimates'].get('avg_supply'):
                    # Trust breakdown
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric(
                            "Trust Total Supply Costs",
                            f"£{fin_data.get('supply_staff_costs', 0):,}"
                        )
                    with col2:
                        st.metric(
                            "Average Per School",
                            f"£{fin_data['per_school_estimates']['avg_supply']:,}"
                        )
                else:
                    # Single school
                    st.metric(
                        "Annual Supply Costs",
                        f"£{fin_data.get('supply_staff_costs', 0):,}"
                    )
            
            # Total opportunity
            if 'recruitment_estimates' in fin_data and 'supply_staff_costs' in fin_data:
                st.subheader("📊 Total Opportunity")
                
                if 'total_trust' in fin_data['recruitment_estimates']:
                    total = fin_data['recruitment_estimates']['total_trust'] + fin_data.get('supply_staff_costs', 0)
                    st.metric(
                        "Total Trust Temporary Staffing Spend",
                        f"£{total:,}",
                        help="Combined recruitment + supply costs across trust"
                    )
                else:
                    total = fin_data['recruitment_estimates']['midpoint'] + fin_data.get('supply_staff_costs', 0)
                    st.metric(
                        "Total Temporary Staffing Spend",
                        f"£{total:,}",
                        help="Combined recruitment + supply costs"
                    )
            
            # Other financial metrics in expandable section
            with st.expander("📈 Additional Financial Data"):
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'teaching_staff_per_pupil' in fin_data:
                        st.metric(
                            "Teaching Staff Cost",
                            f"£{fin_data['teaching_staff_per_pupil']:,}/pupil"
                        )
                    
                    if 'total_expenditure' in fin_data:
                        st.metric(
                            "Total Expenditure",
                            f"£{fin_data['total_expenditure']:,}"
                        )
                
                with col2:
                    if 'admin_supplies_per_pupil' in fin_data:
                        st.metric(
                            "Admin Supplies",
                            f"£{fin_data['admin_supplies_per_pupil']:,}/pupil"
                        )
                    
                    if 'indirect_employee_expenses' in fin_data:
                        st.metric(
                            "Indirect Employee Expenses",
                            f"£{fin_data['indirect_employee_expenses']:,}"
                        )
            
            # Data source
            if 'source_url' in fin_data:
                st.caption(f"Data source: [FBIT Government Database]({fin_data['source_url']})")
                st.caption(f"Extracted: {fin_data.get('extracted_date', 'N/A')}")
        
        # Insights
        if 'insights' in financial and financial['insights']:
            st.subheader("💡 Key Insights")
            for insight in financial['insights']:
                st.write(f"• {insight}")
        
        # Conversation starters specific to costs
        if 'conversation_starters' in financial and financial['conversation_starters']:
            st.subheader("💬 Cost-Focused Conversation Starters")
            for i, starter in enumerate(financial['conversation_starters'], 1):
                with st.expander(f"Talking Point {i}"):
                    st.write(starter)
        
    else:
        st.info("No financial data available for this school")

def display_ofsted_analysis(intel):
    """Display enhanced Ofsted analysis - ONLY WEAKNESSES/IMPROVEMENTS"""
    
    if hasattr(intel, 'ofsted_enhanced') and intel.ofsted_enhanced:
        ofsted_data = intel.ofsted_enhanced
        
        # Header with rating
        col1, col2, col3 = st.columns(3)
        with col1:
            rating = ofsted_data.get('rating', 'Unknown')
            rating_color = {
                'Outstanding': '🟢',
                'Good': '🟡',
                'Requires Improvement': '🟠',
                'Inadequate': '🔴'
            }
            st.metric("Ofsted Rating", f"{rating_color.get(rating, '')} {rating}")
        with col2:
            if ofsted_data.get('inspection_date'):
                st.metric("Inspection Date", ofsted_data['inspection_date'])
        with col3:
            weaknesses_count = ofsted_data.get('weaknesses_count', 0)
            improvements_count = len(ofsted_data.get('areas_for_improvement', []))
            total_issues = weaknesses_count + improvements_count
            st.metric("Improvements Needed", total_issues)
        
        # Report link
        if ofsted_data.get('report_url'):
            st.write(f"[📄 View Full Ofsted Report]({ofsted_data['report_url']})")
        
        st.divider()
        
        # AREAS FOR IMPROVEMENT - PRIMARY DISPLAY
        areas_for_improvement = ofsted_data.get('areas_for_improvement', [])
        if areas_for_improvement:
            st.error("📋 **AREAS FOR IMPROVEMENT IDENTIFIED BY OFSTED**")
            st.write(f"*The report identifies {len(areas_for_improvement)} specific areas where the school needs to improve:*")
            
            for i, improvement in enumerate(areas_for_improvement, 1):
                with st.container():
                    st.warning(f"**{i}. {improvement}**")
                    
                    # Map to Protocol solution
                    if 'phonics' in improvement.lower() or 'reading' in improvement.lower():
                        st.success("🎯 **Protocol Solution:** We have 12 RWI certified phonics specialists ready to start")
                    elif 'math' in improvement.lower():
                        st.success("🎯 **Protocol Solution:** Our maths specialists have proven track records of 20%+ improvement")
                    elif 'send' in improvement.lower() or 'special' in improvement.lower():
                        st.success("🎯 **Protocol Solution:** Qualified SENCOs and SEND specialists available immediately")
                    elif 'leader' in improvement.lower():
                        st.success("🎯 **Protocol Solution:** Interim leaders who specialize in rapid school improvement")
                    else:
                        st.success("🎯 **Protocol Solution:** We have specialists who can address this specific area")
            
            st.markdown("---")
        
        # CRITICAL WEAKNESSES
        critical_weaknesses = [w for w in ofsted_data.get('critical_weaknesses', []) 
                              if w.get('severity') == 'CRITICAL']
        
        if critical_weaknesses:
            st.error("🚨 **CRITICAL ISSUES REQUIRING IMMEDIATE ACTION**")
            
            for weakness in critical_weaknesses:
                with st.container():
                    st.markdown(f"### ❗ {weakness['area']}")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.write(f"**Problem:** {weakness['problem']}")
                        st.write(f"**Evidence:** _{weakness.get('evidence', 'See report')}_")
                    with col2:
                        st.error(f"Severity: {weakness['severity']}")
                        st.warning(f"Urgency: {weakness.get('urgency', 'Immediate')}")
                    
                    # Protocol solution
                    st.success(f"**🎯 Protocol Solution:** {weakness.get('staffing_solution', 'Specialist teachers available')}")
                    if weakness.get('quantity_needed'):
                        st.info(f"**Estimated staff needed:** {weakness['quantity_needed']}")
                    
                    st.markdown("---")
        
        # HIGH PRIORITY WEAKNESSES
        high_weaknesses = [w for w in ofsted_data.get('critical_weaknesses', []) 
                          if w.get('severity') == 'HIGH']
        
        if high_weaknesses:
            st.warning("⚠️ **HIGH PRIORITY IMPROVEMENTS NEEDED**")
            
            for weakness in high_weaknesses[:5]:  # Show top 5
                with st.expander(f"🔸 {weakness['area']} - {weakness.get('urgency', 'This term')}"):
                    st.write(f"**Issue:** {weakness['problem']}")
                    st.write(f"**Solution needed:** {weakness.get('staffing_solution', 'Specialist support')}")
                    if weakness.get('evidence'):
                        st.caption(f"Report quote: _{weakness['evidence'][:150]}..._")
        
        # SUBJECT-SPECIFIC WEAKNESSES
        subject_weaknesses = ofsted_data.get('subject_specific_weaknesses', {})
        if subject_weaknesses:
            st.subheader("📚 Subject-Specific Improvements Needed")
            
            # Create a grid of subjects with issues
            cols = st.columns(3)
            col_idx = 0
            
            for subject, problems in subject_weaknesses.items():
                if problems:
                    with cols[col_idx % 3]:
                        st.error(f"**{subject.upper()}**")
                        st.write(f"{len(problems)} issues to address")
                        
                        # Show first problem as example
                        if problems and isinstance(problems, list) and len(problems) > 0:
                            st.caption(f"e.g., {problems[0][:80]}...")
                    
                    col_idx += 1
        
        # SEND ISSUES - Always highlight if present
        send_issues = ofsted_data.get('send_weaknesses', [])
        if send_issues:
            st.error("♿ **SEND PROVISION IMPROVEMENTS NEEDED**")
            st.write("Ofsted identified the following SEND improvements required:")
            
            for issue in send_issues[:3]:
                st.write(f"• {issue}")
            
            st.success("**Protocol has a dedicated SEND team ready to help:**")
            st.write("✓ Qualified SENCOs available immediately")
            st.write("✓ SEND-trained teachers and support staff")
            st.write("✓ Experience implementing effective SEND systems")
        
        # LEADERSHIP WEAKNESSES
        leadership_issues = ofsted_data.get('leadership_weaknesses', [])
        if leadership_issues:
            st.warning("👥 **Leadership & Management Improvements Needed**")
            
            for issue in leadership_issues[:3]:
                st.write(f"• {issue}")
            
            st.info("Protocol's leadership solutions include interim heads, deputies, and middle leaders with proven improvement records")
        
        # IMPROVEMENT ROADMAP
        if ofsted_data.get('improvement_roadmap'):
            st.subheader("📋 Improvement Action Timeline")
            
            roadmap = ofsted_data['improvement_roadmap']
            
            # Immediate actions
            if roadmap.get('immediate_actions'):
                st.error(f"**Immediate (This month):** {len(roadmap['immediate_actions'])} critical actions")
                
            # Term priorities  
            if roadmap.get('term_priorities'):
                st.warning(f"**This Term:** {len(roadmap['term_priorities'])} high priority improvements")
                
            # Year plan
            if roadmap.get('year_plan'):
                st.info(f"**This Year:** {len(roadmap['year_plan'])} ongoing improvements")
        
        # MOST URGENT NEEDS - Call to action
        urgent_needs = ofsted_data.get('most_urgent_needs', [])
        if urgent_needs:
            st.markdown("---")
            st.subheader("🎯 **Your Top 3 Staffing Priorities Based on Ofsted**")
            
            for i, need in enumerate(urgent_needs[:3], 1):
                st.success(f"**{i}. {need}**")
            
            st.markdown("### 📞 **Ready to address these Ofsted improvements?**")
            st.info("Protocol Education can provide all the specialists you need to improve rapidly. Let's discuss your improvement plan today.")
        
        # Total recruitment opportunities
        total_opps = ofsted_data.get('total_recruitment_opportunities', 0)
        if total_opps:
            st.metric("Total Recruitment Opportunities from Ofsted Report", total_opps)
        
        # NO STRENGTHS DISPLAY - REMOVED COMPLETELY
    
    else:
        # Fallback to basic Ofsted info
        if intel.ofsted_rating:
            st.info(f"Basic Ofsted data: {intel.ofsted_rating}")
            
            # Suggest what might need improvement based on rating
            if intel.ofsted_rating == "Requires Improvement":
                st.warning("Schools rated 'Requires Improvement' typically need to improve:")
                st.write("• Quality of teaching in core subjects")
                st.write("• Middle leadership effectiveness")  
                st.write("• SEND provision and outcomes")
                st.write("• Curriculum implementation")
                st.write("• Pupil progress tracking")
                
                st.success("Protocol Education specializes in rapid improvement - we have teachers who know exactly what Ofsted wants to see")
            
            elif intel.ofsted_rating == "Inadequate":
                st.error("Schools rated 'Inadequate' urgently need to improve:")
                st.write("• Leadership and management at all levels")
                st.write("• Teaching quality across the curriculum")
                st.write("• Safeguarding procedures and culture")
                st.write("• Pupil outcomes and progress")
                st.write("• Behaviour management systems")
                
                st.success("Protocol has extensive experience supporting schools in special measures - our improvement specialists can start immediately")
                
            elif intel.ofsted_rating == "Good":
                st.info("Even 'Good' schools have areas Ofsted expects to improve:")
                st.write("• Moving from Good to Outstanding requires exceptional teaching")
                st.write("• Curriculum innovation and excellence")
                st.write("• Exceptional SEND provision")
                st.write("• Outstanding leadership at all levels")
                
                st.success("Protocol helps Good schools become Outstanding - let's discuss your ambitions")
                
            if intel.ofsted_date:
                st.write(f"Last inspection: {intel.ofsted_date.strftime('%B %Y')}")
                
        else:
            st.info("No Ofsted data available for this school")

def display_vacancies(intel):
    """Display job vacancy information - NEW FUNCTION"""
    
    if not hasattr(intel, 'vacancy_data') or not intel.vacancy_data:
        st.info("No vacancy data available")
        return
    
    vacancy_data = intel.vacancy_data
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Vacancies", vacancy_data['total_found'])
    with col2:
        st.metric("Senior Roles", vacancy_data['senior_roles'])
    with col3:
        urgency = vacancy_data['analysis']['urgency_level']
        urgency_color = {
            'high': '🔴',
            'medium': '🟡', 
            'low': '🟢'
        }
        st.metric("Urgency Level", f"{urgency_color.get(urgency, '')} {urgency.title()}")
    with col4:
        st.metric("Last Checked", datetime.now().strftime('%H:%M'))
    
    st.divider()
    
    # Vacancy list
    if vacancy_data.get('vacancies'):
        st.subheader("🔍 Active Job Vacancies")
        
        # Note: Full vacancy objects aren't serialized, so show summary
        st.info(f"Found {vacancy_data['total_found']} active vacancies across school website and job boards")
        
        # Show analysis insights instead
        analysis = vacancy_data.get('analysis', {})
        
        if analysis.get('subjects_needed'):
            st.write("**Subjects with vacancies:**")
            for subject in analysis['subjects_needed']:
                st.write(f"• {subject}")
        
        if analysis.get('contract_types'):
            st.write("**Contract types:**")
            for contract, count in analysis['contract_types'].items():
                st.write(f"• {contract.title()}: {count}")
    
    # Competitor activity in job postings
    if vacancy_data.get('analysis', {}).get('competitors_active'):
        st.subheader("🏢 Competitor Activity")
        st.warning("The following agencies are already advertising for this school:")
        for competitor in vacancy_data['analysis']['competitors_active']:
            st.write(f"• {competitor}")
        st.info("Protocol Education can offer more competitive rates and better service")
    
    # Recruitment challenges
    if vacancy_data.get('analysis', {}).get('recruitment_challenges'):
        st.subheader("⚠️ Recruitment Challenges Identified")
        for challenge in vacancy_data['analysis']['recruitment_challenges']:
            st.warning(challenge)
    
    # Vacancy-based conversation starters are already in main conversation starters
    st.info("💡 Vacancy-specific conversation starters have been added to the Intelligence tab")
        
def display_borough_summary(results):
    """Display borough sweep summary"""
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    high_quality = sum(1 for r in results if r.data_quality_score > 0.7)
    with_contacts = sum(1 for r in results if r.contacts)
    with_competitors = sum(1 for r in results if r.competitors)
    avg_quality = sum(r.data_quality_score for r in results) / len(results) if results else 0
    
    with col1:
        st.metric("Schools Processed", len(results))
    with col2:
        st.metric("High Quality Data", f"{high_quality}/{len(results)}")
    with col3:
        st.metric("With Contacts", with_contacts)
    with col4:
        st.metric("Avg Quality", f"{avg_quality:.0%}")
    
    # Results table
    st.subheader("Results Overview")
    
    df_data = []
    for intel in results:
        deputy = next((c for c in intel.contacts if c.role == ContactType.DEPUTY_HEAD), None)
        
        df_data.append({
            'School': intel.school_name,
            'Quality': f"{intel.data_quality_score:.0%}",
            'Deputy Head': deputy.full_name if deputy else '',
            'Has Email': '✓' if deputy and deputy.email else '',
            'Has Phone': '✓' if deputy and deputy.phone else '',
            'Competitors': len(intel.competitors),
            'Ofsted': intel.ofsted_rating or 'Unknown'
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)

# Header
st.title("Protocol Education Research Assistant")
st.markdown("**Intelligent school research and contact discovery system**")

# Sidebar
with st.sidebar:
    st.header("Controls")
    
    operation_mode = st.radio(
        "Operation Mode",
        ["Single School", "Borough Sweep"]
    )
    
    export_format = st.selectbox(
        "Export Format",
        ["Excel (.xlsx)", "CSV (.csv)", "JSON (.json)"]
    )
    
    st.divider()
    
    # Feature toggles
    st.subheader("Features")
    enable_ofsted = st.checkbox("Enhanced Ofsted Analysis", value=True)
    enable_vacancies = st.checkbox("Vacancy Detection", value=True)
    
    st.divider()
    
    # Cache stats
    if st.button("Show Cache Stats"):
        stats = cache.get_stats()
        st.metric("Active Entries", stats.get('active_entries', 0))
        st.metric("Hit Rate", f"{stats.get('hit_rate', 0):.1%}")
        st.metric("Cache Size", f"{stats.get('cache_size_mb', 0)} MB")
    
    if st.button("Clear Cache"):
        cache.clear_expired()
        st.success("Cache cleared!")
    
    st.divider()
    
    # API usage
    usage = processor.ai_engine.get_usage_report()
    st.metric("API Cost Today", f"${usage['total_cost']:.3f}")
    st.metric("Cost per School", f"${usage['cost_per_school']:.3f}")
    
    # Show search and GPT costs separately
    with st.expander("Cost Breakdown"):
        st.write(f"Searches: {usage['searches']} (${usage['search_cost']:.3f})")
        st.write(f"GPT-4: {usage['tokens_used']} tokens (${usage['gpt_cost']:.3f})")

# Main content area
if operation_mode == "Single School":
    st.header("Single School Lookup")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        school_name = st.text_input("School Name", placeholder="e.g., St Mary's Primary School")
        website_url = st.text_input("Website URL (optional)", placeholder="https://...")
    
    with col2:
        force_refresh = st.checkbox("Force Refresh", help="Ignore cached data")
        
    if st.button("Search School", type="primary"):
        if school_name:
            with st.spinner(f"Processing {school_name}..."):
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Update processor features based on toggles
                processor.ENABLE_OFSTED_ENHANCEMENT = enable_ofsted
                processor.ENABLE_VACANCY_DETECTION = enable_vacancies
                
                # Process school
                status_text.text("Finding school website...")
                progress_bar.progress(20)
                
                intel = processor.process_single_school(
                    school_name, 
                    website_url,
                    force_refresh
                )
                
                progress_bar.progress(100)
                status_text.text("Complete!")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
            
            # Display results
            display_school_intelligence(intel)
            
            # Export button
            if st.button("Export Results"):
                format_map = {
                    "Excel (.xlsx)": "xlsx",
                    "CSV (.csv)": "csv",
                    "JSON (.json)": "json"
                }
                filepath = exporter.export_single_school(
                    intel, 
                    format_map[export_format]
                )
                st.success(f"Exported to: {filepath}")

elif operation_mode == "Borough Sweep":
    st.header("Borough-wide Intelligence Sweep")
    
    col1, col2 = st.columns(2)
    
    with col1:
        borough_name = st.text_input("Borough Name", placeholder="e.g., Camden, Westminster")
    
    with col2:
        school_type = st.selectbox("School Type", ["All", "Primary", "Secondary"])
    
    if st.button("Start Borough Sweep", type="primary"):
        if borough_name:
            with st.spinner(f"Processing {borough_name} schools..."):
                # Update processor features based on toggles
                processor.ENABLE_OFSTED_ENHANCEMENT = enable_ofsted
                processor.ENABLE_VACANCY_DETECTION = enable_vacancies
                
                # Process borough
                results = processor.process_borough(
                    borough_name,
                    school_type.lower()
                )
            
            st.success(f"Processed {len(results)} schools!")
            
            # Display summary
            display_borough_summary(results)
            
            # Export button
            if st.button("Export All Results"):
                format_map = {
                    "Excel (.xlsx)": "xlsx",
                    "CSV (.csv)": "csv",
                    "JSON (.json)": "json"
                }
                filepath = exporter.export_borough_results(
                    results,
                    borough_name,
                    format_map[export_format]
                )
                st.success(f"Exported to: {filepath}")

if __name__ == "__main__":
    # Ensure .env file exists
    if not os.path.exists('.env'):
        st.error("Please create a .env file with your OPENAI_API_KEY and SERPER_API_KEY")
        st.code("""OPENAI_API_KEY=your-openai-api-key-here
SERPER_API_KEY=your-serper-api-key-here
SCRAPER_API_KEY=your-scraper-api-key-here  # Optional""")
        st.stop()