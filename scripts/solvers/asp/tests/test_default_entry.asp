not filed_pleading(defendant, complaint).
days_since_service_at_least(defendant, 30).

% Rule: Clerk may enter default if no response filed within 30 days
clerk_enters_default(defendant) :-
    not filed_pleading(defendant, complaint),
    days_since_service_at_least(defendant, 30).

% Show which conclusions are true
#show clerk_enters_default/1.
