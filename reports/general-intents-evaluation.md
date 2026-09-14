# General Intent Train/Test Evaluation

- Source examples: 485
- Training examples: 388 (80%)
- Holdout test examples: 97 (20%)
- Split seed: 42
- Intent-routing accuracy: 41.2% (40/97)
- Full-corpus regression routing: 93.2% (452/485)

The holdout result evaluates routing with only the training examples loaded. The full-corpus result is a regression check for the production intent file, not a second holdout score.

| Language | Question | Expected intent | Predicted intent | Result |
| --- | --- | --- | --- | --- |
| ar | أريد هدية | gift | gift | PASS |
| en | birthday gift | gift | gift | PASS |
| en | perfume gift | gift | gift | PASS |
| ar | نراك لاحقا | goodbye | thanks | FAIL |
| en | have a nice day | goodbye | qa_question_invitation | FAIL |
| ar | في امان الله | goodbye | goodbye | PASS |
| ar | مرحبا بك | greeting | greeting | PASS |
| en | hey there | greeting | qa_greeting | FAIL |
| en | good afternoon | greeting | qa_greeting | FAIL |
| ar | مرحبتين | greeting | greeting | PASS |
| en | good day | greeting | qa_greeting | FAIL |
| ar | كيف تساعدني | help | help | PASS |
| en | what do you know | help | qa_what_can_you_do | FAIL |
| ar | ماذا تعرف | help | help | PASS |
| ar | هل انت انسان | identity | wellbeing | FAIL |
| en | who are you | identity | qa_who_are_you | FAIL |
| en | i am sorry | qa_apology | qa_apology | PASS |
| en | are you free | qa_are_you_free | qa_are_you_human | FAIL |
| en | are you a robot | qa_are_you_human | qa_are_you_human | PASS |
| en | is this a bot | qa_are_you_human | qa_are_you_secure | FAIL |
| en | is this secure | qa_are_you_secure | qa_are_you_secure | PASS |
| en | is this chat private | qa_are_you_secure | qa_are_you_secure | PASS |
| en | what do you do for fun | qa_bot_hobbies | qa_what_can_you_do | FAIL |
| en | do math for me | qa_can_you_count | qa_can_you_tell_story | FAIL |
| en | do you get smarter | qa_can_you_learn | qa_do_you_sleep | FAIL |
| en | do you play video games | qa_can_you_play_games | qa_can_you_play_games | PASS |
| en | sing a song | qa_can_you_sing | qa_question_invitation | FAIL |
| en | tell me a story | qa_can_you_tell_story | qa_tell_joke | FAIL |
| en | nice work | qa_compliment_bot | qa_nice_to_meet_you | FAIL |
| en | you are helpful | qa_compliment_bot | qa_insult_bot | FAIL |
| en | let's chat | qa_conversation_companion | qa_conversation_companion | PASS |
| en | i need someone to chat with | qa_conversation_companion | qa_are_you_free | FAIL |
| en | are you sad | qa_do_you_have_feelings | qa_are_you_human | FAIL |
| en | do you have friends | qa_do_you_have_friends | qa_do_you_have_friends | PASS |
| en | i love you | qa_do_you_love_me | qa_compliment_bot | FAIL |
| en | do you need rest | qa_do_you_sleep | qa_do_you_sleep | PASS |
| en | do you have a favorite color | qa_favorite_color | qa_can_you_learn | FAIL |
| en | what is your favorite food | qa_favorite_food | qa_what_is_your_favorite_book | FAIL |
| en | later | qa_goodbye | qa_goodbye | PASS |
| en | cya | qa_goodbye | qa_greeting | FAIL |
| en | see you | qa_goodbye | goodbye | FAIL |
| en | catch you later | qa_goodbye | qa_goodbye | PASS |
| en | hey friend | qa_greeting | qa_greeting | PASS |
| en | hey there | qa_greeting | qa_greeting | PASS |
| en | hiii | qa_greeting | qa_greeting | PASS |
| en | hello bot | qa_greeting | qa_greeting | PASS |
| en | hey buddy | qa_greeting | qa_greeting | PASS |
| en | namaste | qa_greeting | qa_who_are_you | FAIL |
| en | i am good | qa_how_are_you | qa_how_are_you | PASS |
| en | how are you | qa_how_are_you | wellbeing | FAIL |
| en | how are u today | qa_how_are_you | wellbeing | FAIL |
| en | i am fine | qa_how_are_you | qa_how_are_you | PASS |
| en | what's up | qa_how_are_you | qa_greeting | FAIL |
| en | i'm fine how about you | qa_how_are_you | qa_how_are_you | PASS |
| en | is it sunny today | qa_how_is_the_weather | qa_how_is_the_weather | PASS |
| en | when were you born | qa_how_old_are_you | qa_how_old_are_you | PASS |
| en | you are annoying | qa_insult_bot | qa_compliment_bot | FAIL |
| en | you are dumb | qa_insult_bot | qa_insult_bot | PASS |
| en | i am stressed | qa_negative_mood | qa_negative_mood | PASS |
| en | i had a bad day | qa_negative_mood | qa_insult_bot | FAIL |
| en | great to meet you | qa_nice_to_meet_you | qa_nice_to_meet_you | PASS |
| en | nah | qa_no_response | qa_who_are_you | FAIL |
| en | i'm feeling good | qa_positive_mood | qa_negative_mood | FAIL |
| en | i need to ask you something | qa_question_invitation | qa_question_invitation | PASS |
| en | i am bored | qa_small_talk_bored | qa_small_talk_bored | PASS |
| en | do you know my name | qa_small_talk_name | qa_tell_joke | FAIL |
| en | joke please | qa_tell_joke | qa_who_are_you | FAIL |
| en | thank you so much | qa_thanks | thanks | FAIL |
| en | much appreciated | qa_thanks | qa_thanks | PASS |
| en | many thanks | qa_thanks | thanks | FAIL |
| en | np | qa_welcome_response | qa_greeting | FAIL |
| en | what are your features | qa_what_can_you_do | qa_who_are_you | FAIL |
| en | how do you work | qa_what_can_you_do | qa_how_are_you | FAIL |
| en | define artificial intelligence | qa_what_is_ai | qa_are_you_human | FAIL |
| en | what day is it | qa_what_is_the_date | qa_what_time_is_it | FAIL |
| en | what is your favorite animal | qa_what_is_your_favorite_animal | qa_favorite_color | FAIL |
| en | do you read books | qa_what_is_your_favorite_book | qa_how_are_you | FAIL |
| en | do you like movies | qa_what_is_your_favorite_movie | qa_what_is_your_favorite_movie | PASS |
| en | do you like sports | qa_what_is_your_favorite_sport | qa_what_is_your_favorite_animal | FAIL |
| en | are you a boy or girl | qa_what_is_your_gender | qa_are_you_human | FAIL |
| en | why do you exist | qa_what_is_your_purpose | qa_what_can_you_do | FAIL |
| en | do you know hindi | qa_what_language_do_you_speak | qa_tell_joke | FAIL |
| en | tell me the time | qa_what_time_is_it | qa_tell_joke | FAIL |
| en | where do you live | qa_where_are_you_from | shipping | FAIL |
| en | do you have a name | qa_who_are_you | qa_can_you_learn | FAIL |
| en | tell me about yourself | qa_who_are_you | identity | FAIL |
| en | why should i use you | qa_why_should_i_use_you | qa_why_should_i_use_you | PASS |
| en | sure | qa_yes_response | returns | FAIL |
| ar | إرجاع | returns | returns | PASS |
| en | exchange | returns | qa_thanks | FAIL |
| ar | متى يصل | shipping | help | FAIL |
| en | delivery | shipping | shipping | PASS |
| ar | مشكور | thanks | thanks | PASS |
| en | i appreciate it | thanks | qa_thanks | FAIL |
| en | thanks a lot | thanks | qa_thanks | FAIL |
| ar | كيفك | wellbeing | wellbeing | PASS |
| en | are you okay | wellbeing | qa_how_are_you | FAIL |
