import os
import sys
import yaml
from unittest.mock import patch, MagicMock
from io import StringIO
from cli.main import load_yaml, ask_question, run_interview

def test_load_yaml_valid_file():
    # Create a temporary YAML file for testing
    test_yaml = {
        'questions': [
            {
                'id': 'test_question',
                'type': 'boolean',
                'prompt': 'Test question?'
            }
        ]
    }
    
    # Write to temporary file
    temp_path = 'test_questions.yaml'
    with open(temp_path, 'w') as f:
        yaml.dump(test_yaml, f)
    
    # Test loading
    loaded = load_yaml(temp_path)
    assert loaded is not None
    assert 'questions' in loaded
    assert len(loaded['questions']) == 1
    
    # Cleanup
    os.remove(temp_path)

def test_ask_question_boolean():
    with patch('builtins.input', side_effect=['y', 'n']):
        # Test 'y' response
        q = {'type': 'boolean', 'prompt': 'Test boolean question?'}
        assert ask_question(q) is True
        
        # Test 'n' response
        assert ask_question(q) is False

def test_ask_question_choice():
    with patch('builtins.input', side_effect=['2']):
        q = {
            'type': 'choice',
            'prompt': 'Pick one',
            'options': ['Option 1', 'Option 2']
        }
        assert ask_question(q) == 'Option 2'

def test_ask_question_multiple_choice():
    with patch('builtins.input', side_effect=['1,2', 'done']):
        q = {
            'type': 'multiple_choice',
            'prompt': 'Pick multiple',
            'options': ['Option 1', 'Option 2', 'Option 3']
        }
        result = ask_question(q)
        assert isinstance(result, list)
        assert len(result) == 2
        assert 'Option 1' in result
        assert 'Option 2' in result

def test_ask_question_date():
    with patch('builtins.input', side_effect=['2024-12-01']):
        q = {
            'type': 'date',
            'prompt': 'Enter date'
        }
        result = ask_question(q)
        assert result == '2024-12-01'

def test_run_interview_basic_flow():
    # Create mock YAML data
    yaml_data = {
        'questions': [
            {
                'id': 'start',
                'type': 'boolean',
                'prompt': 'Start?',
                'next': 'end'
            },
            {
                'id': 'end',
                'type': 'summary',
                'prompt': 'End'
            }
        ]
    }
    
    # Mock input
    with patch('builtins.input', side_effect=['y']):
        # Capture print output
        with patch('sys.stdout', new=StringIO()) as fake_out:
            answers, flags = run_interview(yaml_data)
            
            # Check output contains expected messages
            output = fake_out.getvalue()
            assert "❓ Start?" in output
            assert "📋 Interview complete" in output
            
            # Check results
            assert answers is not None
            assert 'start' in answers
            assert answers['start'] is True
            assert flags == []

def test_run_interview_with_flags():
    # Create mock YAML with flag conditions
    yaml_data = {
        'questions': [
            {
                'id': 'notice',
                'type': 'boolean',
                'prompt': 'Did you receive notice?',
                'next': 'end',
                'flags': ['notice_received']
            },
            {
                'id': 'end',
                'type': 'summary',
                'prompt': 'End'
            }
        ]
    }
    
    # Mock input
    with patch('builtins.input', side_effect=['y']):
        answers, flags = run_interview(yaml_data)
        assert 'notice_received' in flags

def test_run_interview_with_followup():
    # Create mock YAML with follow-up logic
    yaml_data = {
        'questions': [
            {
                'id': 'condition',
                'type': 'boolean',
                'prompt': 'Condition?',
                'next': 'followup',
                'followup': {
                    'yes': 'followup'
                }
            },
            {
                'id': 'followup',
                'type': 'text',
                'prompt': 'Follow-up',
                'next': 'end'
            },
            {
                'id': 'end',
                'type': 'summary',
                'prompt': 'End'
            }
        ]
    }
    
    # Mock input
    with patch('builtins.input', side_effect=['y', 'followup answer']):
        answers, flags = run_interview(yaml_data)
        assert 'followup' in answers
        assert answers['followup'] == 'followup answer'

def teardown_module():
    """Clean up any generated test files"""
    test_files = ['test_questions.yaml']
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
