% ---------------------------------------------------------------------
% Enhanced Test for Excusable Neglect Relief (CCP §473(b))
% ---------------------------------------------------------------------
% This enhanced test suite provides comprehensive coverage of excusable
% neglect relief scenarios, including edge cases and detailed debugging.
% ---------------------------------------------------------------------

% References to Main Code
% ----------------------
% See ud_vacate.asp:72-74 for the main rule implementation:
% vacate_default_judgment(defendant) :-
%     default_judgment_taken(defendant),
%     excusable_neglect(defendant),
%     within_six_months_judgment(defendant).

% ---------------------------------------------------------------------
% Test Suite Structure
% ---------------------------------------------------------------------
% 1. Positive Test Cases
% 2. Negative Test Cases
% 3. Edge Cases
% 4. Invalid Input Cases
% 5. Time Boundary Cases

% ---------------------------------------------------------------------
% Positive Test Cases
% ---------------------------------------------------------------------
% Case 1: Standard Hospitalization Scenario
% ---------------------------------------------------------------------
% Metadata
% --------
% Legal Citation: CCP §473(b)
% Test Type: Positive
% Scenario: Hospitalization preventing filing
% Expected Result: Judgment can be vacated
% Time Window: Within 6 months

% Base facts
% ---------
default_judgment_taken(defendant).
excusable_neglect(defendant).
days_since_entry(defendant, 120).  % Within 6 months

% Debug Information
% ----------------
% Time Calculations
days(0..1000).  % Maximum of 1000 days
#show days/1.  % Show all possible days

% Rule Dependencies
#show default_judgment_taken/1.
#show excusable_neglect/1.
#show days_since_entry/2.

% Rule Analysis
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Negative Test Cases
% ---------------------------------------------------------------------
% Case 2: Outside 6-Month Window
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Negative
% Scenario: Motion filed just after 6-month window
% Expected Result: Judgment cannot be vacated
% Time Window: 181 days

% Base facts
default_judgment_taken(defendant).
excusable_neglect(defendant).
days_since_entry(defendant, 181).  % Just over 6 months

% Debug Information
#show days_since_entry/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Edge Cases
% ---------------------------------------------------------------------
% Case 3: Exactly 6-Month Boundary
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Edge Case
% Scenario: Motion filed exactly at 6-month boundary
% Expected Result: Judgment can be vacated
% Time Window: 180 days

% Base facts
default_judgment_taken(defendant).
excusable_neglect(defendant).
days_since_entry(defendant, 180).  % Exactly 6 months

% Debug Information
#show days_since_entry/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Invalid Input Cases
% ---------------------------------------------------------------------
% Case 4: Invalid Day Value
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Invalid Input
% Scenario: Negative day value
% Expected Result: No solution
% Time Window: -1 days

% Base facts
default_judgment_taken(defendant).
excusable_neglect(defendant).
days_since_entry(defendant, -1).  % Invalid negative value

% Debug Information
#show days_since_entry/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Time Boundary Cases
% ---------------------------------------------------------------------
% Case 5: Multiple Time Windows
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Time Boundary
% Scenario: Multiple concurrent time windows
% Expected Result: Judgment can be vacated
% Time Windows: 180 days (6 months), 150 days (notice)

% Base facts
default_judgment_taken(defendant).
excusable_neglect(defendant).
days_since_entry(defendant, 150).  % Within both windows

% Debug Information
#show days_since_entry/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Test Execution Control
% ---------------------------------------------------------------------
% Show all conclusions and base facts for debugging
#show vacate_default_judgment/1.
#show default_judgment_taken/1.
#show excusable_neglect/1.
#show days_since_entry/2.
#show days/1.
