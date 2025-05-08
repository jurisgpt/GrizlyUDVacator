% ud_vacate.asp - ASP rules for vacating default judgments in CA unlawful detainer cases
% ----------------------------------------------------------------------------
% This ASP program encodes procedural grounds (statutes and case law)
% for vacating default judgments in California unlawful detainer matters.
% Each rule is a Horn-style "IF ... THEN ... [Citation]" statement.

% --- Base Predicates ---
% personal_delivery(S, C, D): Summons S and Complaint C were delivered to Defendant D
% reasonable_diligence_attempted(D, C): Diligent attempts were made to deliver Complaint C to Defendant D
% filed_pleading(D, C): Defendant D has filed a pleading in response to Complaint C
% days_since_service(D, N): Number of days since service for Defendant D
% days_since_entry(D, N): Number of days since entry of judgment for Defendant D
% days_since_notice(D, N): Number of days since notice was given to Defendant D
% default_judgment_void(D): Default judgment against Defendant D is void
% void_due_improper_service(D): Default judgment against Defendant D is void due to improper service
% actual_notice_received(D): Defendant D received actual notice
% notice_given(D, P): Notice was given to Defendant D by Party P
% excusable_neglect(D): Defendant D shows excusable neglect
% service_type(D, T): Type of service used for Defendant D
% notice_type(P, T): Type of notice given by Party P
% void_reason(D, R): Reason why judgment against Defendant D is void

% Domain constraints
days(0..1000).  % Maximum of 1000 days

% Debug Information
% Basic Facts
#show days/1.  % Show all possible days
#show default_judgment_taken/1.  % Show if default judgment was taken
#show excusable_neglect/1.  % Show if excusable neglect exists
#show days_since_entry/2.  % Show days since entry
#show service_type/2.  % Show service types
#show notice_type/2.  % Show notice types
#show void_reason/2.  % Show void reasons

% Rule Evaluation
#show vacate_default_judgment/1.  % Show final judgment vacate status
#show within_six_months_judgment/1.  % Show time window status
#show within_two_years_entry/1.  % Show extended time window status
#show within_limit_473_5/1.  % Show CCP §473.5 time limit status

% Service and Notice Details
#show days_since_service/2.  % Show days since service
#show days_since_notice/2.  % Show days since notice
#show personal_delivery/3.  % Show personal delivery status
#show reasonable_diligence_attempted/1.  % Show diligence status
#show filed_pleading/2.  % Show pleading filing status
#show actual_notice_received/1.  % Show notice receipt status
#show notice_given/2.  % Show notice given status

% Time Window Calculations
#show days/1.  % Show all possible days
#show days_since_entry/2.  % Show days since entry
#show days_since_notice/2.  % Show days since notice
#show days_since_service/2.  % Show days since service

% Rule Dependencies
#show default_judgment_taken/1.  % Show default judgment status
#show excusable_neglect/1.  % Show excusable neglect status
#show within_six_months_judgment/1.  % Show time window status
#show default_judgment_void/1.  % Show void judgment status
#show void_due_improper_service/1.  % Show improper service status

% Helper predicates for enhanced testing
service_type(defendant, "personal").
service_type(defendant, "substituted").
notice_type(plaintiff, "service").
notice_type(plaintiff, "mail").
void_reason(defendant, "jurisdiction").
void_reason(defendant, "due_process").

% Ensure temporal predicates use grounded variables
days_since_service_at_least(P, N) :- days_since_service(P, D), days(N), D >= N.
within_six_months_judgment(P) :- days_since_entry(P, D), days(D), D <= 180.
within_two_years_entry(P) :- days_since_entry(P, D), days(D), D <= 730.
within_limit_473_5(P) :- within_two_years_entry(P).
within_limit_473_5(P) :- days_since_notice(P, N), days(N), N <= 180.

% Base Predicates
% Service of Process
personal_delivery(summons, complaint, defendant) :-
    service_type(defendant, "personal"),
    days_since_service(defendant, D),
    D >= 0.
% Debug: Personal service status
#show personal_delivery/3.

% Rule: Service by publication requires proof of diligent attempts (CCP §415.50)
reasonable_diligence_attempted(defendant) :-
    service_type(defendant, "publication").
% Debug: Publication service status
#show reasonable_diligence_attempted/1.

% --- Rule Facts: Pleadings ---
% Rule: Pleading must be filed after service (CCP §412.20)
filed_pleading(defendant, complaint) :-
    days_since_service(defendant, D),
    D >= 0.
% Debug: Pleading filing status
#show filed_pleading/2.

% Debug: Service type tracking
#show service_type/2.

% Debug: Days calculations
#show days_since_service/2.
#show days_since_entry/2.
#show days_since_notice/2.

% Notice
actual_notice_received(defendant) :-
    notice_given(defendant, plaintiff),
    days_since_notice(defendant, D),
    D >= 0.

notice_given(defendant, plaintiff) :-
    notice_type(plaintiff, "service"),
    days_since_notice(defendant, D),
    D >= 0.

% Judgment Status
default_judgment_void(defendant) :-
    void_reason(defendant, "jurisdiction"),
    days_since_entry(defendant, D),
    D >= 0.

void_due_improper_service(defendant) :-
    service_type(defendant, "substituted"),
    days_since_service(defendant, D),
    D >= 0.

% Rule for proper service
proper_service_completed(defendant) :-
    service_type(defendant, "personal"),
    days_since_service(defendant, D),
    D >= 0.

% Rule for vacating judgment due to improper service
vacate_default_judgment(defendant) :-
    default_judgment_taken(defendant),
    void_due_improper_service(defendant),
    within_two_years_entry(defendant).

% Rule for not vacating judgment when proper service exists
:- default_judgment_taken(defendant),
   proper_service_completed(defendant),
   not void_due_improper_service(defendant).

% Time Tracking
days_since_service(defendant, D) :- days(D).
days_since_entry(defendant, D) :- days(D).
days_since_notice(defendant, D) :- days(D).

% --- Rule Facts: Service of Process ---
% Rule: Personal service completes upon direct delivery (CCP §415.10)
service_complete(defendant) :- personal_delivery(summons, complaint, defendant).

% Rule: Substituted service valid when personal delivery fails with diligence (CCP §415.20(b))
substituted_service_valid(defendant) :-
    not personal_delivery(summons, complaint, defendant),
    reasonable_diligence_attempted(defendant).

% --- Rule Facts: Entry of Default ---
% Rule: Clerk may enter default if no response filed within 30 days (CCP §585(a))
clerk_enters_default(defendant) :-
    not filed_pleading(defendant, complaint),
    days_since_service_at_least(defendant, 30).

% --- Rule Facts: Relief from Default Judgment ---
% Rule: Relief for CCP §473.5(a)
% A motion to vacate must be filed within 180 days of entry or notice of judgment
% AND the defendant did not receive actual notice
vacate_default_judgment(defendant) :-
    default_judgment_taken(defendant),
    not actual_notice_received(defendant),
    days_since_entry(defendant, D1),
    days(D1),
    D1 <= 180.

vacate_default_judgment(defendant) :-
    default_judgment_taken(defendant),
    not actual_notice_received(defendant),
    days_since_notice(defendant, D2),
    days(D2),
    D2 <= 180.

% Helper predicates for time calculations
days_since_entry(defendant, D) :- days(D).
days_since_notice(defendant, D) :- days(D).

% Debug information
#show days/1.
#show days_since_entry/2.
#show days_since_notice/2.
#show vacate_default_judgment/1.



% ----------------------------------------------------------------------------
% Sample Test Scenario: Excusable Neglect Relief

default_judgment_taken(defendant).
excusable_neglect(defendant).
days_since_entry(defendant, 100).

% Show which conclusions are true in this scenario
#show vacate_default_judgment/1.
