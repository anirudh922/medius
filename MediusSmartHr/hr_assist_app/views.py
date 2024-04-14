from django.http import HttpResponse
from django.shortcuts import render
from openai import OpenAI
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)
SECRET_KEY = os.getenv('SECRET_KEY')
print(SECRET_KEY)

openai = OpenAI(api_key=SECRET_KEY)

def evaluate_candidate_responses(request):
    try:
        if request.method == 'POST':
            name = request.POST['name']
            experience = request.POST['experience']
            answer1 = request.POST['answer1']
            answer2 = request.POST['answer2']
            answer3 = request.POST['answer3']
            answer4 = request.POST['answer4']
            answer5 = request.POST['answer5']
            questions = ["Can you describe your experience with diary management and scheduling appointments?",
                        "How do you handle confidential information and sensitive situations?",
                        "Can you provide an example of a complex problem you've solved in a similar role?",
                        "How do you prioritize tasks and manage your time when dealing with a busy executive's schedule?",
                        "How comfortable are you with liaising with high-level stakeholders and managing professional relationships?"
                        ]
            # Gather candidate responses from the user
            answers = answer1+','+answer2+','+answer3+','+answer4+','+answer5
            answerlist = answers.split(',')
            results = []
            print(answerlist)
            print(questions)
            for i in range(len(questions)):
                question = questions[i]
                print(question[i])
                print(answerlist[i])
                responses = answerlist[i]
                response_text = [
                {
                "role": "system",
                "content": "you are an automated code which only returns these specific words: QUALIFIED, SOMEWHAT QUALIFIED, NOT QUALIFIED based on the question  - "+question+" evaluate candidate response - "+responses+" who is having - "+experience+" years of experience"
                },
                {
                "role": "user",
                "content": responses
                }
                ]
                completion = openai.chat.completions.create(
                    model="gpt-3.5-turbo",  # GPT-3.5 Turbo model
                    messages=response_text,
                    max_tokens=20,
                    temperature=0,
                    top_p=1.0,
                    frequency_penalty=0.0,
                    presence_penalty=0.0,
                    stop=["\n"]
                )
                print('OPENAI DATA For Developers',completion)
                choices = completion.choices[0].message.content
                if choices in ['QUALIFIED','NOT QUALIFIED','SOMEWHAT QUALIFIED']:
                    results.append(choices)
                else:
                    result = 'Please Check Input/output response !'
                    print('ERROR RESPONSE MESSAGE',completion)
                    data = {'name': name, 'result': result}
                    return render(request, 'index.html',{'data':data})
            qualified_count  = results.count('QUALIFIED')
            not_qualified_count = results.count('NOT QUALIFIED')
            somewhat_qualified_count = results.count('SOMEWHAT QUALIFIED')
            if qualified_count > somewhat_qualified_count and qualified_count > not_qualified_count:
                result = 'QUALIFIED'
            elif somewhat_qualified_count > qualified_count and somewhat_qualified_count > not_qualified_count:
                result = 'SOMEWHAT QUALIFIED'
            else:
                result = 'NOT QUALIFIED'
            print('OPENAI DATA For Developers',completion)
            data = {'name': name, 'result': result}
            return render(request,'index.html',{'data':data})
        else:
            return render(request, 'index.html')
    except Exception as e:
        print(e)
        return HttpResponse('Error Occured please check log detail',e)
    