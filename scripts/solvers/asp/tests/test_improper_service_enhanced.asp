% ---------------------------------------------------------------------
% Enhanced Test for Improper Service Relief (Case Law)
% ---------------------------------------------------------------------
% This enhanced test suite provides comprehensive coverage of improper
% service relief scenarios, including edge cases and detailed debugging.
% ---------------------------------------------------------------------

% References to Main Code
% ----------------------
% See ud_vacate.asp:84-86 for the main rule implementation:
% vacate_default_judgment(defendant) :-
%     default_judgment_taken(defendant),
%     void_due_improper_service(defendant),
%     within_two_years_entry(defendant).

% ---------------------------------------------------------------------
% Test Suite Structure
% ---------------------------------------------------------------------
% 1. Positive Test Cases
% 2. Negative Test Cases
% 3. Edge Cases
% 4. Invalid Input Cases
% 5. Service Type Cases
% 6. Time Boundary Cases

% ---------------------------------------------------------------------
% Positive Test Cases
% ---------------------------------------------------------------------
% Case 1: Standard Improper Service Scenario
% ---------------------------------------------------------------------
% Metadata
% --------
% Legal Citation: Case Law
% Test Type: Positive
% Scenario: Service at wrong address within time limit
% Expected Result: Judgment can be vacated
% Time Window: Within 2 years

% Base facts
default_judgment_taken(defendant).
void_due_improper_service(defendant).
days_since_entry(defendant, 720).  % Within 2 years

% Debug Information
#show days_since_entry/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Negative Test Cases
% ---------------------------------------------------------------------
% Case 2: Proper Service Scenario
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Negative
% Scenario: Proper service completed
% Expected Result: Judgment cannot be vacated
% Time Window: Within limits

% Base facts
default_judgment_taken(defendant).
days_since_entry(defendant, 720).
not void_due_improper_service(defendant).

% Debug Information
#show void_due_improper_service/1.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Edge Cases
% ---------------------------------------------------------------------
% Case 3: Multiple Service Attempts
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Edge Case
% Scenario: Multiple service attempts with different outcomes
% Expected Result: Judgment can be vacated if any service was improper
% Time Window: Within 2 years

% Base facts
default_judgment_taken(defendant).
void_due_improper_service(defendant).
days_since_entry(defendant, 720).

% Debug Information
#show days_since_entry/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Invalid Input Cases
% ---------------------------------------------------------------------
% Case 4: Invalid Service Data
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Invalid Input
% Scenario: Invalid service attempt data
% Expected Result: No solution
% Time Window: Invalid

% Base facts
default_judgment_taken(defendant).
void_due_improper_service(defendant).
days_since_entry(defendant, -1).  % Invalid negative value

% Debug Information
#show days_since_entry/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Service Type Cases
% ---------------------------------------------------------------------
% Case 5: Various Service Types
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Service Type
% Scenario: Different types of service attempts
% Expected Result: Judgment can be vacated if any service was improper

% Base facts
default_judgment_taken(defendant).
void_due_improper_service(defendant).
days_since_entry(defendant, 720).
service_type(defendant, "personal").
service_type(defendant, "substituted").

% Debug Information
#show service_type/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Time Boundary Cases
% ---------------------------------------------------------------------
% Case 6: Just Outside Time Window
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Time Boundary
% Scenario: Just outside 2-year window
% Expected Result: Judgment cannot be vacated
% Time Window: 731 days

% Base facts
default_judgment_taken(defendant).
void_due_improper_service(defendant).
days_since_entry(defendant, 731).  % Just over 2 years

% Debug Information
#show days_since_entry/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Test Execution Control
% ---------------------------------------------------------------------
% Show all conclusions and base facts for debugging
#show vacate_default_judgment/1.
#show default_judgment_taken/1.
#show void_due_improper_service/1.
#show days_since_entry/2.
#show service_type/2.
#show days/1.
