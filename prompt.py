answer_space_formats = f"""
FORMAT FOR SINGLE LINE ANSWERS:
answer_space: {{ 
    "type":"single-line",
}}

FORMAT FOR MULTI LINE ANSWERS:
answer_space: {{ 
    "type":"multi-line",
    "details": {{
      "lines": 2,  
    }}
}}

FORMAT FOR MULTIPLE CHOICE ANSWERS:
answer_space: {{ 
    "type":"multiple-choice",
    "details": {{
      "options": ["choice 1", "choice 2", "choice 3"], 
      "answer-format": "single-tick" 
    }}
}}"""

def build_prompt():
  prompt = f"""
    Extract questions from this document and put them in a JSON object in this format:
    VERY IMPORTANT, PLEASE EXTRACT CAREFULLY HERE. CHECK IF THERE ARE ANY OF THESE:
    1. Strict Numbering Format: IMPORTANT!!! CHECK THESE PATTENRS
        - Main Questions: "1", "2", "3" (Number)
        - Questions: "(a)", "(b)", "(c)" (Alphabet)
        - Sub-Questions: "(i)", "(ii)", "(iii)" (Numeral)
    2. A diagram is usually an image with labels and arrows. Do not extract the diagram as a paragraph.
    3. If main question paragraph is separated by a diagram, add the next main question paragraph as a new item in main_question_text array.
    4. Any scientific equation (whether single or multiple at once) is added as ONE new item in array (main_question_text/question_text/sub_question_text).
    5. Make sure to only separate the main question/question/sub-question only when there is a Number/Alphabet/Numeral.
    6. Make sure that every main question has a question number. Every question has a question alphabet. Every sub-question has a sub-question numeral. If not, then it is not a new question, merge with the previous question.
    7. Sometimes, the main question/question/sub-question has "Based on Diagram..." (description) or "Tick for the correct answer" (instruction to students), please include that as well according to where it is positioned (main question/question/sub-question) as a new item in the respective array.
    8. If question/sub-question is separated by a answer space (......), add the next question/sub-question as a new item in question_text/sub_question_text array.
    9. DO NOT SKIP any ENGLISH paragraph. If any question is separated by page break, then it is still the same question unless there is a new quesion number/alphabet/numeral.
    10. SKIP MALAY SENTENCES

    EXAMPLE INPUT (PDF Content):
    3. Diagram 3 shows the planet Venus orbiting around the Sun. The  area  sweeps  out  by  AOB  and  COD  is  equal  in  the  same  time  interval.
    [ r1 = 1.08 x 1011 m and mass of the Sun, M = 1.989 x 1030 kg]

      [[DIAGRAM 3 IMAGE]]
      Diagram 3

      (a) State physics law involved. [1 mark]
      (b) (i) Determine the value of the linear speed of the Venus at point X [2 marks]
      (ii) State the change in linear speed of the Venus when moving from point C to D. [1 mark]
      (c) Explain your answer in 3(b)(ii). [2 mark]

      
    7. Diagram 7.1 shows a glass block with refractive index of 1.47 placed in oil reservoir.

      [[DIAGRAM 7.1 IMAGE]]
      Diagram 7.1

      Diagram 7.2 shows a ray diagram of light travel from oil to the glass block from top view.

      [[DIAGRAM 7.2 IMAGE]]
      Diagram 7.2

      (a) What is meant by refractive index? [1 mark]
      (b) Complete the beam of light when entering the glass block and label the angle of refraction, r. [1 mark]
      (c) Calculate the value of the angle of refraction, when the index of refraction of the glass block is 1.47 [2 mark]

      (d) Diagram 7.3 shows the arrangement of the apparatus used to create the magic trick of making the glass rod appear to disappear when placed behind the beaker.

      [[DIAGRAM 7.3 IMAGE]]
      Diagram 7.3

      Table 7 shows the different characteristics of the arrangement of apparatus used to produce the trick.

      [[TABLE 7]]
      Table 7

      Based on Table 7, state the appropriate characteristics to make the glass rod disappear from view
      (i) Type of rod
      ............................................................ (answer_space)
      Reason
      ............................................................ (answer_space) [2 marks]

      (ii) Refractive index of the oil
      ............................................................ (answer_space)
      Reason
      ............................................................ (answer_space) [2 marks]

      (e) Based on your answers in 7(d)(i) and 7(d)(ii), choose the most appropriate model to create a perfect magic trick [1 mark]


    9. Diagram 9.1 shows some of the components of the cooling system of a refrigerator using cooling agent with high specific latent heat.
    Arrows indicate the flow of cooling agent from the compressor to the condenser coil and back to the compressor.

      [[DIAGRAM 9.1 IMAGE]]
      Diagram 9.1

      (a) What is meant by specific latent heat? [1 mark]
      (b) Based on Diagram 9.1 and appropriate physics concepts, explain how the cooling system in a refrigerator works. [3 marks]
      (c) Diagram 9.2 shows an electric steamer without a lid. 

      [[DIAGRAM 9.2 IMAGE]]
      Diagram 9.2

      You are required to study the characteristics of an electric steamer as shown in Table 9.

      [[TABLE 9]]
      Table 9

      Explain the suitability of each characteristic of an electric steamer. Determine the most effective electric steamer to use to cook large quantities of food more quickly, efficiently, and safely. [10 marks]
      (d) A chicken is cooked in an electric steamer. 0.8 kg of water at a temperature of 30 oC turns into steam.
      [Specific heat capacity of water, c = 4.20 × 103 J kg−1 oC−1]
      [Specific latent heat of vaporization of water, lv = 2.26 × 106 J kg−1]
      (i) Calculate the heat energy absorbed to raise the temperature of the water from 30 oC to 100 oC. [3 marks]
      (ii) Calculate the amount of energy absorbed to change the water into steam. [2 marks]
    "


    EXAMPLE OUTPUT:
    {{
      "result": [
        {{                
          "main_question_number": "3", 
          "main_question_text": ["Diagram 3 shows the planet Venus orbiting around the Sun. The  area  sweeps  out  by  AOB  and  COD  is  equal  in  the  same  time  interval.",
          "[ r1 = 1.08 x 1011 m and mass of the Sun, M = 1.989 x 1030 kg]"],
          "questions": [
            {{
              "question_alphabet": "(a)",
              "question_text": ["State physics law involved."],
              "sub_questions": [],
              "marks": 1
            }},
            {{
              "question_alphabet": "(b)",
              "question_text": [""],
              "sub_questions": [
                {{
                  "sub_question_numeral": "(i)",
                  "sub_question_text": ["Determine the value of the linear speed of the Venus at point X"],
                  "marks": 2,
                }},
                {{
                  "sub_question_numeral": "(ii)",
                  "sub_question_text": ["State the change in linear speed of the Venus when moving from point C to D."],
                  "marks": 1,
                }}
              ]
            }},
            {{
              "question_alphabet": "c",
              "question_text": ["Explain your answer in 3(b)(ii)."],
              "sub_questions": [],
              "marks": 2,
            }}
          ] 
        }},
        {{                
          "main_question_number": "7", 
          "main_question_header": [
            "Diagram 7.1 shows a glass block with refractive index of 1.47 placed in oil reservoir.",
            "Diagram 7.2 shows a ray diagram of light travel from oil to the glass block from top view."
          ],
          "questions": [
            {{
              "question_alphabet": "(a)",
              "question_text": ["What is meant by refractive index?"],
              "sub_questions": [],
              "marks": 1,
            }},
            {{
              "question_alphabet": "(b)",
              "question_text": ["Complete the beam of light when entering the glass block and label the angle of refraction, r."],
              "sub_questions": [],
              "marks": 1
            }},
            {{
              "question_alphabet": "(c)",
              "question_text": [
                  "Calculate the value of the angle of refraction, when the index of refraction of the glass block is 1.47",
              ]
              "sub_questions": [],
              "marks": 2
            }},
            {{
              "question_alphabet": "(d)",
              "question_text": [
                "Diagram 7.3 shows the arrangement of the apparatus used to create the magic trick of making the glass rod appear to disappear when placed behind the beaker.",
                "Table 7 shows the different characteristics of the arrangement of apparatus used to produce the trick.",
                "Based on Table 7, state the appropriate characteristics to make the glass rod disappear from view"
              ],
              "sub_questions": [
                {{
                  "sub_question_numeral": "(i)",
                  "sub_question_text": [
                    "Type of rod",
                    "Reason"
                  ],
                  "marks": 2
                }},
                {{
                  "sub_question_numeral": "(ii)",
                  "sub_question_text": [
                    "Refractive index of the oil",
                    "Reason"
                  ],
                  "marks": 2
                }}
              ]
            }},
            {{
              "question_alphabet": "(e)",
              "question_text": [
                "Based on your answers in 7(d)(i) and 7(d)(ii), choose the most appropriate model to create a perfect magic trick"
              ],
              "marks": 1
            }}
          ]
        }},
        {{                
          "main_question_number": "9", 
          "main_question_header": ["Diagram 9.1 shows some of the components of the cooling system of a refrigerator using cooling agent with high specific latent heat. 
          Arrows indicate the flow of cooling agent from the compressor to the condenser coil and back to the compressor."],
          "questions": [
            {{
              "question_alphabet": "(a)",
              "question_text": ["What is meant by specific latent heat?"],
              "sub_questions": [],
              "marks": 1,
            }},
            {{
              "question_alphabet": "(b)",
              "question_text": ["Based on Diagram 9.1 and appropriate physics concepts, explain how the cooling system in a refrigerator works."],
              "sub_questions": [],
              "marks": 3
            }},
            {{
              "question_alphabet": "(c)",
              "question_text": ["Diagram 9.2 shows an electric steamer without a lid.",
              "You are required to study the characteristics of an electric steamer as shown in Table 9.",
              "Explain the suitability of each characteristic of an electric steamer. Determine the most effective electric steamer to use to cook large quantities of food more quickly, efficiently, and safely."],
              "sub_questions": [],
              "marks": 10
            }},
            {{
              "question_alphabet": "(d)",
              "question_text": ["A chicken is cooked in an electric steamer. 0.8 kg of water at a temperature of 30 oC turns into steam.",
              "[Specific heat capacity of water, c = 4.20 × 103 J kg−1 oC−1]",
              "[Specific latent heat of vaporization of water, lv = 2.26 × 106 J kg−1]"],
              "sub_questions": [
                {{
                  "sub_question_numeral": "(i)",
                  "sub_question_text": ["Calculate the heat energy absorbed to raise the temperature of the water from 30 oC to 100 oC."],
                  "marks": 3
                }},
                {{
                  "sub_question_numeral": "(ii)",
                  "sub_question_text": ["Calculate the amount of energy absorbed to change the water into steam."],
                  "marks": 2
                }}
              ]
            }}
          ]
        }}
      ]
    }}
    CONTENT CONSTRAINTS:
    - English only (Do not include malay)
    - Ignore tables
    - Ignore bilingual elements
    - Preserve complete question semantics
  """
  return prompt
