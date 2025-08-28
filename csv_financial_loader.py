"""
Protocol Education CI System - Safe CSV Financial Data Loader
Uses only built-in Python libraries - no external fuzzy matching dependencies
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Any, List, Tuple
from pathlib import Path
import logging
from difflib import get_close_matches, SequenceMatcher
from functools import lru_cache
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class CSVFinancialLoader:
    """Safe CSV-based financial data loader with built-in Python fuzzy matching"""
    
    def __init__(self, csv_path: str = "school_financial_data.csv"):
        self.csv_path = Path(csv_path)
        self.df = None
        self.school_names = []
        self.urn_index = {}
        self.name_index = {}
        self.normalized_names = {}
        self._load_data()
    
    def _load_data(self):
        """Load CSV data and build optimized search indexes"""
        try:
            logger.info(f"Loading financial data from {self.csv_path}")
            
            # Load CSV with optimized dtypes
            self.df = pd.read_csv(self.csv_path, dtype={
                'URN': str,
                'No pupils': 'float64',
                'Supply Staff: E02 + E10 + E26': 'float64',
                'Education support staff: E03': 'float64',
                'Supply Spend': 'float64'
            })
            
            # Clean the dataframe
            self.df = self.df.dropna(subset=[self.df.columns[0]])
            
            # Build optimized indexes
            self._build_indexes()
            
            logger.info(f"Loaded {len(self.df)} schools from CSV with indexes built")
            
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            self.df = pd.DataFrame()
    
    def _build_indexes(self):
        """Build optimized search indexes for fast lookup"""
        if self.df.empty:
            return
            
        # Get all school names (first column)
        self.school_names = self.df.iloc[:, 0].astype(str).str.strip().tolist()
        
        # Build URN index for O(1) lookup
        if 'URN' in self.df.columns:
            for idx, row in self.df.iterrows():
                urn = str(row.get('URN', ''))
                if urn and urn != 'nan' and urn != '':
                    self.urn_index[urn] = idx
        
        # Build name index with variations for O(1) lookup
        for idx, name in enumerate(self.school_names):
            if pd.isna(name) or name == 'nan':
                continue
                
            # Store original name
            name_clean = name.strip()
            self.name_index[name_clean.lower()] = idx
            
            # Store normalized version
            normalized = self._normalize_school_name(name_clean)
            self.normalized_names[normalized] = idx
            
            # Store common variations
            variations = self._generate_name_variations(name_clean)
            for variant in variations:
                variant_lower = variant.lower()
                if variant_lower not in self.name_index:
                    self.name_index[variant_lower] = idx
                    
                variant_normalized = self._normalize_school_name(variant)
                if variant_normalized not in self.normalized_names:
                    self.normalized_names[variant_normalized] = idx
    
    def _normalize_school_name(self, name: str) -> str:
        """Enhanced normalization for better matching"""
        if pd.isna(name) or not name:
            return ""
        
        name = str(name).lower().strip()
        
        # Remove common school type suffixes
        name = re.sub(r'\b(school|academy|college|centre|center)\b', '', name)
        name = re.sub(r'\b(primary|secondary|infant|junior|nursery)\b', '', name)
        
        # Normalize common abbreviations
        name = re.sub(r'\bst\.?\s+', 'saint ', name)
        name = re.sub(r'\b&\b', 'and', name)
        name = re.sub(r'\brc\b', 'roman catholic', name)
        name = re.sub(r'\bce\b', 'church england', name)
        
        # Remove punctuation but preserve word boundaries
        name = re.sub(r'[^\w\s]', ' ', name)
        
        # Normalize whitespace
        name = ' '.join(name.split())
        
        return name
    
    def _generate_name_variations(self, name: str) -> List[str]:
        """Generate comprehensive variations of school names"""
        if pd.isna(name) or not name:
            return []
            
        variations = set()
        name_str = str(name).strip()
        
        # St./Saint variations
        if 'St.' in name_str or 'St ' in name_str:
            variations.add(name_str.replace('St.', 'Saint'))
            variations.add(name_str.replace('St ', 'Saint '))
        elif 'Saint' in name_str:
            variations.add(name_str.replace('Saint', 'St.'))
            variations.add(name_str.replace('Saint', 'St'))
        
        # & vs and variations
        if ' & ' in name_str:
            variations.add(name_str.replace(' & ', ' and '))
        elif ' and ' in name_str:
            variations.add(name_str.replace(' and ', ' & '))
        
        # Possessive variations
        if "'s " in name_str:
            variations.add(name_str.replace("'s ", " "))
            variations.add(name_str.replace("'s ", "s "))
        
        # Remove/add "The"
        if name_str.startswith('The '):
            variations.add(name_str[4:])
        else:
            variations.add(f'The {name_str}')
        
        # Common abbreviations
        variations.add(name_str.replace('Roman Catholic', 'RC'))
        variations.add(name_str.replace('RC', 'Roman Catholic'))
        variations.add(name_str.replace('Church of England', 'CE'))
        variations.add(name_str.replace('CE', 'Church of England'))
        
        return list(variations)
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using built-in Python
        Uses SequenceMatcher from difflib (no external dependencies)
        """
        if not str1 or not str2:
            return 0.0
            
        # Normalize both strings
        norm1 = self._normalize_school_name(str1)
        norm2 = self._normalize_school_name(str2)
        
        if not norm1 or not norm2:
            return 0.0
        
        # Use SequenceMatcher for similarity ratio
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Boost score for exact word matches
        words1 = set(norm1.split())
        words2 = set(norm2.split())
        if words1 and words2:
            word_overlap = len(words1 & words2) / len(words1 | words2)
            # Combine sequence similarity with word overlap
            similarity = (similarity * 0.7) + (word_overlap * 0.3)
        
        return similarity
    
    def _find_best_fuzzy_match(self, query: str, threshold: float = 0.75) -> Optional[Tuple[str, int, float]]:
        """
        Find best fuzzy match using built-in Python difflib
        Returns: (matched_name, index, confidence) or None
        """
        if not self.school_names:
            return None
        
        best_match = None
        best_score = 0.0
        best_idx = None
        
        # First try difflib's get_close_matches (fast and good)
        close_matches = get_close_matches(
            query, 
            self.school_names, 
            n=3,  # Get top 3 matches
            cutoff=threshold
        )
        
        if close_matches:
            # Calculate detailed similarity for the close matches
            for match in close_matches:
                idx = self.school_names.index(match)
                score = self._calculate_similarity(query, match)
                
                if score > best_score:
                    best_score = score
                    best_match = match
                    best_idx = idx
        
        if best_match and best_score >= threshold:
            return (best_match, best_idx, best_score)
        
        return None
    
    @lru_cache(maxsize=2000)
    def find_school(self, school_name: str, urn: Optional[str] = None) -> Optional[pd.Series]:
        """
        Find school with multi-stage matching strategy using safe Python libraries
        """
        if self.df.empty:
            logger.warning("CSV data not loaded")
            return None
        
        # Stage 1: Exact URN match (highest priority)
        if urn and urn in self.urn_index:
            idx = self.urn_index[urn]
            logger.info(f"✅ Found school by URN {urn}: {self.school_names[idx]}")
            return self.df.iloc[idx]
        
        # Stage 2: Exact name match
        name_lower = school_name.lower().strip()
        if name_lower in self.name_index:
            idx = self.name_index[name_lower]
            logger.info(f"✅ Found school by exact name: {self.school_names[idx]}")
            return self.df.iloc[idx]
        
        # Stage 3: Normalized name match
        normalized = self._normalize_school_name(school_name)
        if normalized and normalized in self.normalized_names:
            idx = self.normalized_names[normalized]
            logger.info(f"✅ Found school by normalized name: {self.school_names[idx]}")
            return self.df.iloc[idx]
        
        # Stage 4: Fuzzy matching with built-in Python
        try:
            fuzzy_result = self._find_best_fuzzy_match(school_name, threshold=0.75)
            
            if fuzzy_result:
                matched_name, idx, confidence = fuzzy_result
                confidence_pct = int(confidence * 100)
                
                logger.info(f"🔍 Fuzzy match for '{school_name}': '{matched_name}' (confidence: {confidence_pct}%)")
                
                if confidence >= 0.80:  # High confidence
                    return self.df.iloc[idx]
                elif confidence >= 0.75:  # Medium confidence
                    logger.warning(f"⚠️  Medium confidence match ({confidence_pct}%) - please verify")
                    return self.df.iloc[idx]
        
        except Exception as e:
            logger.error(f"Fuzzy matching error: {e}")
        
        # Stage 5: Word overlap fallback
        school_words = set(self._normalize_school_name(school_name).split())
        if not school_words:
            logger.warning(f"❌ No match found for school: {school_name}")
            return None
        
        best_score = 0
        best_idx = None
        
        for idx, name in enumerate(self.school_names):
            if pd.isna(name):
                continue
                
            name_words = set(self._normalize_school_name(name).split())
            if not name_words:
                continue
                
            # Calculate word overlap score
            intersection = len(school_words & name_words)
            union = len(school_words | name_words)
            score = intersection / union if union > 0 else 0
            
            if score > best_score and score > 0.6:
                best_score = score
                best_idx = idx
        
        if best_idx is not None:
            logger.info(f"🔍 Word overlap match for '{school_name}': '{self.school_names[best_idx]}' (score: {best_score:.2f})")
            return self.df.iloc[best_idx]
        
        logger.warning(f"❌ No match found for school: {school_name}")
        return None
    
    def get_financial_data(self, school_name: str, urn: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get financial data in the same format as the web scraper
        """
        # Find school in CSV
        school_data = self.find_school(school_name, urn)
        
        if school_data is None:
            return None
        
        # Extract basic info
        found_urn = str(school_data.get('URN', ''))
        official_name = str(school_data.iloc[0])
        no_pupils = school_data.get('No pupils', 0)
        
        # Initialize financial data structure
        financial_data = {
            'urn': found_urn,
            'entity_name': official_name,
            'entity_type': 'School',
            'source_url': f'CSV:{self.csv_path.name}',
            'extracted_date': datetime.now().isoformat(),
            'data_source': 'csv',
            'extraction_confidence': 0.95
        }
        
        # Extract supply staff costs (E02 + E10 + E26)
        try:
            supply_costs = 0
            
            if 'Supply Staff: E02 + E10 + E26' in school_data and pd.notna(school_data['Supply Staff: E02 + E10 + E26']):
                supply_costs = float(school_data['Supply Staff: E02 + E10 + E26'])
            elif 'Supply Spend' in school_data and pd.notna(school_data['Supply Spend']):
                supply_costs = float(school_data['Supply Spend'])
            
            financial_data['supply_staff_costs'] = int(supply_costs) if supply_costs > 0 else 0
            
        except (ValueError, TypeError) as e:
            logger.debug(f"Error parsing supply costs: {e}")
            financial_data['supply_staff_costs'] = 0
        
        # Extract education support staff costs
        try:
            if 'Education support staff: E03' in school_data and pd.notna(school_data['Education support staff: E03']):
                support_staff = float(school_data['Education support staff: E03'])
                financial_data['education_support_staff'] = int(support_staff) if support_staff > 0 else 0
        except (ValueError, TypeError):
            financial_data['education_support_staff'] = 0
        
        # Calculate teaching staff per pupil
        try:
            teaching_columns = [col for col in school_data.index if 'teaching' in col.lower() and 'staff' in col.lower()]
            
            if teaching_columns and no_pupils and pd.notna(no_pupils) and no_pupils > 0:
                teaching_total = float(school_data[teaching_columns[0]])
                if teaching_total > 0:
                    financial_data['teaching_staff_per_pupil'] = int(teaching_total / no_pupils)
        except (ValueError, TypeError, IndexError):
            pass
        
        # Calculate indirect employee expenses
        indirect_total = 0
        indirect_columns = []
        for col in school_data.index:
            col_lower = str(col).lower()
            if any(term in col_lower for term in ['indirect', 'admin', 'management', 'premises']):
                indirect_columns.append(col)
        
        try:
            for col in indirect_columns:
                if pd.notna(school_data[col]):
                    value = float(school_data[col])
                    if value > 0:
                        indirect_total += value
        except (ValueError, TypeError):
            pass
        
        if indirect_total > 0:
            financial_data['indirect_employee_expenses'] = int(indirect_total)
        elif financial_data['supply_staff_costs'] > 0:
            financial_data['indirect_employee_expenses'] = int(financial_data['supply_staff_costs'] * 3.5)
        
        # Generate recruitment estimates
        if financial_data.get('indirect_employee_expenses', 0) > 0:
            base_amount = financial_data['indirect_employee_expenses']
            financial_data['recruitment_estimates'] = {
                'low': int(base_amount * 0.2),
                'high': int(base_amount * 0.3),
                'midpoint': int(base_amount * 0.25),
                'note': 'Based on CSV financial data - indirect employee expenses'
            }
        elif financial_data.get('supply_staff_costs', 0) > 0:
            base_amount = financial_data['supply_staff_costs']
            financial_data['recruitment_estimates'] = {
                'low': int(base_amount * 0.8),
                'high': int(base_amount * 1.2),
                'midpoint': int(base_amount),
                'note': 'Estimated from supply staff costs (CSV data)'
            }
        
        # Add metadata
        financial_data['csv_match_type'] = 'urn' if urn and urn == found_urn else 'name_fuzzy'
        
        # Include additional useful fields
        additional_mappings = {
            'LA Name': 'local_authority',
            'Type': 'school_type',
            'Overall Phase': 'phase',
            'No pupils': 'number_of_pupils'
        }
        
        for csv_field, output_field in additional_mappings.items():
            if csv_field in school_data and pd.notna(school_data[csv_field]):
                financial_data[output_field] = school_data[csv_field]
        
        return financial_data
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about loaded data"""
        if self.df.empty:
            return {'loaded': False, 'error': 'No data loaded'}
        
        supply_col = 'Supply Staff: E02 + E10 + E26'
        if supply_col in self.df.columns:
            supply_data = self.df[supply_col].dropna()
            supply_stats = {
                'schools_with_supply_costs': len(supply_data[supply_data > 0]),
                'total_supply_spend': float(supply_data.sum()),
                'avg_supply_spend': float(supply_data.mean()) if len(supply_data) > 0 else 0,
                'median_supply_spend': float(supply_data.median()) if len(supply_data) > 0 else 0
            }
        else:
            supply_stats = {'schools_with_supply_costs': 0, 'total_supply_spend': 0}
        
        return {
            'loaded': True,
            'total_schools': len(self.df),
            'unique_las': len(self.df['LA Name'].unique()) if 'LA Name' in self.df else 0,
            'school_types': self.df['Type'].value_counts().to_dict() if 'Type' in self.df else {},
            'csv_file': str(self.csv_path),
            'csv_modified': datetime.fromtimestamp(self.csv_path.stat().st_mtime).isoformat() if self.csv_path.exists() else None,
            'index_size': {
                'name_index': len(self.name_index),
                'urn_index': len(self.urn_index),
                'normalized_names': len(self.normalized_names)
            },
            'fuzzy_matching': 'Built-in Python (difflib)',
            **supply_stats
        }
    
    def bulk_lookup(self, school_list: List[str]) -> Dict[str, Dict[str, Any]]:
        """Optimized bulk lookup for multiple schools"""
        results = {}
        
        logger.info(f"Performing bulk lookup for {len(school_list)} schools")
        
        for school_name in school_list:
            try:
                financial_data = self.get_financial_data(school_name)
                results[school_name] = financial_data
            except Exception as e:
                logger.error(f"Error in bulk lookup for {school_name}: {e}")
                results[school_name] = None
        
        found_count = sum(1 for v in results.values() if v is not None)
        logger.info(f"Bulk lookup complete: {found_count}/{len(school_list)} schools found")
        
        return results


# Example usage and testing
if __name__ == "__main__":
    # Test the safe loader
    loader = CSVFinancialLoader("school_financial_data.csv")
    
    # Test various school name variations
    test_schools = [
        ("St Mary's Primary School", None),
        ("Saint Mary's Primary", None),
        ("St. Mary's", None),
        ("Harris Academy Peckham", None),
        ("Hargrave Park School", None),
        ("The London Oratory School", None),
        ("Nonexistent School XYZ", None),
    ]
    
    print(f"\n{'='*80}")
    print("TESTING SAFE FUZZY MATCHING (No External Dependencies)")
    print(f"{'='*80}")
    
    for school_name, urn in test_schools:
        print(f"\nSearching for: '{school_name}'" + (f" (URN: {urn})" if urn else ""))
        
        result = loader.get_financial_data(school_name, urn)
        
        if result:
            print(f"  ✅ Found: {result['entity_name']}")
            print(f"     URN: {result['urn']}")
            print(f"     Supply costs: £{result.get('supply_staff_costs', 0):,}")
            if result.get('recruitment_estimates'):
                print(f"     Recruitment estimate: £{result['recruitment_estimates'].get('midpoint', 0):,}")
            print(f"     Match type: {result.get('csv_match_type', 'unknown')}")
        else:
            print("  ❌ Not found in CSV")
    
    # Print stats
    print(f"\n{'='*80}")
    print("SAFE CSV STATISTICS")
    print(f"{'='*80}")
    
    stats = loader.get_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"  {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")