% ---------------------------------------------------------------------
% Enhanced Test for Void Judgment Relief (CCP §473(d))
% ---------------------------------------------------------------------
% This enhanced test suite provides comprehensive coverage of void
% judgment relief scenarios, including edge cases and detailed debugging.
% ---------------------------------------------------------------------

% References to Main Code
% ----------------------
% See ud_vacate.asp:80-82 for the main rule implementation:
% vacate_default_judgment(defendant) :-
%     default_judgment_void(defendant),
%     notice_given(defendant, plaintiff).

% ---------------------------------------------------------------------
% Test Suite Structure
% ---------------------------------------------------------------------
% 1. Positive Test Cases
% 2. Negative Test Cases
% 3. Edge Cases
% 4. Invalid Input Cases
% 5. Notice Type Cases
% 6. Void Judgment Types

% ---------------------------------------------------------------------
% Positive Test Cases
% ---------------------------------------------------------------------
% Case 1: Standard Void Judgment Scenario
% ---------------------------------------------------------------------
% Metadata
% --------
% Legal Citation: CCP §473(d)
% Test Type: Positive
% Scenario: Void judgment with proper notice
% Expected Result: Judgment can be vacated

% Base facts
default_judgment_void(defendant).
notice_given(defendant, plaintiff).

% Debug Information
#show default_judgment_void/1.
#show notice_given/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Negative Test Cases
% ---------------------------------------------------------------------
% Case 2: Valid Judgment Scenario
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Negative
% Scenario: Valid judgment entered
% Expected Result: Judgment cannot be vacated

% Base facts
default_judgment_taken(defendant).
notice_given(defendant, plaintiff).

% Debug Information
#show default_judgment_void/1.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Edge Cases
% ---------------------------------------------------------------------
% Case 3: Multiple Parties Notice
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Edge Case
% Scenario: Notice given to multiple parties
% Expected Result: Judgment can be vacated

% Base facts
default_judgment_void(defendant).
notice_given(defendant, plaintiff).
notice_given(defendant, third_party).

% Debug Information
#show notice_given/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Invalid Input Cases
% ---------------------------------------------------------------------
% Case 4: Invalid Party Input
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Invalid Input
% Scenario: Invalid party identifier
% Expected Result: No solution

% Base facts
default_judgment_void(defendant).
notice_given(defendant, "invalid_party").

% Debug Information
#show notice_given/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Notice Type Cases
% ---------------------------------------------------------------------
% Case 5: Notice Variations
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Notice Type
% Scenario: Different types of notice
% Expected Result: Judgment can be vacated if proper notice given

% Base facts
default_judgment_void(defendant).
notice_given(defendant, plaintiff).
notice_type(plaintiff, "service").
notice_type(plaintiff, "mail").

% Debug Information
#show notice_type/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Void Judgment Types
% ---------------------------------------------------------------------
% Case 6: Various Void Judgment Types
% ---------------------------------------------------------------------
% Metadata
% --------
% Test Type: Void Judgment Type
% Scenario: Different types of void judgments
% Expected Result: Judgment can be vacated if void

% Base facts
default_judgment_void(defendant).
notice_given(defendant, plaintiff).
void_reason(defendant, "jurisdiction").
void_reason(defendant, "due_process").

% Debug Information
#show void_reason/2.
#show vacate_default_judgment/1.

% ---------------------------------------------------------------------
% Test Execution Control
% ---------------------------------------------------------------------
% Show all conclusions and base facts for debugging
#show vacate_default_judgment/1.
#show default_judgment_void/1.
#show notice_given/2.
#show notice_type/2.
#show void_reason/2.
