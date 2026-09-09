# General Intent Train/Test Evaluation

- Source examples: 457
- Training examples: 366 (80%)
- Holdout test examples: 91 (20%)
- Split seed: 42
- Intent-routing accuracy: 44.0% (40/91)
- Full-corpus regression routing: 92.8% (424/457)

The holdout result evaluates routing with only the training examples loaded. The full-corpus result is a regression check for the production intent file, not a second holdout score.

| Language | Question | Expected intent | Predicted intent | Result |
| --- | --- | --- | --- | --- |
| ar | فكرة هدية | gift | gift | PASS |
| en | anniversary gift | gift | gift | PASS |
| ar | هدية عيد ميلاد | gift | gift | PASS |
| ar | مع السلامة | goodbye | greeting | FAIL |
| en | see you | goodbye | qa_goodbye | FAIL |
| en | have a nice day | goodbye | qa_question_invitation | FAIL |
| ar | مرحبا بك | greeting | greeting | PASS |
| en | hi there | greeting | greeting | PASS |
| en | good afternoon | greeting | qa_greeting | FAIL |
| en | hey | greeting | qa_greeting | FAIL |
| ar | اهلين | greeting | greeting | PASS |
| ar | اريد الدعم | help | gift | FAIL |
| en | please help me | help | help | PASS |
| ar | هل يمكنك مساعدتي | help | help | PASS |
| ar | ما هو مساعد منسم | identity | help | FAIL |
| en | who are you | identity | qa_who_are_you | FAIL |
| en | i am sorry | qa_apology | qa_apology | PASS |
| en | do i need to pay | qa_are_you_free | qa_question_invitation | FAIL |
| en | are you a robot | qa_are_you_human | qa_are_you_human | PASS |
| en | are you real | qa_are_you_human | qa_are_you_human | PASS |
| en | is this secure | qa_are_you_secure | qa_are_you_secure | PASS |
| en | do you store my information | qa_are_you_secure | qa_small_talk_name | FAIL |
| en | what do you do for fun | qa_bot_hobbies | qa_what_can_you_do | FAIL |
| en | do you remember me | qa_can_you_learn | qa_do_you_love_me | FAIL |
| en | do you know any songs | qa_can_you_sing | qa_tell_joke | FAIL |
| en | you are amazing | qa_compliment_bot | qa_insult_bot | FAIL |
| en | you're great | qa_compliment_bot | qa_welcome_response | FAIL |
| en | can we talk | qa_conversation_companion | qa_conversation_companion | PASS |
| en | chat with me | qa_conversation_companion | qa_conversation_companion | PASS |
| en | do you have feelings | qa_do_you_have_feelings | qa_do_you_have_friends | FAIL |
| en | do you have any friends | qa_do_you_have_friends | qa_do_you_have_friends | PASS |
| en | will you marry me | qa_do_you_love_me | qa_can_you_call_me | FAIL |
| en | do you need rest | qa_do_you_sleep | qa_do_you_sleep | PASS |
| en | what is your favorite color | qa_favorite_color | qa_favorite_food | FAIL |
| en | do you eat food | qa_favorite_food | qa_what_can_you_do | FAIL |
| en | farewell | qa_goodbye | qa_compliment_bot | FAIL |
| en | talk to you later | qa_goodbye | goodbye | FAIL |
| en | goodbye | qa_goodbye | goodbye | FAIL |
| en | see ya | qa_goodbye | qa_goodbye | PASS |
| en | hii | qa_greeting | greeting | FAIL |
| en | howdy | qa_greeting | qa_how_are_you | FAIL |
| en | hello there | qa_greeting | qa_greeting | PASS |
| en | hi | qa_greeting | greeting | FAIL |
| en | hii there | qa_greeting | greeting | FAIL |
| en | hii my friend | qa_greeting | greeting | FAIL |
| en | how's everything | qa_how_are_you | qa_how_are_you | PASS |
| en | you doing okay? | qa_how_are_you | qa_how_are_you | PASS |
| en | im fine | qa_how_are_you | qa_how_are_you | PASS |
| en | how r u | qa_how_are_you | qa_how_are_you | PASS |
| en | you good? | qa_how_are_you | qa_how_are_you | PASS |
| en | hw r u | qa_how_are_you | qa_how_are_you | PASS |
| en | is it raining | qa_how_is_the_weather | qa_how_is_the_weather | PASS |
| en | how old are you | qa_how_old_are_you | qa_how_are_you | FAIL |
| en | you are bad | qa_insult_bot | qa_insult_bot | PASS |
| en | you are useless | qa_insult_bot | qa_compliment_bot | FAIL |
| en | i had a bad day | qa_negative_mood | qa_how_are_you | FAIL |
| en | i feel lonely | qa_negative_mood | qa_negative_mood | PASS |
| en | great to meet you | qa_nice_to_meet_you | qa_nice_to_meet_you | PASS |
| en | nah | qa_no_response | qa_greeting | FAIL |
| en | i'm feeling good | qa_positive_mood | qa_negative_mood | FAIL |
| en | i want to ask something | qa_question_invitation | qa_question_invitation | PASS |
| en | entertain me | qa_small_talk_bored | qa_what_is_ai | FAIL |
| en | who am i | qa_small_talk_name | qa_who_are_you | FAIL |
| en | another joke | qa_tell_joke | qa_tell_joke | PASS |
| en | thanks for the help | qa_thanks | qa_thanks | PASS |
| en | thanks a bunch | qa_thanks | qa_thanks | PASS |
| en | thank u | qa_thanks | qa_thanks | PASS |
| en | np | qa_welcome_response | qa_greeting | FAIL |
| en | can you help me | qa_what_can_you_do | help | FAIL |
| en | help | qa_what_can_you_do | help | FAIL |
| en | what is artificial intelligence | qa_what_is_ai | qa_what_is_ai | PASS |
| en | what's today's date | qa_what_is_the_date | qa_what_is_the_date | PASS |
| en | what is your favorite animal | qa_what_is_your_favorite_animal | qa_favorite_food | FAIL |
| en | do you like reading | qa_what_is_your_favorite_book | qa_what_is_your_favorite_animal | FAIL |
| en | what is your favorite movie | qa_what_is_your_favorite_movie | qa_favorite_food | FAIL |
| en | why were you created | qa_what_is_your_purpose | qa_how_old_are_you | FAIL |
| en | do you know hindi | qa_what_language_do_you_speak | help | FAIL |
| en | tell me the time | qa_what_time_is_it | qa_tell_joke | FAIL |
| en | where do you live | qa_where_are_you_from | shipping | FAIL |
| en | tell me about yourself | qa_who_are_you | identity | FAIL |
| en | what should i call you | qa_who_are_you | qa_small_talk_food_recommendation | FAIL |
| en | sure | qa_yes_response | returns | FAIL |
| ar | استرجاع | returns | returns | PASS |
| en | can i return | returns | returns | PASS |
| ar | الشحن | shipping | thanks | FAIL |
| en | delivery | shipping | shipping | PASS |
| ar | يعطيك العافية | thanks | goodbye | FAIL |
| en | i appreciate it | thanks | qa_thanks | FAIL |
| ar | شكراً | thanks | thanks | PASS |
| ar | كيفك | wellbeing | wellbeing | PASS |
| en | how do you feel | wellbeing | qa_how_are_you | FAIL |
