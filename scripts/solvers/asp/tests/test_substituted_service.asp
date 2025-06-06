% Test Case: Valid Substituted Service

% Service type - Only substituted service
service_type(defendant, "substituted").

% Temporal domain
days(0..1000).

% Service facts
days_since_service(defendant, 0).
days_since_service_at_least(defendant, 0).

% Reasonable diligence facts
reasonable_diligence_attempted(defendant).

% Notice facts
notice_given(defendant, plaintiff).
notice_type(plaintiff, "service").
days_since_notice(defendant, 0).

% Judgment facts
void_due_improper_service(defendant).
default_judgment_taken(defendant).
days_since_entry(defendant, 0).
within_two_years_entry(defendant).

% Pleading facts
not filed_pleading(defendant, complaint).

% Actual notice facts
not actual_notice_received(defendant).

% Show conclusions
#show substituted_service_valid/1.
#show days_since_service/2.
#show days_since_service_at_least/2.

% Debug information
#show service_type/2.
#show reasonable_diligence_attempted/1.
#show notice_given/2.
#show notice_type/2.
#show days_since_notice/2.
#show void_due_improper_service/1.
#show default_judgment_taken/1.
#show days_since_entry/2.
#show within_two_years_entry/1.

% Constraints
:- service_type(defendant, "personal"), service_type(defendant, "substituted").
:- days_since_service(defendant, D1), days_since_service(defendant, D2), D1 != D2.
:- days_since_service(defendant, D), D < 0.
:- days_since_notice(defendant, D), D < 0.
:- days_since_entry(defendant, D), D < 0.
:- days_since_service(defendant, D), D > 1000.
:- days_since_notice(defendant, D), D > 1000.
:- days_since_entry(defendant, D), D > 1000.

% Rule validation
:- substituted_service_valid(defendant), not not personal_delivery(summons, complaint, defendant).
:- substituted_service_valid(defendant), not reasonable_diligence_attempted(defendant).
