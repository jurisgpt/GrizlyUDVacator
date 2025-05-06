service_type(defendant, "personal").
days_since_service(defendant, 0).

% Base facts
personal_delivery(summons, complaint, defendant).

% Rule: Personal service completes upon direct delivery
proper_service_completed(defendant) :-
    service_type(defendant, "personal"),
    days_since_service(defendant, D),
    D >= 0.

% Show conclusions
#show proper_service_completed/1.
#show days_since_service/2.
