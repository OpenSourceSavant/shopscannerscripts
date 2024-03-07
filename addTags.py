import google.generativeai as genai
import socket
import json
import re
import random
API_KEYS = ['AIzaSyBBy0N7bia-ejb2svG6PiQt5YVEM16f0S4','AIzaSyCVQNjb3HPa_3Pg6qX4Z39eHmP_-vuGuVU','AIzaSyCqB1To9nkLc3xT0FRLW7QJVrr-HlKLZaQ']
selected_api_key = random.choice(API_KEYS)
genai.configure(api_key=selected_api_key)
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)


# Set up the model
generation_config = {
  "temperature": 0.9,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 2048,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

model = genai.GenerativeModel(model_name="gemini-pro",
                              generation_config=generation_config,
                              safety_settings=safety_settings)


def getTags(productTitle):
    prompt_parts = [
        f"""
          Title: "Product Tagging Assistance for Best Price Drop Deals on Amazon and Flipkart"

          We send best pricedrop deals from amazon and flipkart to our users via our app. whenever any deal comes we have to categorize the deal and add tags to the deal so that we can map the deal with correct tags . for example Electronics, Men's Fashion, Women's Fashion, Men's Footwear, Women's Footwear, Home Improvement, MakeUp etc. Some tag can contain multiple category deals for example beauty can contain deal from makeup, skincare, haircare etc so you have to correctly tag the deals from the list of tags below.
          tags -


          You are curating a list of deals across various product categories. Your task is to add relevant tags to each product based on its category. Use the provided tag list, and ensure that gender (male, female, or unisex) is incorporated into the tags field.

          Available Categories and Tags (comma-separated):

          electronics & gadgets, mobiles, phone, phones, smartphone, laptops, cameras, earphones, headphones, televisions, tv, air conditioners, ac, electronics others
          men's fashion, shirts & t-shirts, menshirt, mentshirt, t-shirt, men track pants, jeans & trousers,men trousers, men joggers, men jeans, men's jeans, ethnic wear, menethnicwear, winter wear, menwinterwear, watches, menwatch, smartwatch, accessories, menaccessories, backpack, bags
          women's fashion, shirts & t-shirts, womenshirt, womentshirt, womenshirts, women track pants, women trousers,women joggers, women jeans, jeans & trousers, womenjeans, womentrouser,women ethnic wear, womenethnicwear, sarees, saree,lehenga, winter wear, womenwinterwear, watches, womenwatch, smartwatch, accessories, womenaccessories, backpack, bags
          beauty & personal care, facewash, sunscreen, face serum, faceserum, serum, moisturizer, moituriser, hair care, hairwash, shampoo, hairserum, makeup, perfumes, perfume, fragrance, deo
          footwear, casual shoes, casualshoes, sports shoes, sportsshoes, formal shoes, formalshoes, flip flops, flipflops, heels, heels
          home improvement, kitchen ware, kitchenware, home decor, homedecor, furnishing, appliances, ac, tv, television, refrigerator, fridge, bathroom accessories,taps, bathroom, outdoor and garden, outdoor, garden, diy tools, diytools, air freshner
          health & wellness, oral care,toothbrush, oralcare, sexual wellness, sexualwellness, condoms

          When providing tags, make sure to follow these guidelines:

          Use lower case English for all tags.
          Include the gender (male, female, or unisex) in the tags field.
          Avoid adding anything outside the predefined tag list.
          Remember brand associations, e.g., vivo is a mobile brand, and Castrol is an automotive brand.
          Provide your response with the relevant tags for each product category along with the brand identification, formatted in JSON.
          Toys should not be tagged as electronics
          Gummies should not get tags like fecewash, faceserum etc.
          condoms should not be tagged as beauty, skincare, oral care or any other tags

          Example 1 
          Bajaj Almond Drops Moisturizing Soap 5 X 125g - this deal title in provided
          Your Reply 
          "Brand":"Bajaj",
          "Tags":["beauty","skincare"]

          Example 2 
          
          "Tags":["condom"] (ONLY 1 TAG in CASE of CONDOM)





          

\n\n{productTitle}""",
    ]

    response = model.generate_content(prompt_parts)

    # Check if the response is empty
    if not response.text.strip():
        print("Empty response received.")
        return

    # Debugging: Print the response text
    #print("Response Text:", response.text)

    # Use a regular expression to extract JSON from the response
    # This will handle cases with and without backticks
    match = re.search(r'```json\n?({.*?})\n?```|({.*})', response.text, flags=re.DOTALL)
    if match:
        corrected_response = match.group(1) or match.group(2)
    else:
        print("No JSON data found in the response.")
        return

    # Debugging: Print the corrected response
    print("Corrected Response:", corrected_response)
    #print('hello in am below corrected response in affTags.py')
    try:
        
        json_object = json.loads(corrected_response)
    except json.JSONDecodeError as e:
        print("JSON Decode Error:", e)

    return json_object
