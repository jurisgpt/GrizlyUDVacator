% Base facts for testing
personal_delivery(summons, complaint, defendant).
reasonable_diligence_attempted(defendant, complaint).
filed_pleading(defendant, complaint).
days_since_service(defendant, 30).
days_since_entry(defendant, 100).
days_since_notice(defendant, 150).
default_judgment_void(defendant).
void_due_improper_service(defendant).

% Show all base predicates
#show personal_delivery/3.
#show reasonable_diligence_attempted/2.
#show filed_pleading/2.
#show days_since_service/2.
#show days_since_entry/2.
#show days_since_notice/2.
#show default_judgment_void/1.
#show void_due_improper_service/1.
