% Test Excusable Neglect Relief (CCP §473(b))
% ---------------------------------------------------------------------
% This test verifies that a defendant can vacate a default judgment when:
% 1. A default judgment has been taken
% 2. The defendant shows excusable neglect
% 3. The motion is filed within 6 months of judgment

% Base facts for testing excusable neglect
% Scenario: Defendant missed filing due to hospitalization

default_judgment_taken(defendant).
excusable_neglect(defendant).
days_since_entry(defendant, 120).  % Within 6 months

% Show which conclusions are true
#show vacate_default_judgment/1.

% Show base facts for debugging
#show default_judgment_taken/1.
#show excusable_neglect/1.
#show days_since_entry/2.

% Test negative case: outside 6-month window
days_since_entry(defendant, 181).  % Just over 6 months
#show vacate_default_judgment/1.

% Test negative case: no excusable neglect
default_judgment_taken(defendant).
days_since_entry(defendant, 120).
#show vacate_default_judgment/1.
