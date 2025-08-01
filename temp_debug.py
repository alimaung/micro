#!/usr/bin/env python3
"""
Temp Roll Analysis and Filming Order Debug Script
Analyzes current temp roll situation and determines optimal filming order
"""

import os
import sys
import django
from datetime import datetime
from collections import defaultdict, deque

# Setup Django environment
sys.path.append('micro')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'micro.settings')
django.setup()

from microapp.models import TempRoll, Roll, Project

def analyze_temp_rolls():
    """Analyze all temp rolls and their current state."""
    print("=" * 80)
    print("TEMP ROLL INVENTORY ANALYSIS")
    print("=" * 80)
    
    temp_rolls = TempRoll.objects.all().order_by('temp_roll_id')
    
    existing_temp_rolls = []
    planned_temp_rolls = []
    
    for temp_roll in temp_rolls:
        print(f"Temp Roll #{temp_roll.temp_roll_id}:")
        print(f"  Film Type: {temp_roll.film_type}")
        print(f"  Capacity: {temp_roll.usable_capacity} pages")
        print(f"  Status: {temp_roll.status}")
        print(f"  Exists: {temp_roll.exists}")
        print(f"  Source Roll: {temp_roll.source_roll.id if temp_roll.source_roll else 'None'}")
        print(f"  Used By Roll: {temp_roll.used_by_roll.id if temp_roll.used_by_roll else 'None'}")
        print()
        
        if temp_roll.exists:
            existing_temp_rolls.append(temp_roll)
        else:
            planned_temp_rolls.append(temp_roll)
    
    print(f"SUMMARY: {len(existing_temp_rolls)} existing, {len(planned_temp_rolls)} planned")
    print()
    
    return existing_temp_rolls, planned_temp_rolls

def analyze_roll_dependencies():
    """Analyze all rolls and their temp roll dependencies."""
    print("=" * 80)
    print("ROLL DEPENDENCY ANALYSIS")
    print("=" * 80)
    
    rolls = Roll.objects.filter(filming_status='ready').select_related(
        'project', 'source_temp_roll', 'created_temp_roll'
    ).order_by('project__archive_id', 'roll_number')
    
    roll_analysis = {}
    
    for roll in rolls:
        analysis = {
            'roll': roll,
            'type': 'unknown',
            'issues': [],
            'can_film_now': False,
            'blocks_others': False,
            'dependency_depth': 0
        }
        
        # Determine roll type and issues
        if not roll.source_temp_roll and not roll.created_temp_roll:
            analysis['type'] = 'independent'
            analysis['can_film_now'] = True
            
        elif roll.source_temp_roll and not roll.created_temp_roll:
            analysis['type'] = 'consumer'
            # Check if source temp roll exists and is allocated to this roll
            if roll.source_temp_roll.exists:
                # If the temp roll is allocated to this roll (used_by_roll), it can use it
                if (roll.source_temp_roll.used_by_roll == roll or 
                    roll.source_temp_roll.status == 'available'):
                    analysis['can_film_now'] = True
                else:
                    analysis['can_film_now'] = False
                    analysis['issues'].append(f"Temp roll #{roll.source_temp_roll.temp_roll_id} is allocated to different roll (Roll {roll.source_temp_roll.used_by_roll.id if roll.source_temp_roll.used_by_roll else 'Unknown'})")
            else:
                analysis['can_film_now'] = False
                analysis['issues'].append(f"Temp roll #{roll.source_temp_roll.temp_roll_id} doesn't exist physically")
                    
        elif not roll.source_temp_roll and roll.created_temp_roll:
            analysis['type'] = 'creator'
            analysis['can_film_now'] = True
            # Check if other rolls are waiting for this temp roll
            waiting_rolls = Roll.objects.filter(
                source_temp_roll=roll.created_temp_roll,
                filming_status='ready'
            ).exclude(id=roll.id)
            if waiting_rolls.exists():
                analysis['blocks_others'] = True
                analysis['blocks_count'] = waiting_rolls.count()
        
        elif roll.source_temp_roll and roll.created_temp_roll:
            analysis['type'] = 'chain'
            # Check source temp roll exists and is allocated to this roll
            if roll.source_temp_roll.exists:
                # If the temp roll is allocated to this roll (used_by_roll), it can use it
                if (roll.source_temp_roll.used_by_roll == roll or 
                    roll.source_temp_roll.status == 'available'):
                    analysis['can_film_now'] = True
                else:
                    analysis['can_film_now'] = False
                    analysis['issues'].append(f"Temp roll #{roll.source_temp_roll.temp_roll_id} is allocated to different roll (Roll {roll.source_temp_roll.used_by_roll.id if roll.source_temp_roll.used_by_roll else 'Unknown'})")
            else:
                analysis['can_film_now'] = False
                analysis['issues'].append(f"Temp roll #{roll.source_temp_roll.temp_roll_id} doesn't exist physically")
            # Check if this creates temp rolls others need
            waiting_rolls = Roll.objects.filter(
                source_temp_roll=roll.created_temp_roll,
                filming_status='ready'
            ).exclude(id=roll.id)
            if waiting_rolls.exists():
                analysis['blocks_others'] = True
                analysis['blocks_count'] = waiting_rolls.count()
        
        roll_analysis[roll.id] = analysis
        
        # Print analysis
        print(f"Roll {roll.id} ({roll.project.archive_id} R{roll.roll_number}):")
        print(f"  Type: {analysis['type']}")
        print(f"  Can film now: {analysis['can_film_now']}")
        if analysis['blocks_others']:
            print(f"  Blocks {analysis.get('blocks_count', 0)} other rolls")
        if roll.source_temp_roll:
            print(f"  Uses: Temp Roll #{roll.source_temp_roll.temp_roll_id} (exists: {roll.source_temp_roll.exists})")
        if roll.created_temp_roll:
            print(f"  Creates: Temp Roll #{roll.created_temp_roll.temp_roll_id}")
        if analysis['issues']:
            print(f"  Issues: {'; '.join(analysis['issues'])}")
        print()
    
    return roll_analysis

def calculate_dependency_depth(roll_analysis):
    """Calculate dependency depth for each roll."""
    print("=" * 80)
    print("DEPENDENCY DEPTH CALCULATION")
    print("=" * 80)
    
    # Create a mapping of temp_roll_id to creator roll
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
        
        roll = analysis['roll']
        print(f"Roll {roll.id} ({roll.project.archive_id} R{roll.roll_number}): depth {depth}")
    
    print()
    return roll_analysis

def determine_filming_order(roll_analysis):
    """Determine optimal filming order based on analysis."""
    print("=" * 80)
    print("OPTIMAL FILMING ORDER")
    print("=" * 80)
    
    # Separate rolls by category
    immediate_rolls = []  # Can film right now
    creator_rolls = []    # Create temp rolls others need
    chain_rolls = []      # Part of dependency chains
    problem_rolls = []    # Have issues that need resolution
    
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
            chain_rolls.append((roll, analysis))
    
    # Sort each category
    immediate_rolls.sort(key=lambda x: (x[1]['dependency_depth'], x[0].project.archive_id, x[0].roll_number or 0))
    creator_rolls.sort(key=lambda x: (-x[1].get('blocks_count', 0), x[1]['dependency_depth'], x[0].project.archive_id))
    chain_rolls.sort(key=lambda x: (x[1]['dependency_depth'], x[0].project.archive_id, x[0].roll_number or 0))
    
    print("TIER 1: IMMEDIATE (Can film right now)")
    print("-" * 40)
    for i, (roll, analysis) in enumerate(immediate_rolls):
        temp_info = ""
        if roll.source_temp_roll:
            temp_info = f" [uses T#{roll.source_temp_roll.temp_roll_id}]"
        if roll.created_temp_roll:
            temp_info += f" [creates T#{roll.created_temp_roll.temp_roll_id}]"
        print(f"{i+1}. Roll {roll.id} - {roll.project.archive_id} R{roll.roll_number} ({analysis['type']}){temp_info}")
    
    print(f"\nTIER 2: CREATORS (Create temp rolls for others)")
    print("-" * 40)
    for i, (roll, analysis) in enumerate(creator_rolls):
        blocks_info = f" [blocks {analysis.get('blocks_count', 0)} rolls]" if analysis['blocks_others'] else ""
        temp_info = ""
        if roll.source_temp_roll:
            temp_info = f" [uses T#{roll.source_temp_roll.temp_roll_id}]"
        if roll.created_temp_roll:
            temp_info += f" [creates T#{roll.created_temp_roll.temp_roll_id}]"
        print(f"{i+1}. Roll {roll.id} - {roll.project.archive_id} R{roll.roll_number} ({analysis['type']}){temp_info}{blocks_info}")
    
    print(f"\nTIER 3: WAITING (Need dependencies created first)")
    print("-" * 40)
    for i, (roll, analysis) in enumerate(chain_rolls):
        depth_info = f" [depth {analysis['dependency_depth']}]"
        temp_info = ""
        if roll.source_temp_roll:
            temp_info = f" [needs T#{roll.source_temp_roll.temp_roll_id}]"
        if roll.created_temp_roll:
            temp_info += f" [creates T#{roll.created_temp_roll.temp_roll_id}]"
        print(f"{i+1}. Roll {roll.id} - {roll.project.archive_id} R{roll.roll_number} ({analysis['type']}){temp_info}{depth_info}")
        if analysis['issues']:
            for issue in analysis['issues']:
                print(f"     Issue: {issue}")
    
    if problem_rolls:
        print(f"\nPROBLEM ROLLS (Need manual intervention)")
        print("-" * 40)
        for i, (roll, analysis) in enumerate(problem_rolls):
            print(f"{i+1}. Roll {roll.id} - {roll.project.archive_id} R{roll.roll_number}")
            for issue in analysis['issues']:
                print(f"     Issue: {issue}")
    
    print()
    return immediate_rolls, creator_rolls, chain_rolls, problem_rolls

def suggest_alternatives(problem_rolls):
    """Suggest alternatives for problematic rolls."""
    if not problem_rolls:
        return
    
    print("=" * 80)
    print("ALTERNATIVE SOLUTIONS")
    print("=" * 80)
    
    available_temp_rolls = TempRoll.objects.filter(
        exists=True, 
        status='available'  # Only truly available ones (not allocated to other rolls)
    ).order_by('film_type', '-usable_capacity')
    
    for roll, analysis in problem_rolls:
        print(f"Roll {roll.id} - {roll.project.archive_id} R{roll.roll_number}:")
        print(f"  Originally planned to use: Temp Roll #{roll.source_temp_roll.temp_roll_id if roll.source_temp_roll else 'None'}")
        print(f"  Pages needed: {roll.pages_used} (estimated)")
        
        print("  Alternatives:")
        # Find suitable alternatives
        suitable_alternatives = []
        for temp_roll in available_temp_rolls:
            if (temp_roll.film_type == roll.film_type and 
                temp_roll.usable_capacity >= roll.pages_used):
                suitable_alternatives.append(temp_roll)
        
        # Also check existing temp rolls that might not be in use yet
        existing_unused = TempRoll.objects.filter(
            exists=True,
            film_type=roll.film_type,
            used_by_roll__isnull=True,  # Not allocated to any roll yet
            usable_capacity__gte=roll.pages_used
        ).exclude(status='used')  # Exclude ones allocated by registration
        
        all_alternatives = list(suitable_alternatives) + list(existing_unused)
        # Remove duplicates
        seen = set()
        unique_alternatives = []
        for temp_roll in all_alternatives:
            if temp_roll.temp_roll_id not in seen:
                seen.add(temp_roll.temp_roll_id)
                unique_alternatives.append(temp_roll)
        
        if unique_alternatives:
            for temp_roll in unique_alternatives[:3]:  # Show top 3
                efficiency = (roll.pages_used / temp_roll.usable_capacity) * 100
                print(f"    - Temp Roll #{temp_roll.temp_roll_id}: {temp_roll.usable_capacity} pages ({efficiency:.1f}% utilization)")
        else:
            print("    - No suitable temp rolls available")
            
        print(f"    - Use new {roll.film_type} roll")
        print()

def main():
    """Main analysis function."""
    print(f"TEMP ROLL ANALYSIS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Step 1: Analyze temp roll inventory
    existing_temp_rolls, planned_temp_rolls = analyze_temp_rolls()
    
    # Step 2: Analyze roll dependencies
    roll_analysis = analyze_roll_dependencies()
    
    # Step 3: Calculate dependency depths
    roll_analysis = calculate_dependency_depth(roll_analysis)
    
    # Step 4: Determine filming order
    immediate_rolls, creator_rolls, chain_rolls, problem_rolls = determine_filming_order(roll_analysis)
    
    # Step 5: Suggest alternatives for problems
    suggest_alternatives(problem_rolls)
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total temp rolls: {len(existing_temp_rolls)} existing, {len(planned_temp_rolls)} planned")
    print(f"Ready to film immediately: {len(immediate_rolls)} rolls")
    print(f"Should film next (creators): {len(creator_rolls)} rolls")
    print(f"Waiting in chains: {len(chain_rolls)} rolls")
    print(f"Need intervention: {len(problem_rolls)} rolls")
    print()
    
    if immediate_rolls or creator_rolls:
        print("RECOMMENDED NEXT ACTION:")
        if creator_rolls:
            next_roll = creator_rolls[0][0]
            print(f"Film Roll {next_roll.id} ({next_roll.project.archive_id} R{next_roll.roll_number}) - creates temp roll for others")
        elif immediate_rolls:
            next_roll = immediate_rolls[0][0]
            print(f"Film Roll {next_roll.id} ({next_roll.project.archive_id} R{next_roll.roll_number}) - independent")
    else:
        print("No rolls ready to film - check problem rolls above")

if __name__ == "__main__":
    main()
