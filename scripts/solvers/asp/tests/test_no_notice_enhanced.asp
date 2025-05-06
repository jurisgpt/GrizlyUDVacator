% ---------------------------------------------------------------------
% Enhanced Test for No Actual Notice Relief (CCP §473.5(a))
% ---------------------------------------------------------------------
% This enhanced test suite provides comprehensive coverage of no notice
% relief scenarios, including edge cases and detailed debugging.
% ---------------------------------------------------------------------

% References to Main Code
% ----------------------
% See ud_vacate.asp:76-78 for the main rule implementation:
% vacate_default_judgment(defendant) :-
%     default_judgment_taken(defendant),
%     not actual_notice_received(defendant),
%     within_limit_473_5(defendant).

% ---------------------------------------------------------------------
% Test Suite Structure
% ---------------------------------------------------------------------
% 1. Positive Test Cases
% 2. Negative Test Cases
% 3. Edge Cases
% 4. Invalid Input Cases
% 5. Time Boundary Cases
% 6. Notice Type Cases

% ---------------------------------------------------------------------
% Positive Test Cases
% ---------------------------------------------------------------------
% Case 1: Standard No Notice Scenario
% ---------------------------------------------------------------------
% Metadata
% --------
% Legal Citation: CCP §473.5(a)
% Test Type: Positive
% Scenario: No notice received within time limits
% Expected Result: Judgment can be vacated
% Time Windows: Within 180 days of notice and 2 years of judgment

% Base facts
default_judgment_taken(defendant).
not actual_notice_received(defendant).
days_since_entry(defendant, 365).  % Within 2 years
days_since_notice(defendant, 150).  % Within 180 days

% Debug Information
#show days_since_entry/2.
#show days_since_notice/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Negative Test Cases
% ---------------------------------------------------------------------
% Case 2: Notice Received Scenario
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Negative
% Scenario: Actual notice received
% Expected Result: Judgment cannot be vacated
% Time Windows: Within limits

% Base facts
default_judgment_taken(defendant).
days_since_entry(defendant, 365).
days_since_notice(defendant, 150).
actual_notice_received(defendant).

% Debug Information
#show actual_notice_received/1.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Edge Cases
% ---------------------------------------------------------------------
% Case 3: Multiple Time Window Boundaries
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Edge Case
% Scenario: Multiple concurrent time window boundaries
% Expected Result: Judgment can be vacated
% Time Windows: 730 days (2 years), 180 days (notice)

% Base facts
default_judgment_taken(defendant).
not actual_notice_received(defendant).
days_since_entry(defendant, 730).  % Exactly 2 years
days_since_notice(defendant, 180).  % Exactly 180 days

% Debug Information
#show days_since_entry/2.
#show days_since_notice/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Invalid Input Cases
% ---------------------------------------------------------------------
% Case 4: Invalid Notice Day Value
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Invalid Input
% Scenario: Negative notice day value
% Expected Result: No solution
% Time Windows: Invalid

% Base facts
default_judgment_taken(defendant).
not actual_notice_received(defendant).
days_since_entry(defendant, 365).
days_since_notice(defendant, -1).  % Invalid negative value

% Debug Information
#show days_since_notice/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Time Boundary Cases
% ---------------------------------------------------------------------
% Case 5: Just Outside Time Windows
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Time Boundary
% Scenario: Just outside both time windows
% Expected Result: Judgment cannot be vacated
% Time Windows: 731 days (2 years + 1), 181 days (notice + 1)

% Base facts
default_judgment_taken(defendant).
not actual_notice_received(defendant).
days_since_entry(defendant, 731).  % Just over 2 years
days_since_notice(defendant, 181).  % Just over 180 days

% Debug Information
#show days_since_entry/2.
#show days_since_notice/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Notice Type Cases
% ---------------------------------------------------------------------
% Case 6: Multiple Notice Types
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Notice Type
% Scenario: Multiple notice types with different time windows
% Expected Result: Judgment can be vacated if any notice is valid
% Time Windows: Various combinations

% Base facts
default_judgment_taken(defendant).
not actual_notice_received(defendant).
days_since_entry(defendant, 720).  % Within 2 years
days_since_notice(defendant, 179).  % Within 180 days

% Debug Information
#show days_since_entry/2.
#show days_since_notice/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Test Execution Control
% ---------------------------------------------------------------------
% Show all conclusions and base facts for debugging
#show vacate_default_judgment/1.
#show default_judgment_taken/1.
#show actual_notice_received/1.
#show days_since_entry/2.
#show days_since_notice/2.
#show days/1.
