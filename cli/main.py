#!/usr/bin/env python3
"""
Default Judgment Interview System
For Legal Aid Intake Coordinators

This script implements a structured interview system for tenant intake
when assessing the viability of a motion to set aside default judgment
in eviction cases.
"""

import yaml
import os
import re
import sys
import datetime
from pathlib import Path


def load_yaml(path):
    """Load YAML file from the given path."""
    try:
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            # Validate basic structure
            if not isinstance(data, dict) or 'questions' not in data:
                raise ValueError("Invalid YAML structure: missing questions section")
            return data
    except Exception as e:
        print(f"❌ Failed to load YAML: {e}")
        sys.exit(1)


def ask_question(q):
    """Ask a question and return the user's response."""
    print(f"\n❓ {q['prompt']}")
    
    if q['type'] == 'boolean':
        while True:
            ans = input("Enter [y/n]: ").strip().lower()
            if ans in ['y', 'yes']:
                return True
            elif ans in ['n', 'no']:
                return False
            else:
                print("Please enter y or n.")
    
    elif q['type'] == 'choice':
        for i, opt in enumerate(q['options']):
            print(f"{i+1}. {opt}")
        while True:
            sel = input("Enter choice number: ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(q['options']):
                return q['options'][int(sel)-1]
            else:
                print("Invalid choice.")
    
    elif q['type'] == 'text':
        return input("Your answer: ").strip()
    
    elif q['type'] == 'date':
        while True:
            date_str = input("Enter date (YYYY-MM-DD): ").strip()
            try:
                # Validate date format
                datetime.datetime.strptime(date_str, '%Y-%m-%d')
                return date_str
            except ValueError:
                print("Invalid date format. Please use YYYY-MM-DD.")
    
    elif q['type'] == 'multiple_choice':
        selected = []
        for i, opt in enumerate(q['options']):
            print(f"{i+1}. {opt}")
        print("Enter numbers separated by commas, or 'done' when finished")
        while True:
            sel = input("Selection: ").strip()
            if sel.lower() == 'done':
                break
            try:
                choices = [int(x.strip()) for x in sel.split(',')]
                for choice in choices:
                    if 1 <= choice <= len(q['options']) and q['options'][choice-1] not in selected:
                        selected.append(q['options'][choice-1])
                print(f"Current selections: {', '.join(selected)}")
            except ValueError:
                print("Invalid input. Enter numbers separated by commas.")
        return selected
    
    elif q['type'] == 'number':
        while True:
            try:
                return float(input("Enter a number: ").strip())
            except ValueError:
                print("Please enter a valid number.")
    
    elif q['type'] == 'summary':
        print("📋 Interview complete. Thank you!")
        return None
    
    else:
        print(f"⚠️ Unsupported question type: {q['type']}")
        return None


def run_interview(yaml_data):
    """Run an interview based on the provided YAML structure."""
    # Create dictionary for easy question lookup
    qdict = {q['id']: q for q in yaml_data['questions']}
    
    # Start with the first question
    current_id = yaml_data['questions'][0]['id']
    
    # Storage for answers and flags
    answers = {}
    flags = []
    
    # Main interview loop
    while current_id:
        q = qdict[current_id]
        ans = ask_question(q)
        answers[current_id] = ans
        
        # Capture static flags
        if 'flags' in q:
            flags.extend(q['flags'])
        
        # Keyword-based flag detection using regex
        if 'flags_from_text' in q and isinstance(ans, str):
            # Get the keywords section
            keywords = q['flags_from_text'].get('keywords', [])
            if isinstance(keywords, list):
                # If it's a list, convert to dict format
                keywords_dict = {}
                for item in keywords:
                    if isinstance(item, dict) and len(item) == 1:
                        key = next(iter(item))
                        value = item[key]
                        keywords_dict[key] = value
                keywords = keywords_dict
            
            # Now process the keywords
            for label, pattern in keywords.items():
                if re.search(rf"\b{pattern}\b", ans, re.IGNORECASE):
                    flags.append(label)
        
        # Calculate time-based flags if dates are involved
        if q['type'] == 'date' and 'date_flags' in q and ans:
            try:
                date_obj = datetime.datetime.strptime(ans, '%Y-%m-%d').date()
                today = datetime.date.today()
                days_diff = (today - date_obj).days
                
                for flag, threshold in q['date_flags'].items():
                    if days_diff >= threshold:
                        flags.append(flag)
            except ValueError:
                # Skip if date is invalid
                pass
        
        # Determine next step
        if 'follow_up' in q:
            if isinstance(ans, bool):
                branch = 'if_true' if ans else 'if_false'
                next_info = q['follow_up'].get(branch, {})
                flags.extend(next_info.get('flags', []))
                current_id = next_info.get('next')
            elif isinstance(ans, str) and 'options' in q['follow_up']:
                # Handle option-specific follow-ups
                next_info = q['follow_up']['options'].get(ans, {})
                flags.extend(next_info.get('flags', []))
                current_id = next_info.get('next', q.get('next'))
            else:
                current_id = q.get('next')
        else:
            current_id = q.get('next')
    
    # Interview complete — print summary
    print("\n" + "="*50)
    print("📊 INTERVIEW SUMMARY")
    print("="*50)
    
    print("\n🧾 Collected Answers:")
    for k, v in answers.items():
        # Format multi-select answers nicely
        if isinstance(v, list):
            print(f" - {k}:")
            for item in v:
                print(f"   * {item}")
        else:
            print(f" - {k}: {v}")
    
    print("\n🚩 Flags Triggered:")
    for f in sorted(set(flags)):
        print(f" - {f}")
    
    # Generate recommendation based on flags
    print("\n📝 Initial Assessment:")
    if 'improper_service' in flags:
        print(" ✅ Potential grounds for motion based on improper service (CCP § 473.5)")
    if 'mistake_neglect' in flags:
        print(" ✅ Potential grounds based on mistake/excusable neglect (CCP § 473(b))")
    if 'fraud_misconduct' in flags:
        print(" ✅ Potential grounds based on fraud/misconduct (CCP § 473(d))")
    if 'void_judgment' in flags:
        print(" ✅ Potential void judgment argument available")
    if 'time_barred' in flags:
        print(" ⚠️ Motion may be time-barred - careful review needed")
    if 'urgent_lockout' in flags:
        print(" ⚠️ URGENT: Lockout imminent - consider ex parte application")
    
    if not any(x in flags for x in ['improper_service', 'mistake_neglect', 'fraud_misconduct', 'void_judgment']):
        print(" ⚠️ No clear grounds for relief identified - further review needed")
    
    return answers, flags


def save_results(answers, flags, save_path=None):
    """Save interview results to a text file."""
    if not save_path:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"interview_results_{timestamp}.txt"
    
    try:
        with open(save_path, 'w') as f:
            f.write("DEFAULT JUDGMENT INTERVIEW RESULTS\n")
            f.write("="*40 + "\n\n")
            
            f.write("ANSWERS:\n")
            for k, v in answers.items():
                if isinstance(v, list):
                    f.write(f"{k}:\n")
                    for item in v:
                        f.write(f"  - {item}\n")
                else:
                    f.write(f"{k}: {v}\n")
            
            f.write("\nFLAGS TRIGGERED:\n")
            for flag in sorted(set(flags)):
                f.write(f"- {flag}\n")
        
        print(f"\n💾 Results saved to: {save_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to save results: {e}")
        return False


from backend.rules.rule_engine import evaluate_statutes
from backend.generator.doc_filler import generate_motion

def main():
    yaml_path = os.path.join(os.path.dirname(__file__), 'prompts', 'vacate_default.yaml')
    if not os.path.exists(yaml_path):
        print(f"❌ Error: YAML file not found at {yaml_path}")
        sys.exit(1)

    yaml_data = load_yaml(yaml_path)

    # Run the interview
    answers, flags = run_interview(yaml_data)

    # Evaluate legal basis
    result = evaluate_statutes(flags)

    # Generate the motion document
    generate_motion(answers, result)

    # Ask if the user wants to save plain-text results
    save = input("\nSave results to file? [y/n]: ").strip().lower()
    if save in ['y', 'yes']:
        save_results(answers, flags)

    print("\n👋 Thank you for using the Default Judgment Interview System.")


if __name__ == "__main__":
    main()

