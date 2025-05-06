% Test Relief for Improper Service (Case Law)
% ---------------------------------------------------------------------
% This test verifies that a defendant can vacate a default judgment when:
% 1. A default judgment has been taken
% 2. The service was improper
% 3. The motion is filed within 2 years of judgment

% Base facts for testing improper service
% Scenario: Service attempted at wrong address
default_judgment_taken(defendant).
void_due_improper_service(defendant).
days_since_entry(defendant, 720).  % Within 2 years

% Show which conclusions are true
#show vacate_default_judgment/1.

% Show base facts for debugging
#show default_judgment_taken/1.
#show void_due_improper_service/1.
#show days_since_entry/2.

% Test negative case: proper service
default_judgment_taken(defendant).
days_since_entry(defendant, 720).
#show vacate_default_judgment/1.

% Test negative case: outside 2-year window
default_judgment_taken(defendant).
void_due_improper_service(defendant).
days_since_entry(defendant, 731).  % Just over 2 years
#show vacate_default_judgment/1.
