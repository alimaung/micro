"""
Filming Order Service
Determines optimal filming order based on temp roll dependencies and physical existence
"""

import logging
from typing import Dict, List, Tuple, Any
from django.db.models import QuerySet
from ..models import Roll, TempRoll

logger = logging.getLogger(__name__)

class FilmingOrderService:
    """Service for determining optimal filming order based on temp roll dependencies."""
    
    @classmethod
    def analyze_rolls_for_filming(cls, rolls: QuerySet) -> Dict[str, Any]:
        """
        Analyze rolls and determine optimal filming order.
        
        Args:
            rolls: QuerySet of Roll objects to analyze
            
        Returns:
            Dict containing filming order analysis
        """
        roll_analysis = {}
        
        # Analyze each roll
        for roll in rolls:
            analysis = cls._analyze_single_roll(roll)
            roll_analysis[roll.id] = analysis
        
        # Calculate dependency depths
        cls._calculate_dependency_depths(roll_analysis)
        
        # Categorize and sort rolls
        filming_order = cls._determine_filming_order(roll_analysis)
        
        # Add summary statistics
        filming_order['summary'] = cls._generate_summary(filming_order)
        
        return filming_order
    
    @classmethod
    def _analyze_single_roll(cls, roll) -> Dict[str, Any]:
        """Analyze a single roll's filming readiness and dependencies."""
        analysis = {
            'roll': roll,
            'type': 'unknown',
            'issues': [],
            'can_film_now': False,
            'blocks_others': False,
            'dependency_depth': 0,
            'temp_roll_info': {}
        }
        
        # Add temp roll information
        if roll.source_temp_roll:
            analysis['temp_roll_info']['uses'] = {
                'temp_roll_id': roll.source_temp_roll.temp_roll_id,
                'capacity': roll.source_temp_roll.usable_capacity,
                'exists': roll.source_temp_roll.exists,
                'status': roll.source_temp_roll.status
            }
        
        if roll.created_temp_roll:
            analysis['temp_roll_info']['creates'] = {
                'temp_roll_id': roll.created_temp_roll.temp_roll_id,
                'capacity': roll.created_temp_roll.usable_capacity,
                'exists': roll.created_temp_roll.exists,
                'status': roll.created_temp_roll.status
            }
        
        # Determine roll type and filming readiness
        if not roll.source_temp_roll and not roll.created_temp_roll:
            analysis['type'] = 'independent'
            analysis['can_film_now'] = True
            
        elif roll.source_temp_roll and not roll.created_temp_roll:
            analysis['type'] = 'consumer'
            analysis['can_film_now'] = cls._can_use_temp_roll(roll, roll.source_temp_roll)
            if not analysis['can_film_now']:
                analysis['issues'] = cls._get_temp_roll_issues(roll, roll.source_temp_roll)
                
        elif not roll.source_temp_roll and roll.created_temp_roll:
            analysis['type'] = 'creator'
            analysis['can_film_now'] = True
            # Check if other rolls are waiting for this temp roll
            analysis['blocks_others'] = cls._check_blocks_others(roll)
            
        elif roll.source_temp_roll and roll.created_temp_roll:
            analysis['type'] = 'chain'
            analysis['can_film_now'] = cls._can_use_temp_roll(roll, roll.source_temp_roll)
            if not analysis['can_film_now']:
                analysis['issues'] = cls._get_temp_roll_issues(roll, roll.source_temp_roll)
            # Check if this creates temp rolls others need
            analysis['blocks_others'] = cls._check_blocks_others(roll)
        
        return analysis
    
    @classmethod
    def _can_use_temp_roll(cls, roll, temp_roll) -> bool:
        """Check if a roll can use its allocated temp roll."""
        if not temp_roll.exists:
            return False
        
        # Roll can use temp roll if:
        # 1. It's specifically allocated to this roll, OR
        # 2. It's still available for allocation
        return (temp_roll.used_by_roll == roll or 
                temp_roll.status == 'available')
    
    @classmethod
    def _get_temp_roll_issues(cls, roll, temp_roll) -> List[str]:
        """Get list of issues preventing roll from using temp roll."""
        issues = []
        
        if not temp_roll.exists:
            issues.append(f"Temp roll #{temp_roll.temp_roll_id} doesn't exist physically")
        elif temp_roll.used_by_roll and temp_roll.used_by_roll != roll:
            issues.append(f"Temp roll #{temp_roll.temp_roll_id} is allocated to different roll (Roll {temp_roll.used_by_roll.id})")
        elif temp_roll.status not in ['available', 'used']:
            issues.append(f"Temp roll #{temp_roll.temp_roll_id} has invalid status: {temp_roll.status}")
        
        return issues
    
    @classmethod
    def _check_blocks_others(cls, roll) -> bool:
        """Check if this roll creates temp rolls that other rolls are waiting for."""
        if not roll.created_temp_roll:
            return False
        
        waiting_rolls = Roll.objects.filter(
            source_temp_roll=roll.created_temp_roll,
            filming_status='ready'
        ).exclude(id=roll.id)
        
        return waiting_rolls.exists()
    
    @classmethod
    def _calculate_dependency_depths(cls, roll_analysis: Dict) -> None:
        """Calculate dependency depth for each roll."""
        # Create mapping of temp_roll_id to creator roll
        temp_roll_creators = {}
        for roll_id, analysis in roll_analysis.items():
            roll = analysis['roll']
            if roll.created_temp_roll:
                temp_roll_creators[roll.created_temp_roll.temp_roll_id] = roll_id
        
        def get_depth(roll_id, visited=None):
            if visited is None:
                visited = set()
            
            if roll_id in visited:
                return float('inf')  # Circular dependency
            
            visited.add(roll_id)
            analysis = roll_analysis[roll_id]
            roll = analysis['roll']
            
            if not roll.source_temp_roll:
                return 0  # No dependencies
            
            # Check if the needed temp roll exists
            if roll.source_temp_roll.exists:
                return 0  # Can use existing temp roll
            
            # Check if another roll creates this temp roll
            creator_roll_id = temp_roll_creators.get(roll.source_temp_roll.temp_roll_id)
            if creator_roll_id and creator_roll_id in roll_analysis:
                return get_depth(creator_roll_id, visited.copy()) + 1
            else:
                return float('inf')  # Orphaned dependency
        
        # Calculate depths
        for roll_id, analysis in roll_analysis.items():
            depth = get_depth(roll_id)
            analysis['dependency_depth'] = depth
    
    @classmethod
    def _determine_filming_order(cls, roll_analysis: Dict) -> Dict[str, List]:
        """Determine optimal filming order based on analysis."""
        immediate_rolls = []  # Can film right now
        creator_rolls = []    # Create temp rolls others need
        waiting_rolls = []    # Wait for dependencies
        problem_rolls = []    # Need manual intervention
        
        for roll_id, analysis in roll_analysis.items():
            roll = analysis['roll']
            
            if analysis['dependency_depth'] == float('inf'):
                problem_rolls.append((roll, analysis))
            elif analysis['can_film_now']:
                if analysis['blocks_others']:
                    creator_rolls.append((roll, analysis))
                else:
                    immediate_rolls.append((roll, analysis))
            else:
                waiting_rolls.append((roll, analysis))
        
        # Sort each category
        immediate_rolls.sort(key=lambda x: (
            x[1]['dependency_depth'], 
            x[0].project.archive_id, 
            x[0].roll_number or 0
        ))
        
        creator_rolls.sort(key=lambda x: (
            -cls._count_blocked_rolls(x[0]),  # Prioritize by number of rolls unblocked
            x[1]['dependency_depth'], 
            x[0].project.archive_id
        ))
        
        waiting_rolls.sort(key=lambda x: (
            x[1]['dependency_depth'], 
            x[0].project.archive_id, 
            x[0].roll_number or 0
        ))
        
        return {
            'immediate_rolls': immediate_rolls,
            'creator_rolls': creator_rolls,
            'waiting_rolls': waiting_rolls,
            'problem_rolls': problem_rolls
        }
    
    @classmethod
    def _count_blocked_rolls(cls, roll) -> int:
        """Count how many rolls are blocked waiting for this roll's temp roll."""
        if not roll.created_temp_roll:
            return 0
        
        return Roll.objects.filter(
            source_temp_roll=roll.created_temp_roll,
            filming_status='ready'
        ).exclude(id=roll.id).count()
    
    @classmethod
    def _generate_summary(cls, filming_order: Dict) -> Dict[str, Any]:
        """Generate summary statistics."""
        return {
            'total_ready': len(filming_order['immediate_rolls']) + len(filming_order['creator_rolls']),
            'immediate_count': len(filming_order['immediate_rolls']),
            'creator_count': len(filming_order['creator_rolls']),
            'waiting_count': len(filming_order['waiting_rolls']),
            'problem_count': len(filming_order['problem_rolls']),
            'recommended_next': cls._get_recommended_next(filming_order)
        }
    
    @classmethod
    def _get_recommended_next(cls, filming_order: Dict) -> Dict[str, Any]:
        """Get recommendation for next roll to film."""
        if filming_order['creator_rolls']:
            roll, analysis = filming_order['creator_rolls'][0]
            return {
                'roll_id': roll.id,
                'reason': 'Creates temp roll for others',
                'blocks_count': cls._count_blocked_rolls(roll)
            }
        elif filming_order['immediate_rolls']:
            roll, analysis = filming_order['immediate_rolls'][0]
            return {
                'roll_id': roll.id,
                'reason': 'Ready to film immediately',
                'blocks_count': 0
            }
        else:
            return None
    
    @classmethod
    def get_filming_priority(cls, roll) -> Dict[str, Any]:
        """Get filming priority information for a single roll."""
        analysis = cls._analyze_single_roll(roll)
        
        priority_info = {
            'can_film_now': analysis['can_film_now'],
            'priority_tier': 'unknown',
            'priority_score': 999,  # Lower is higher priority
            'temp_roll_info': analysis['temp_roll_info'],
            'issues': analysis['issues']
        }
        
        if analysis['can_film_now']:
            if analysis['blocks_others']:
                priority_info['priority_tier'] = 'creator'
                priority_info['priority_score'] = 1
            else:
                priority_info['priority_tier'] = 'immediate'
                priority_info['priority_score'] = 2
        elif analysis['dependency_depth'] != float('inf'):
            priority_info['priority_tier'] = 'waiting'
            priority_info['priority_score'] = 10 + analysis['dependency_depth']
        else:
            priority_info['priority_tier'] = 'problem'
            priority_info['priority_score'] = 999
        
        return priority_info 