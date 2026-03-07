import json
import boto3

bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")

def lambda_handler(event, context):

    path = event.get("rawPath", "")
    params = event.get("queryStringParameters") or {}

    # -------- IDEA GENERATION ROUTE --------
    if path.endswith("/generate"):

        user_input = params.get("topic", "content creation")

        text = user_input.lower()
        is_link = "http" in text or "www." in text

        # -------- LINK ANALYSIS PROMPT --------
        if is_link:

            prompt = f"""
You are CREVO, an AI social media strategist.

A creator shared this social media reel/post link:
{user_input}

You cannot access the link directly, but assume it is a social media reel.

Provide the following in a short structured format:

Hook Strength: Low / Medium / High

Engagement Improvements:
- 2 to 3 short suggestions

Better Caption:
Write one improved caption.

Trending Hashtags:
Provide 5 relevant hashtags.

Virality Score:
Score from 0 to 100.

Keep the response short and clear.
"""

        # -------- NORMAL IDEA GENERATION PROMPT --------
        else:

            prompt = f"""
You are CREVO, an AI social media strategist.

User request:
{user_input}

Your task is to generate VIRAL SOCIAL MEDIA CONTENT IDEAS.

IMPORTANT RULES:
- Do NOT respond like a chatbot
- Do NOT say sentences like "Here are ideas"
- Do NOT give advice
- Only generate content ideas

Each line must be a SOCIAL MEDIA POST IDEA.

GOOD EXAMPLES:
30 Second Fat Burn Morning Workout Reel
Gym Myth vs Reality: 3 Beginner Mistakes
1 Week Fitness Transformation Challenge
Morning Routine for Productivity Reel

BAD EXAMPLES:
Use a fun tone
Post consistently
Be authentic
Please provide suggestions

RULES:
- Maximum 5 ideas
- One idea per line
- Short catchy titles
- Suitable for Instagram Reels, TikTok or YouTube Shorts
"""

        try:

            body = {
                "prompt": prompt,
                "max_gen_len": 200,
                "temperature": 0.9,
                "top_p": 0.9
            }

            response = bedrock.invoke_model(
                modelId="meta.llama3-8b-instruct-v1:0",
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )

            result = json.loads(response["body"].read())
            text = result.get("generation", "")

            lines = text.split("\n")

            ideas = []
            seen_titles = set()

            for line in lines:

                clean = line.strip()
                clean = clean.replace("1.", "").replace("2.", "").replace("3.", "")
                clean = clean.replace("4.", "").replace("5.", "")
                clean = clean.replace("-", "")
                clean = clean.replace("</p>", "")
                clean = clean.replace('"', "")
                clean = clean.strip()

                if (
                    len(clean) < 10
                    or "idea" in clean.lower()
                    or "here are" in clean.lower()
                    or "tips" in clean.lower()
                    or "tone" in clean.lower()
                    or "example" in clean.lower()
                    or "output" in clean.lower()
                    or "suggestion" in clean.lower()
                    or "please" in clean.lower()
                ):
                    continue

                key = clean.lower()

                if key not in seen_titles and len(ideas) < 3:

                    seen_titles.add(key)

                    caption = f"{clean} 🚀\nWhat do you think about this? Drop your thoughts below!"

                    hashtags = [
                        "#viral",
                        "#contentcreator",
                        "#trending"
                    ]

                    ideas.append({
                        "title": clean,
                        "caption": caption,
                        "hashtags": hashtags
                    })

            if len(ideas) == 0:
                ideas = [
                    {
                        "title": f"Creative content idea about {user_input}",
                        "caption": f"Create engaging content about {user_input}",
                        "hashtags": ["#creator", "#viral", "#growth"]
                    }
                ]

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "request": user_input,
                    "ideas": ideas
                })
            }

        except Exception as e:

            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": str(e)
                })
            }

    # -------- CALENDAR ROUTE --------
    elif path.endswith("/calendar"):

        topic = params.get("topic", "content creation")

        prompt = f"""
You are CREVO, an AI social media strategist.

Create a 7-day social media posting calendar for the topic: {topic}.

STRICT RULES:
- Only output the calendar
- No explanations
- No hashtags
- No paragraphs
- No bullet points
- One idea per line

Format EXACTLY like this:

Monday – idea
Tuesday – idea
Wednesday – idea
Thursday – idea
Friday – idea
Saturday – idea
Sunday – idea
"""

        try:

            body = {
                "prompt": prompt,
                "max_gen_len": 200,
                "temperature": 0.8,
                "top_p": 0.9
            }

            response = bedrock.invoke_model(
                modelId="meta.llama3-8b-instruct-v1:0",
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json"
            )

            result = json.loads(response["body"].read())
            text = result.get("generation", "")

            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "topic": topic,
                    "calendar": text
                })
            }

        except Exception as e:

            return {
                "statusCode": 500,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({
                    "error": str(e)
                })
            }

    # -------- DEFAULT ROUTE --------
    else:

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Crevo backend running"
            })
        }