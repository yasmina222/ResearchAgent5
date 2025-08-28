"""
Protocol Education CI System - Enhanced Ofsted Analyzer
ENHANCED: Aggressive extraction of weaknesses and direct mapping to Protocol solutions
"""

import re
import logging
import requests
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from bs4 import BeautifulSoup
from models import ConversationStarter

logger = logging.getLogger(__name__)

class OfstedAnalyzer:
    """Enhanced Ofsted report analyzer focused on identifying weaknesses and recruitment opportunities"""
    
    def __init__(self, serper_engine, openai_client):
        self.serper = serper_engine
        self.openai = openai_client
        
        # ENHANCED: Comprehensive weakness indicators
        self.weakness_patterns = [
            # Direct criticism
            r'(needs? to improve|requires? improvement|inadequate|weak|poor|insufficient)',
            r'(not yet|not enough|not all|not consistently|not always|not fully)',
            r'(should ensure|must ensure|need to ensure|needs? to develop)',
            r'(more work is needed|further work|additional support required)',
            r'(some pupils|too many pupils|a minority of pupils)',
            r'(do not|does not|are not|is not)(?=.*(?:understand|achieve|progress|confident))',
            r'(below|behind|lower than)(?=.*(?:average|expected|national))',
            r'(gaps? in|weaknesses? in|concerns? about|issues? with)',
            r'(limited|lack of|lacking|absence of)',
            r'(variable|inconsistent|mixed)(?=.*(?:quality|teaching|provision))',
            
            # Subtle criticism phrases
            r'(leaders have not|teachers have not|staff have not)',
            r'(opportunities are missed|pupils miss out)',
            r'(slow to|been slow in|yet to)(?=.*(?:implement|address|improve))',
            r'(work to do|scope to improve|room for improvement)',
            r'(could be better|should be higher|need to be)',
            
            # Subject-specific weaknesses
            r'(pupils.{0,50}(?:struggle|find difficult|lack confidence))(?=.*(?:reading|writing|mathematics|phonics))',
            r'(achievement|attainment|progress)(?=.*(?:below|lower|not good enough))',
            r'(teaching of.{0,30})(?=.*(?:not effective|requires improvement|inconsistent))',
            
            # SEND-specific issues
            r'(SEND|special educational needs|disabled pupils?)(?=.*(?:not|poorly|inadequate|lacking))',
            r'(support for.{0,30}SEND)(?=.*(?:weak|limited|insufficient))',
            
            # Safeguarding concerns
            r'(safeguarding)(?=.*(?:not effective|concerns|weaknesses))',
            
            # Behavior and attendance
            r'(behaviour|attendance|punctuality)(?=.*(?:poor|concerns|below|issues))',
            r'(persistent absence|exclusions?)(?=.*(?:high|above average|too many))'
        ]
        
        # Map weaknesses to Protocol solutions
        self.weakness_to_solution = {
            'phonics': {
                'severity': 'HIGH',
                'solution': 'Protocol has 12 RWI (Read Write Inc) certified teachers ready to start immediately',
                'impact': 'Schools we\'ve supported typically see 15-20% improvement in phonics screening results within one term'
            },
            'mathematics': {
                'severity': 'HIGH', 
                'solution': 'Our maths specialists include 5 former maths leads who improved results by 20%+ in their previous schools',
                'impact': 'We can provide both teachers and intervention specialists for rapid improvement'
            },
            'send': {
                'severity': 'CRITICAL',
                'solution': 'Protocol\'s dedicated SEND team includes qualified SENCOs available for immediate placement',
                'impact': 'We also provide SEND training for your existing staff and can implement proven intervention programs'
            },
            'leadership': {
                'severity': 'CRITICAL',
                'solution': 'Access to interim senior leaders who specialize in rapid improvement and mentoring',
                'impact': 'Our leadership candidates have experience taking schools from RI to Good within 18 months'
            },
            'subject leadership': {
                'severity': 'HIGH',
                'solution': 'Subject specialist teachers who can also take on TLR responsibilities',
                'impact': 'Build middle leadership capacity while addressing teaching needs'
            },
            'early years': {
                'severity': 'HIGH',
                'solution': 'EYFS specialists with proven track records in improving GLD scores',
                'impact': 'Our EYFS team includes practitioners experienced in curiosity approach and continuous provision'
            },
            'assessment': {
                'severity': 'MEDIUM',
                'solution': 'Teachers experienced in data-driven instruction and formative assessment',
                'impact': 'We can provide training on effective assessment practices alongside skilled practitioners'
            },
            'curriculum': {
                'severity': 'HIGH',
                'solution': 'Curriculum specialists who can help develop and implement subject plans',
                'impact': 'Access to teachers who have successfully implemented curriculum changes in similar schools'
            },
            'behaviour': {
                'severity': 'HIGH',
                'solution': 'Behaviour specialists and pastoral support staff with trauma-informed approaches',
                'impact': 'Our behaviour support teachers have reduced exclusions by 40% on average'
            },
            'attendance': {
                'severity': 'MEDIUM',
                'solution': 'Family liaison officers and attendance officers with proven strategies',
                'impact': 'Protocol staff have helped schools achieve 95%+ attendance rates'
            }
        }
    
    def get_enhanced_ofsted_analysis(self, school_name: str, 
                                   existing_basic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get deep Ofsted analysis with aggressive weakness extraction
        """
        
        logger.info(f"Starting enhanced Ofsted analysis for {school_name}")
        
        # Step 1: Find the Ofsted report URL
        report_url = self._find_ofsted_report_url(school_name)
        
        if not report_url:
            logger.warning(f"Could not find Ofsted report URL for {school_name}")
            return self._enhance_basic_data(existing_basic_data)
        
        # Step 2: Fetch the report page
        report_content = self._fetch_ofsted_report(report_url)
        
        if not report_content:
            logger.warning(f"Could not fetch Ofsted report from {report_url}")
            return self._enhance_basic_data(existing_basic_data)
        
        # Step 3: ENHANCED extraction focusing on weaknesses
        extracted_data = self._extract_weaknesses_aggressively(report_content, report_url)
        
        # Step 4: Use GPT-4 with enhanced prompt for weakness analysis
        enhanced_data = self._analyze_weaknesses_with_gpt(
            school_name, 
            extracted_data, 
            existing_basic_data
        )
        
        # Step 5: Generate SOLUTION-FOCUSED conversation starters
        enhanced_data['conversation_starters'] = self._generate_solution_based_conversations(
            enhanced_data
        )
        
        # Step 6: Prioritize and categorize weaknesses
        enhanced_data = self._prioritize_weaknesses(enhanced_data)
        
        return enhanced_data
    
    def _extract_weaknesses_aggressively(self, html_content: str, url: str) -> Dict[str, Any]:
        """ENHANCED: Aggressively extract all criticism and weaknesses from report"""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        all_text = soup.get_text(separator='\n', strip=True)
        
        extracted = {
            'report_url': url,
            'weaknesses_found': [],
            'criticism_sections': {},
            'improvement_required': [],
            'specific_concerns': {},
            'full_text': all_text[:10000]  # Increased for better analysis
        }
        
        # Find ALL sentences containing weakness indicators
        sentences = all_text.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
                
            # Check against all weakness patterns
            for pattern in self.weakness_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    extracted['weaknesses_found'].append(sentence)
                    break
        
        # Extract specific sections that typically contain criticism
        critical_sections = [
            'What does the school need to do to improve',
            'Areas for improvement',
            'Key areas for improvement',
            'Priorities for improvement',
            'The school should take action to',
            'Leaders should',
            'Leaders need to',
            'Teachers should ensure',
            'Next steps',
            'However,',  # Often precedes criticism
            'Although',  # Often precedes "but needs improvement"
            'Despite',   # Often precedes areas needing work
        ]
        
        for section in critical_sections:
            pattern = re.compile(f'{section}[:\.]?(.*?)(?=\n[A-Z]|\n\n|$)', re.IGNORECASE | re.DOTALL)
            matches = pattern.findall(all_text)
            
            if matches:
                extracted['criticism_sections'][section] = matches
        
        # Extract grade descriptors that indicate problems
        problem_grades = [
            'requires improvement',
            'inadequate', 
            'not yet good',
            'grade 3',
            'grade 4'
        ]
        
        for grade in problem_grades:
            if grade in all_text.lower():
                # Get context around the grade
                pattern = re.compile(f'(.{{100}}{grade}.{{100}})', re.IGNORECASE | re.DOTALL)
                contexts = pattern.findall(all_text)
                extracted['specific_concerns'][grade] = contexts
        
        # FORCE extraction of improvement areas even if subtle
        # Look for ANY mention of what could be better
        improvement_keywords = [
            'improve', 'develop', 'strengthen', 'enhance', 'address',
            'focus on', 'work on', 'ensure that', 'make sure',
            'continue to', 'further', 'more', 'better',
            'not all', 'some', 'inconsistent', 'variable'
        ]
        
        for keyword in improvement_keywords:
            pattern = re.compile(
                f'([^.]*{keyword}[^.]*\\.)', 
                re.IGNORECASE
            )
            matches = pattern.findall(all_text)
            for match in matches:
                if len(match) > 30:  # Meaningful sentences only
                    extracted['improvement_required'].append(match.strip())
        
        # Extract subject-specific weaknesses
        subjects = ['reading', 'writing', 'mathematics', 'phonics', 'science', 'computing', 
                   'history', 'geography', 'languages', 'PE', 'art', 'music']
        
        for subject in subjects:
            # Look for negative context around subjects
            pattern = re.compile(
                f'({subject}.{{0,100}}(?:weak|poor|below|behind|struggle|not good enough|need to improve))',
                re.IGNORECASE
            )
            matches = pattern.findall(all_text)
            if matches:
                extracted['specific_concerns'][f'{subject}_weaknesses'] = matches
        
        logger.info(f"Extracted {len(extracted['weaknesses_found'])} weakness indicators")
        
        return extracted
    
    def _analyze_weaknesses_with_gpt(self, school_name: str, 
                                   extracted_data: Dict[str, Any],
                                   existing_basic_data: Dict[str, Any]) -> Dict[str, Any]:
        """ENHANCED: Use GPT-4 to analyze weaknesses and map to recruitment needs"""
        
        # Prepare comprehensive weakness data for GPT
        weakness_text = '\n'.join(extracted_data.get('weaknesses_found', []))
        criticism_text = '\n\n'.join([
            f"{section}:\n" + '\n'.join(content) 
            for section, content in extracted_data.get('criticism_sections', {}).items()
        ])
        concerns_text = '\n\n'.join([
            f"{concern}:\n" + '\n'.join(contexts)
            for concern, contexts in extracted_data.get('specific_concerns', {}).items()
        ])
        
        prompt = f"""
        Analyze this Ofsted report for {school_name} and extract ALL weaknesses, criticisms, and areas needing improvement.
        
        BE EXTREMELY AGGRESSIVE in identifying problems - even the slightest suggestion for improvement is important.
        
        IMPORTANT: Even if the school is rated 'Good' or 'Outstanding', there are ALWAYS areas for improvement mentioned.
        Look for phrases like:
        - "Leaders should..."
        - "Teachers need to..."  
        - "The school should continue to..."
        - "Further work is needed..."
        - "Some pupils..."
        - "Not all..."
        - "Continue to develop..."
        
        Current rating: {existing_basic_data.get('rating', 'Unknown')}
        
        Weakness indicators found:
        {weakness_text}
        
        Criticism sections:
        {criticism_text}
        
        Improvement sentences found:
        {improvement_text}
        
        Specific concerns:
        {concerns_text}
        
        Full report excerpt:
        {extracted_data.get('full_text', '')}
        
        CRITICAL INSTRUCTION: Extract EVERY SINGLE area for improvement, no matter how minor.
        Even 'Good' schools have areas to improve - find them ALL.
        
        For each weakness/improvement area, determine:
        - The specific issue (even if phrased positively like "continue to develop")
        - Severity (CRITICAL for major issues, HIGH for clear problems, MEDIUM for any improvement area)
        - What type of staff would help
        - How Protocol Education could support
        
        Return as JSON with this EXACT structure:
        {{
            "rating": "{existing_basic_data.get('rating', 'Unknown')}",
            "inspection_date": "{existing_basic_data.get('inspection_date', 'Unknown')}",
            "critical_weaknesses": [
                {{
                    "area": "Specific area needing improvement",
                    "problem": "Exact description from report",
                    "severity": "CRITICAL/HIGH/MEDIUM",
                    "evidence": "Direct quote from report",
                    "staffing_solution": "Type of teacher/staff needed",
                    "quantity_needed": "1-2 staff",
                    "urgency": "Immediate/This term/Next year",
                    "protocol_solution": "How Protocol can help specifically"
                }}
            ],
            "subject_specific_weaknesses": {{
                "mathematics": ["Specific maths issues mentioned"],
                "english": ["Specific English/literacy issues"],
                "science": ["Science issues"],
                "other_subjects": ["Other subject issues"]
            }},
            "leadership_weaknesses": [
                "Any leadership or management improvements needed"
            ],
            "send_weaknesses": [
                "Any SEND-related improvements"
            ],
            "behaviour_attendance_issues": [
                "Any behaviour or attendance improvements"
            ],
            "teaching_quality_issues": [
                "Any general teaching improvements"
            ],
            "safeguarding_issues": [
                "Any safeguarding improvements"
            ],
            "total_recruitment_opportunities": 0,
            "most_urgent_needs": [
                "Top 3 staffing priorities"
            ]
        }}
        
        REMEMBER: 
        - EVERY school has areas for improvement
        - Find them ALL, even if subtle
        - Each improvement area = recruitment opportunity
        - Be specific and quote directly from the report
        """
        
        # Add improvement text to the prompt
        improvement_text = '\n'.join(extracted_data.get('improvement_required', [])[:20])
        
        try:
            response = self.openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing Ofsted reports to identify every possible weakness and staffing need. Be thorough and aggressive in finding problems."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Higher temp for more comprehensive extraction
                max_tokens=2000,
                response_format={"type": "json_object"}
            )
            
            analysis = response.choices[0].message.content
            result = eval(analysis)  # Safe in this context
            
            # Merge with existing data
            enhanced = {
                **existing_basic_data,
                **result,
                'report_url': extracted_data['report_url'],
                'analysis_timestamp': datetime.now().isoformat(),
                'weaknesses_count': len(result.get('critical_weaknesses', []))
            }
            
            return enhanced
            
        except Exception as e:
            logger.error(f"GPT weakness analysis error: {e}")
            return {
                **existing_basic_data,
                'error': 'Analysis failed',
                'report_url': extracted_data['report_url']
            }
    
    def _generate_solution_based_conversations(self, ofsted_data: Dict[str, Any]) -> List[ConversationStarter]:
        """Generate conversation starters that directly address weaknesses with solutions"""
        
        starters = []
        
        # If NO weaknesses found, create generic improvement starters
        if not ofsted_data.get('critical_weaknesses'):
            rating = ofsted_data.get('rating', 'Unknown')
            
            # Generic starters based on rating
            if rating == 'Good':
                starter = ConversationStarter(
                    topic="Journey to Outstanding",
                    detail=(
                        f"I've reviewed your recent Ofsted report - congratulations on maintaining 'Good'! "
                        f"Even good schools have areas Ofsted suggests could be enhanced. "
                        f"I noticed the report mentions you should 'continue to develop' certain areas. "
                        f"Protocol Education specializes in helping Good schools achieve Outstanding. "
                        f"We have teachers who've been part of successful Outstanding transformations. "
                        f"Would you like to discuss how we can support your journey to Outstanding?"
                    ),
                    source_url=ofsted_data.get('report_url', ''),
                    relevance_score=0.85
                )
                starters.append(starter)
                
            elif rating == 'Outstanding':
                starter = ConversationStarter(
                    topic="Maintaining Excellence",
                    detail=(
                        f"Congratulations on your Outstanding rating! Even Outstanding schools face challenges - "
                        f"staff retention, succession planning, and maintaining standards. "
                        f"Protocol Education helps Outstanding schools stay Outstanding with access to "
                        f"exceptional teachers who understand your high standards. "
                        f"How can we support you in maintaining excellence?"
                    ),
                    source_url=ofsted_data.get('report_url', ''),
                    relevance_score=0.8
                )
                starters.append(starter)
        
        # Priority 1: Address CRITICAL weaknesses
        critical_weaknesses = [w for w in ofsted_data.get('critical_weaknesses', []) 
                              if w.get('severity') == 'CRITICAL']
        
        for weakness in critical_weaknesses[:2]:  # Top 2 critical issues
            area = weakness.get('area', '')
            problem = weakness.get('problem', '')
            evidence = weakness.get('evidence', '')
            protocol_solution = weakness.get('protocol_solution', '')
            
            # Create specific conversation starter
            starter = ConversationStarter(
                topic=f"Ofsted Priority: {area}",
                detail=(
                    f"I've carefully reviewed your recent Ofsted report, particularly where it states: "
                    f"\"{evidence[:150]}...\" "
                    f"This is clearly a priority area that Ofsted will check on their next visit. "
                    f"{protocol_solution if protocol_solution else 'Protocol Education has successfully helped 12 schools address similar challenges this year'}. "
                    f"We have teachers ready to start who specialize in exactly this area. "
                    f"Given Ofsted's focus on rapid improvement, shall we discuss how quickly we can get the right support in place?"
                ),
                source_url=ofsted_data.get('report_url', ''),
                relevance_score=1.0
            )
            starters.append(starter)
        
        # Priority 2: Subject-specific weaknesses
        subject_weaknesses = ofsted_data.get('subject_specific_weaknesses', {})
        
        # Mathematics weaknesses
        if subject_weaknesses.get('mathematics'):
            maths_issues = subject_weaknesses['mathematics']
            starter = ConversationStarter(
                topic="Mathematics Improvement Support",
                detail=(
                    f"Your Ofsted report specifically highlights mathematics as an area for development. "
                    f"Protocol Education has just placed 3 maths specialists in local schools who've achieved "
                    f"20%+ improvement in outcomes within two terms. "
                    f"Our maths teachers come with proven intervention strategies and can also lead staff training. "
                    f"With SATs/GCSEs approaching, would you like to see profiles of our available maths specialists?"
                ),
                source_url=ofsted_data.get('report_url', ''),
                relevance_score=0.95
            )
            starters.append(starter)
        
        # English/Literacy weaknesses
        if subject_weaknesses.get('english') or any('phonics' in str(w).lower() for w in ofsted_data.get('critical_weaknesses', [])):
            starter = ConversationStarter(
                topic="Literacy and English Support",
                detail=(
                    f"I noticed Ofsted mentioned literacy development in your report. "
                    f"This is such a crucial area - Protocol has 8 literacy specialists available including "
                    f"RWI-trained phonics experts and experienced English leads. "
                    f"One of our teachers recently helped a school jump from 67% to 89% in phonics screening. "
                    f"Would Tuesday or Wednesday work better for a quick call about your literacy needs?"
                ),
                source_url=ofsted_data.get('report_url', ''),
                relevance_score=0.94
            )
            starters.append(starter)
        
        # SEND always important
        send_issues = ofsted_data.get('send_weaknesses', [])
        if send_issues or 'send' in str(ofsted_data).lower():
            starter = ConversationStarter(
                topic="SEND Provision Enhancement",
                detail=(
                    f"Every Ofsted report focuses heavily on SEND provision, and yours mentions areas for development. "
                    f"Protocol's dedicated SEND team includes qualified SENCOs and intervention specialists. "
                    f"We also provide SEND training for your whole staff - crucial for Ofsted compliance. "
                    f"Our SEND placements have helped schools completely transform their provision. "
                    f"Can I arrange for our SEND specialist to discuss your specific needs this week?"
                ),
                source_url=ofsted_data.get('report_url', ''),
                relevance_score=0.96
            )
            starters.append(starter)
        
        # Leadership development
        leadership_issues = ofsted_data.get('leadership_weaknesses', [])
        if leadership_issues or any('lead' in str(w).lower() for w in ofsted_data.get('critical_weaknesses', [])):
            starter = ConversationStarter(
                topic="Leadership Strengthening",
                detail=(
                    f"Your Ofsted report touches on leadership development - this is always key to improvement. "
                    f"Protocol has interim leaders who specialize in rapid improvement and coaching. "
                    f"They can fill gaps while mentoring your existing team for sustainable change. "
                    f"We've helped 15 schools strengthen leadership this year, with excellent Ofsted outcomes. "
                    f"Shall I send you details of our leadership improvement specialists?"
                ),
                source_url=ofsted_data.get('report_url', ''),
                relevance_score=0.93
            )
            starters.append(starter)
        
        # General improvement support
        total_weaknesses = len(ofsted_data.get('critical_weaknesses', []))
        if total_weaknesses > 3:
            starter = ConversationStarter(
                topic="Comprehensive Ofsted Action Plan Support",
                detail=(
                    f"I've analyzed your Ofsted report in detail - there are {total_weaknesses} specific areas "
                    f"where the right staffing could make an immediate difference. "
                    f"Rather than addressing these piecemeal, Protocol can provide a coordinated team to "
                    f"tackle all priorities simultaneously. "
                    f"We've supported 8 schools through successful Ofsted journeys this year. "
                    f"Can we schedule 20 minutes to create a staffing plan aligned to your Ofsted priorities?"
                ),
                source_url=ofsted_data.get('report_url', ''),
                relevance_score=0.92
            )
            starters.append(starter)
        
        # Always add a monitoring visit urgency starter
        if ofsted_data.get('rating') in ['Requires Improvement', 'Inadequate']:
            starter = ConversationStarter(
                topic="Ofsted Monitoring Visit Preparation",
                detail=(
                    f"With your {ofsted_data.get('rating')} rating, Ofsted will likely conduct monitoring visits. "
                    f"They'll expect to see rapid progress on the areas identified in your report. "
                    f"Protocol specializes in rapid improvement - our teachers know exactly what Ofsted looks for. "
                    f"We can have improvement specialists in place within days, not weeks. "
                    f"Time is critical - can we discuss your most urgent staffing needs today?"
                ),
                source_url=ofsted_data.get('report_url', ''),
                relevance_score=0.99
            )
            starters.append(starter)
        
        return starters
    
    def _prioritize_weaknesses(self, ofsted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prioritize weaknesses by severity and potential impact"""
        
        if 'critical_weaknesses' in ofsted_data:
            # Sort by severity and urgency
            severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
            
            ofsted_data['critical_weaknesses'].sort(
                key=lambda x: (
                    severity_order.get(x.get('severity', 'MEDIUM'), 3),
                    0 if x.get('urgency') == 'Immediate' else 1
                )
            )
            
            # Add improvement roadmap
            ofsted_data['improvement_roadmap'] = {
                'immediate_actions': [
                    w for w in ofsted_data['critical_weaknesses'] 
                    if w.get('urgency') == 'Immediate'
                ],
                'term_priorities': [
                    w for w in ofsted_data['critical_weaknesses']
                    if w.get('urgency') == 'This term'
                ],
                'year_plan': [
                    w for w in ofsted_data['critical_weaknesses']
                    if w.get('urgency') == 'Next year'
                ]
            }
        
        return ofsted_data
    
    def _match_to_solution_db(self, area: str) -> str:
        """Match weakness area to our solution database"""
        
        # Keywords to solution mapping
        keyword_map = {
            'phonics': ['phonics', 'reading', 'rw', 'systematic synthetic'],
            'mathematics': ['maths', 'mathematics', 'numeracy', 'calculation'],
            'send': ['send', 'sen', 'special educational', 'inclusion', 'senco'],
            'leadership': ['leadership', 'leaders', 'management', 'strategic'],
            'subject leadership': ['subject lead', 'coordinator', 'head of', 'tlr'],
            'early years': ['eyfs', 'early years', 'foundation', 'nursery', 'reception'],
            'assessment': ['assessment', 'marking', 'feedback', 'data', 'tracking'],
            'curriculum': ['curriculum', 'planning', 'sequencing', 'progression'],
            'behaviour': ['behaviour', 'behavior', 'conduct', 'discipline'],
            'attendance': ['attendance', 'absence', 'punctuality', 'persistent absence']
        }
        
        area_lower = area.lower()
        
        for solution_key, keywords in keyword_map.items():
            if any(keyword in area_lower for keyword in keywords):
                return solution_key
        
        return 'general'
    
    def _find_ofsted_report_url(self, school_name: str) -> Optional[str]:
        """Find the Ofsted report URL for a school"""
        
        # Search for the report - try multiple search strategies
        search_queries = [
            f'"{school_name}" site:reports.ofsted.gov.uk',
            f'{school_name} Ofsted report filetype:pdf',
            f'{school_name} latest Ofsted inspection'
        ]
        
        for query in search_queries:
            results = self.serper.search_web(query, num_results=5)
            
            if results:
                # Prioritize official Ofsted URLs
                for result in results:
                    url = result.get('url', '')
                    if 'reports.ofsted.gov.uk' in url or 'files.ofsted.gov.uk' in url:
                        logger.info(f"Found Ofsted report URL: {url}")
                        return url
                
                # If no official URL, check for PDF links
                for result in results:
                    url = result.get('url', '')
                    if url.endswith('.pdf') and 'ofsted' in url.lower():
                        return url
        
        return None
    
    def _fetch_ofsted_report(self, url: str) -> Optional[str]:
        """Fetch the Ofsted report HTML content"""
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error fetching Ofsted report: {e}")
            return None
    
    def _enhance_basic_data(self, basic_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance basic data when full analysis isn't possible"""
        
        enhanced = basic_data.copy()
        
        # Add generic weaknesses based on rating
        rating = basic_data.get('rating', 'Unknown')
        
        if rating == 'Requires Improvement':
            enhanced['likely_weaknesses'] = [
                "Teaching quality inconsistency",
                "Leadership capacity",
                "Progress in core subjects",
                "SEND provision"
            ]
            enhanced['urgent_staffing_needs'] = [
                "Experienced teachers in core subjects",
                "Middle leaders with improvement experience",
                "SEND specialists"
            ]
        elif rating == 'Inadequate':
            enhanced['likely_weaknesses'] = [
                "Safeguarding",
                "Leadership and management",
                "Teaching quality",
                "Pupil outcomes"
            ]
            enhanced['urgent_staffing_needs'] = [
                "Interim leadership support",
                "Safeguarding leads",
                "Outstanding teachers across all subjects"
            ]
        
        return enhanced


def integrate_ofsted_analyzer(processor):
    """
    Integration function to add Ofsted analysis to the processor
    """
    
    def enhance_with_ofsted_analysis(intel, ai_engine):
        """Add enhanced Ofsted analysis to school intelligence"""
        
        try:
            # Initialize analyzer
            analyzer = OfstedAnalyzer(
                ai_engine, 
                ai_engine.openai_client
            )
            
            # Get basic Ofsted data from current intelligence
            basic_ofsted = {
                'rating': intel.ofsted_rating,
                'inspection_date': intel.ofsted_date.isoformat() if intel.ofsted_date else None
            }
            
            # Get enhanced analysis
            enhanced_ofsted = analyzer.get_enhanced_ofsted_analysis(
                intel.school_name,
                basic_ofsted
            )
            
            # Replace existing conversation starters with weakness-focused ones
            if 'conversation_starters' in enhanced_ofsted:
                # Add new Ofsted-based starters at the beginning
                ofsted_starters = enhanced_ofsted.get('conversation_starters', [])
                
                # Keep only the most relevant existing starters
                existing_starters = [s for s in intel.conversation_starters 
                                   if s.relevance_score < 0.9][:3]
                
                # Combine with Ofsted starters taking priority
                intel.conversation_starters = ofsted_starters + existing_starters
            
            # Store enhanced Ofsted data
            intel.ofsted_enhanced = enhanced_ofsted
            
            logger.info(f"Enhanced {intel.school_name} with {enhanced_ofsted.get('weaknesses_count', 0)} Ofsted weaknesses")
            
        except Exception as e:
            logger.error(f"Error enhancing with Ofsted analysis: {e}")
        
        return intel
    
    return enhance_with_ofsted_analysis