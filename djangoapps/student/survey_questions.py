import random
import settings

def exit_survey_list_for_student(student):
    # Right now, we just randomly pick some questions from random_questions
    common_questions = exit_survey_questions['common_questions']
    randomized_questions = exit_survey_questions['random_questions']
            
    #If we use random.sample on randomized_questions directly, it will re-arrange the questions
    if not settings.DEBUG_SURVEY:
        chosen_indices = random.sample( range( len(randomized_questions) ), 6)
    else:
        #In debug mode, we show all surveys
        chosen_indices = range( len(randomized_questions) )
                
    chosen_questions = [ randomized_questions[i] for i in sorted(chosen_indices)]
    
    survey_list = common_questions + chosen_questions
    return survey_list
    
    

exit_survey_questions = {
    'common_questions' : [
        {'type' : 'checkbox',
        'question_name' : 'future_classes',
        'label' : 'Please inform me of future classes offered by edX.'},
        
        {'type' : 'checkbox',
        'question_name' : 'future_offerings',
        'label' : 'Please inform me of opportunities to help with future offerings of this course, such as staffing discussiong forums or developing content.'},
        
        {'type' : 'checkbox',
        'question_name' : 'future_updates',
        'label' : 'Please subscribe me to periodic updates about additional topics, refreshers, and follow-ups for topics in this course.'},
        
        {'type' : 'medium_field',
        'question_name' : 'favorite_parts',
        'label' : 'What were your favorite parts of this course? We would love to hear your comments on the course or the platform.'},
        
        {'type' : 'radio',
        'question_name' : 'rating',
        'label' : 'How would you rate this course?',
        'choices' : [
            '1 - I hated it. I didn\'t learn anything.',
            '2',
            '3',
            '4 - It was pretty good, but could use some improvement.',
            '5',
            '6',
            '7 - Absolutely amazing. I learned a great deal.',
        ]},
    ],
    'random_questions' : [
        # New, needs review
        {'type' : 'radio',
        'question_name' : 'university_comparison',
        'label' : 'How would you compare this course to an equivalent university course, if you have taken one?',
        'choices' : [
            'This course was <strong>much worse</strong> than the university class.',
            'This course was <strong>on the same level</strong> as the university class.',
            'This course was <strong>much better</strong> than the university class.',
            'I have not taken an equivalent university class.',
        ]},
        
        
        {'type' : 'select_many',
        'question_name' : 'smartphone_usage',
        'label' : 'Are you interested in taking edX courses from a mobile device, such as a smartphone? (Chech all that apply.)',
        'choices' : [
            'I would like to use a mobile device my <strong>primary</strong> way of taking edX courses.',
            'I would like to use a mobile device to <strong>sometimes</strong> access edX courses.',
            'I would <strong>not</strong> like to use a mobile device with edX courses.',
            'I use an Android device.',
            'I use an iPhone or iPod Touch.',
            'I use an iPad.',
            'I use a different internet-capable mobile device.',
            'I do not use an internet-capable mobile device.',
        ]},
        
        {'type' : 'medium_field',
        'question_name' : 'improvement_ideas',
        'label' : 'Do you have any ideas on how to improve this course or the edX platform?'},
        
        
        # Level of bandwidth
        # Speed of computer/RAM/etc. 
        # Size of monitor
        # Own a tablet? 
        
        
        {'type' : 'radio',
        'question_name' : 'teach_ee',
        'label' : 'Do you teach electrical engineering (EE)?',
        'choices' : [
            'I teach EE in college/university.',
            'I teach EE in high school/secondary school.',
            'I teach EE elsewhere.',
            'I do not teach EE.',
        ]},
        
        {'type' : 'radio',
        'question_name' : 'highest_degree',
        'label' : 'What is the highest degree you have completed?',
        'choices' : [
            'PhD in a science or engineering field.',
            'PhD in another field.',
            'Master\'s or professional degree.',
            'Bachelor\'s degree.',
            'Secondary/high school.',
            'Junior secondary/high school.',
            'Elementary/primary school.',
        ]},
        
        {'type' : 'short_field',
        'question_name' : 'age',
        'label' : 'What is your age?',
        },
        
        {'type' : 'radio',
                'question_name' : 'gender',
                'label' : 'What is your gender?',
                'choices' : [
                    'Female',
                    'Male',
                    'Other',
        ]},
        
        {'type' : 'radio',
        'question_name' : 'ee_level',
        'label' : 'How much electrical engineering have you studied? ',
        'choices' : [
            'More than one year of EE in college/university',
            'One year or less of EE in college/university',
            'More than one year of EE in high school/secondary school',
            'One year or less of EE in high school/secondary school',
            'Self-taught in EE',
            'None of the above',
        ]},
        
        {'type' : 'radio',
        'question_name' : 'math_level',
        'label' : 'What was your calculus background prior to this course?',
        'choices' : [
            'Vector calculus or differential equations',
            'Single variable calculus',
            'No calculus',
        ]},
        
        {'type' : 'select_many',
        'question_name' : 'why_course',
        'label' : 'Why are you taking this course? (Check all that apply.)',
        'choices' : [
            'Interest in topic',
            'Preparation for advanced standing exam',
            'Review of EE concepts',
            'Employment/job advancement opportunities',
            'Other',
        ]},
        
        {'type' : 'short_field',
        'question_name' : 'weekly_hours',
        'label' : 'How many hours per week on average did you work on this course?',
        },
        
        {'type' : 'radio',
        'question_name' : 'internet_access',
        'label' : 'Where do you access the MITx website most frequently?',
        'choices' : [
            'At home',
            'At the home of a friend or family member outside your home',
            'At school',
            'Internet cafe or other public space',
            'Other',
        ]},
        

        {'type' : 'radio',
        'question_name' : 'work_offline',
        'label' : 'Have you worked <b>offline</b> with anyone on the MITx material?',
        'choices' : [
            'I worked with another person who is also completing the course.',
            'I worked with someone who teaches or has expertise in this area.',
            'I worked completely on my own.',
            'Other',
        ]},
        
        {'type' : 'radio',
        'question_name' : 'online_course_count',
        'label' : 'Including 6.002x, how many online courses have you taken?',
        'choices' : [
            '1',
            '2',
            '3',
            '4',
            '5 or more',
        ]},
        
        {'type' : 'short_field',
        'question_name' : 'race',
        'label' : 'With what race/ethnic group do you most strongly identify?',
        },
        
        {'type' : 'radio',
        'question_name' : 'book_count',
        'label' : 'How many books are there in your home? <br/><em>(There are usually about 40 books per meter of shelving. Do not include magazines, newspapers, or schoolbooks in your estimate.)</em>',
        'choices' : [
            '0-10 books',
            '11-25 books',
            '26-100 books',
            '101-200 books',
            '201-500 books',
            'More than 500 books',
        ]},
        
        {'type' : 'radio',
        'question_name' : 'computer_in_home',
        'label' : 'Did you have a computer in your home?',
        'choices' : [
            'Yes',
            'No',
        ]},
        
        {'type' : 'radio',
        'question_name' : 'parents_engineering',
        'label' : 'Do either of your parents have any training or experience in engineering?',
        'choices' : [
            'Yes',
            'No',
            'I don\'t know',
        ]},
        
        #We used to have two of these questions, one for their mom and one for their dad. That might not make sense for some students.
        {'type' : 'radio',
        'question_name' : 'engineering',
        'label' : 'What is the highest level of schooling completed by one of your parents? (Please choose the answer you think fits best.)',
        'choices' : [
            'PhD degree',
            'Post-graduate, professional degree, or master\'s degree',
            'Bachelor\'s degree',
            'Vocational/technical training',
            'High school or secondary school',
            'Primary school',
            'Did not complete primary school',
        ]},
    ]
}
