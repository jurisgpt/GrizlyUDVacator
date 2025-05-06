% Test Relief for No Actual Notice (CCP §473.5(a))
% ---------------------------------------------------------------------
% This test verifies that a defendant can vacate a default judgment when:
% 1. A default judgment has been taken
% 2. The defendant did not receive actual notice
% 3. The motion is filed within 180 days of notice or 2 years of judgment

% Base facts for testing no notice
% Scenario: Defendant never received notice of judgment

default_judgment_taken(defendant).
not actual_notice_received(defendant).
days_since_entry(defendant, 365).  % Within 2 years
days_since_notice(defendant, 150).  % Within 180 days

% Show which conclusions are true
#show vacate_default_judgment/1.

% Show base facts for debugging
#show default_judgment_taken/1.
#show actual_notice_received/1.
#show days_since_entry/2.
#show days_since_notice/2.

% Test negative case: received actual notice
default_judgment_taken(defendant).
days_since_entry(defendant, 365).
days_since_notice(defendant, 150).
actual_notice_received(defendant).
#show vacate_default_judgment/1.

% Test negative case: outside time limits
default_judgment_taken(defendant).
not actual_notice_received(defendant).
days_since_entry(defendant, 731).  % Just over 2 years
#show vacate_default_judgment/1.
