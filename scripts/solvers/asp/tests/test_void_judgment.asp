% Test Relief for Void Judgment (CCP §473(d))
% ---------------------------------------------------------------------
% This test verifies that a defendant can vacate a default judgment when:
% 1. The judgment is void
% 2. Proper notice was given to the defendant

% Base facts for testing void judgment
% Scenario: Judgment entered without proper service

default_judgment_void(defendant).
notice_given(defendant, plaintiff).

% Show which conclusions are true
#show vacate_default_judgment/1.

% Show base facts for debugging
#show default_judgment_void/1.
#show notice_given/2.

% Test negative case: valid judgment
default_judgment_taken(defendant).
notice_given(defendant, plaintiff).
#show vacate_default_judgment/1.

% Test negative case: no notice given
default_judgment_void(defendant).
#show vacate_default_judgment/1.
