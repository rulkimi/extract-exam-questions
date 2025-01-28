import os
import base64
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

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

def prompt():
  return f"""""Extract questions from this document and put them in a JSON object in this format:
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
        9. DO NOT SKIP any paragraph. If any question is separated by page break, then it is still the same question unless there is a new quesion number/alphabet/numeral.
        10. Separate main_question_text/question_text/sub_question_text by language (english/malay).

        EXAMPLE INPUT (PDF Content):
        "3. Rajah 3 menunjukkan planet Zuhrah yang mengorbit mengelilingi Matahari. Luas yang dicakupi oleh AOB dan COD adalah sama dalam selang masa yang sama.
            [ r1 = 1.08 x 1011 m dan jisim Matahari, M = 1.989 x 1030 kg]
            Diagram 3 shows the planet Venus orbiting around the Sun. The  area  sweeps  out  by  AOB  and  COD  is  equal  in  the  same  time  interval.
            [ r1 = 1.08 x 1011 m and mass of the Sun, M = 1.989 x 1030 kg]

          [[DIAGRAM 3 IMAGE]]
          Rajah 3
          Diagram 3

          (a) Nyatakan hukum fizik yang terlibat.
              State physics law involved. [1 mark]
          (b) (i) Tentukan nilai laju linear planet Zuhrah di titik X.
                  Determine the value of the linear speed of the Venus at point X [2 marks]
          (ii) Nyatakan perubahan laju linear Zuhrah apabila bergerak dari titik C ke D.
              State the change in linear speed of the Venus when moving from point C to D. [1 mark]
          (c) Jelaskan jawapan anda dalam 3(b)(ii).
              Explain your answer in 3(b)(ii). [2 mark]
          

          
          7. Rajah 7.1 menunjukkan satu bongkah kaca dengan indek biasan 1.47 berada dalam takungan minyak.
            Diagram 7.1 shows a glass block with refractive index of 1.47 placed in oil reservoir.

          [[DIAGRAM 7.1 IMAGE]]
          Rajah 7.1
          Diagram 7.1

          Rajah 7.2 menunjukkan gambarajah sinar bagi alur cahaya yang merambat dari minyak ke bongkah kaca dari pandangan atas.
          Diagram 7.2 shows a ray diagram of light travel from oil to the glass block from top view.

          [[DIAGRAM 7.2 IMAGE]]
          Rajah 7.2
          Diagram 7.2

          (a) Apakah yang dimaksudkan dengan indeks biasan?
              What is meant by refractive index? [1 mark]
          (b) Lengkapkan alur sinar cahaya apabila memasuki blok kaca tersebut dan labelkan sudut biasan, r.
              Complete the beam of light when entering the glass block and label the angle of refraction, r. [1 mark]
          (c) Hitung nilai sudut biasan, apabila indeks biasan blok kaca ialah 1.47
              Calculate the value of the angle of refraction, when the index of refraction of the glass block is 1.47 [2 mark]
          (d) Rajah 7.3 menunjukkan susunan radas yang digunakan untuk membuat helah silap mata agar rod kaca kelihatan hilang apabila diletakkan di belakang bikar.
              Diagram 7.3 shows the arrangement of the apparatus used to create the magic trick of making the glass rod appear to disappear when placed behind the beaker.

          [[DIAGRAM 7.3 IMAGE]]
          Rajah 7.3
          Diagram 7.3

          Jadual 7 menunjukkan ciri-ciri yang berbeza bagi susunan radas yang digunakan untuk menghasilkan silap mata tersebut.
          Table 7 shows the different characteristics of the arrangement of apparatus used to produce the trick.

          [[TABLE 7]]
          Table 7

          Berdasarkan Jadual 7, nyatakan ciri-ciri yang sesuai untuk membuatkan rod kaca hilang dari pandangan.
          Based on Table 7, state the appropriate characteristics to make the glass rod disappear from view
          (i) Jenis rod
              Type of rod
          ............................................................ (answer_space)
          Sebab/Reason
          ............................................................ (answer_space) [2 marks]

          (ii) Indek biasan minyak
              Refractive index of the oil
          ............................................................ (answer_space)
          Sebab/Reason
          ............................................................ (answer_space) [2 marks]

          (e) Berdasarkan jawapan anda dalam 7(d)(i) dan 7(d)(ii), pilih model yang paling sesuai untuk mencipta satu helah silap mata yang sempurna.
              Based on your answers in 7(d)(i) and 7(d)(ii), choose the most appropriate model to create a perfect magic trick [1 mark]


          9. Rajah 9.1 menunjukkan sebahagian daripada komponen sistem penyejukan sebuah peti sejuk yang menggunakan agen penyejuk yang mempunyai haba pendam tentu yang tinggi. Anak panah menunjukkan aliran agen penyejuk dari pemampat ke gegelung kondenser dan kembali ke pemampat.
            Diagram 9.1 shows some of the components of the cooling system of a refrigerator using cooling agent with high specific latent heat. Arrows indicate the flow of cooling agent from the compressor to the condenser coil and back to the compressor.

          [[DIAGRAM 9.1 IMAGE]]
          Diagram 9.1

          (a) Apakah yang dimaksudkan dengan haba pendam tentu?
              What is meant by specific latent heat? [1 mark]
          (b) Berdasarkan Rajah 9.1 dan konsep fizik yang sesuai, terangkan bagaimana sistem penyejukan dalam peti sejuk berfungsi.
              Based on Diagram 9.1 and appropriate physics concepts, explain how the cooling system in a refrigerator works. [3 marks]
          (c) Rajah 9.2 menunjukkan sebuah pengukus elektrik tanpa penutup.
              Diagram 9.2 shows an electric steamer without a lid. 

          [[DIAGRAM 9.2 IMAGE]]
          Rajah 9.2
          Diagram 9.2

          Anda dikehendaki mengkaji ciri-ciri sebuah pengukus elektrik seperti yang ditunjukkan dalam Jadual 9.
          You are required to study the characteristics of an electric steamer as shown in Table 9.

          [[TABLE 9]]
          Jadual 9
          Table 9

          Terangkan kesesuaian setiap ciri pengukus elektrik. Tentukan pengukus elektrik paling berkesan untuk digunakan bagi memasak makanan yang banyak dengan lebih cepat, cekap, dan selamat.
          Explain the suitability of each characteristic of an electric steamer. Determine the most effective electric steamer to use to cook large quantities of food more quickly, efficiently, and safely. [10 marks]
          (d) Seekor ayam dimasak di dalam sebuah pengukus elektrik. Sebanyak 0.8 kg air pada suhu 30 oC bertukar menjadi wap.
              [Muatan haba tentu air, c = 4.20 × 103 J kg−1 oC−1]
              [Haba pendam tentu pengewapan air, lv = 2.26 × 106 J kg−1]
              A chicken is cooked in an electric steamer. 0.8 kg of water at a temperature of 30 oC turns into steam.
              [Specific heat capacity of water, c = 4.20 × 103 J kg−1 oC−1]
              [Specific latent heat of vaporization of water, lv = 2.26 × 106 J kg−1]
          (i) Hitung tenaga haba yang diserap untuk meningkatkan suhu air tersebut daripada 30 oC ke 100 oC.
              Calculate the heat energy absorbed to raise the temperature of the water from 30 oC to 100 oC. [3 marks]
          (ii) Hitung jumlah tenaga yang diserap untuk mengubah air tersebut menjadi wap.
              Calculate the amount of energy absorbed to change the water into steam. [2 marks]
          "


        EXAMPLE OUTPUT (JSON Object):
        {{
            "result": [
              {{                
                "main_question_number": "3", 
                "main_question_text": {{
                  "english":["Diagram 3 shows the planet Venus orbiting around the Sun. The  area  sweeps  out  by  AOB  and  COD  is  equal  in  the  same  time  interval.",
                  "[ r1 = 1.08 x 1011 m and mass of the Sun, M = 1.989 x 1030 kg]"],
                  "malay": ["Rajah 3 menunjukkan planet Zuhrah yang mengorbit mengelilingi Matahari. Luas yang dicakupi oleh AOB dan COD adalah sama dalam selang masa yang sama.",
                  "[ r1 = 1.08 x 1011 m dan jisim Matahari, M = 1.989 x 1030 kg]"]
                }},
                "questions": [
                    {{
                      "question_alphabet": "(a)",
                      "question_text": {{
                          "english": ["State physics law involved."],
                          "malay": ["Nyatakan hukum fizik yang terlibat."],
                      }},
                      "sub_questions": [],
                      "marks": 1
                    }},
                    {{
                      "question_alphabet": "(b)",
                      "question_text": [""],
                      "sub_questions": [
                          {{
                            "sub_question_numeral": "(i)",
                            "sub_question_text": {{
                              "english":["Determine the value of the linear speed of the Venus at point X"],
                              "malay": ["Tentukan nilai laju linear planet Zuhrah di titik X."]
                            }},
                            "marks": 2,
                          }},
                          {{
                            "sub_question_numeral": "(ii)",
                            "sub_question_text": {{
                              "english":["State the change in linear speed of the Venus when moving from point C to D."],
                              "malay": ["Nyatakan perubahan laju linear Zuhrah apabila bergerak dari titik C ke D."]
                            }}
                            "marks": 1,
                          }}
                        ]
                    }},
                    {{
                      "question_alphabet": "c",
                      "question_text": {{
                        "english":["Explain your answer in 3(b)(ii)."],
                        "malay":["Jelaskan jawapan anda dalam 3(b)(ii)."]
                      }}
                      "sub_questions": [],
                      "marks": 2,
                    }}
                  ]
              }},
              {{                
                "main_question_number": "7", 
                "main_question_header": {{
                  "english":[
                    "Diagram 7.1 shows a glass block with refractive index of 1.47 placed in oil reservoir.",
                    "Diagram 7.2 shows a ray diagram of light travel from oil to the glass block from top view."
                  ],
                  "malay":[
                    "Rajah 7.1 menunjukkan satu bongkah kaca dengan indek biasan 1.47 berada dalam takungan minyak.",
                    "Rajah 7.2 menunjukkan gambarajah sinar bagi alur cahaya yang merambat dari minyak ke bongkah kaca dari pandangan atas."
                  ]
                }},
                "questions": [
                  {{
                    "question_alphabet": "(a)",
                    "question_text": {{
                      "english":["What is meant by refractive index?"],
                      "malay":["Apakah yang dimaksudkan dengan indek biasan?"]
                    }},
                    "sub_questions": [],
                    "marks": 1,
                  }},
                  {{
                    "question_alphabet": "(b)",
                    "question_text": {{
                      "english":["Complete the beam of light when entering the glass block and label the angle of refraction, r."],
                      "malay":["Lengkapkan alur sinar cahaya apabila memasuki blok kaca tersebut dan labelkan sudut biasan, r."]
                    }}
                    "sub_questions": [],
                    "marks": 1
                  }},
                  {{
                    "question_alphabet": "(c)",
                    "question_text": 
                    {{
                      "english":["Calculate the value of the angle of refraction, when the index of refraction of the glass block is 1.47"],
                      "malay":["Hitung nilai sudut biasan, apabila indeks biasan blok kaca ialah 1.47"]
                    }}
                    "sub_questions": [],
                    "marks": 2
                  }},
                  {{
                    "question_alphabet": "(d)",
                    "question_text": {{
                      "english":[
                        "Diagram 7.3 shows the arrangement of the apparatus used to create the magic trick of making the glass rod appear to disappear when placed behind the beaker.",
                        "Table 7 shows the different characteristics of the arrangement of apparatus used to produce the trick.",
                        "Based on Table 7, state the appropriate characteristics to make the glass rod disappear from view"
                      ],
                      "malay":[
                        "Rajah 7.3 menunjukkan susunan radas yang digunakan untuk membuat helah silap mata agar rod kaca kelihatan hilang apabila diletakkan di belakang bikar.",
                        "Jadual 7 menunjukkan ciri-ciri yang berbeza bagi susunan radas yang digunakan untuk menghasilkan silap mata tersebut.",
                        "Berdasarkan Jadual 7, nyatakan ciri-ciri yang sesuai untuk membuatkan rod kaca hilang dari pandangan."
                      ]
                    }}
                    "sub_questions": [
                        {{
                            "sub_question_numeral": "(i)",
                            "sub_question_text": {{
                              "english": [
                                "Type of rod",
                                "Reason"
                              ],
                              "malay": [
                                "Jenis rod",
                                "Sebab"
                              ]
                            }}
                            "marks": 2
                        }},
                        {{
                            "sub_question_numeral": "(ii)",
                            "sub_question_text": {{
                              "english": [
                                "Refractive index of the oil",
                                "Reason"
                              ],
                              "malay": [
                                "Indeks biasan minyak",
                                "Sebab"
                              ]
                            }}
                            "marks": 2
                        }}
                    ]
                  }},
                  {{
                    "question_alphabet": "(e)",
                    "question_text": {{
                      "english":["Based on your answers in 7(d)(i) and 7(d)(ii), choose the most appropriate model to create a perfect magic trick"],
                      "malay":["Berdasarkan jawapan anda dalam 7(d)(i) dan 7(d)(ii), pilih model yang paling sesuai untuk mencipta satu helah silap mata yang sempurna."]
                    }}
                    "marks": 1
                  }}
                ]
              }},
              {{                
                "main_question_number": "9", 
                "main_question_header": {{
                  "english": ["Diagram 9.1 shows some of the components of the cooling system of a refrigerator using cooling agent with high specific latent heat. Arrows indicate the flow of cooling agent from the compressor to the condenser coil and back to the compressor."],
                  "malay": ["Rajah 9.1 menunjukkan sebahagian daripada komponen sistem penyejukan sebuah peti sejuk yang menggunakan agen penyejuk yang mempunyai haba pendam tentu yang tinggi. Anak panah menunjukkan aliran agen penyejuk dari pemampat ke gegelung kondenser dan kembali ke pemampat."]
                }}
                "questions": [
                  {{
                    "question_alphabet": "(a)",
                    "question_text": {{
                      "english": ["What is meant by specific latent heat?"],
                      "malay": ["Apakah yang dimaksudkan dengan haba pendam tentu?"]
                    }}
                    "sub_questions": [],
                    "marks": 1,
                  }},
                  {{
                    "question_alphabet": "(b)",
                    "question_text": {{
                      "english": ["Based on Diagram 9.1 and appropriate physics concepts, explain how the cooling system in a refrigerator works."],
                      "malay": ["Berdasarkan Rajah 9.1 dan konsep fizik yang sesuai, terangkan bagaimana sistem penyejukan dalam peti sejuk berfungsi."]
                    }}
                    "sub_questions": [],
                    "marks": 3
                  }},
                  {{
                    "question_alphabet": "(c)",
                    "question_text": {{
                      "english": [
                        "Diagram 9.2 shows an electric steamer without a lid.",
                        "You are required to study the characteristics of an electric steamer as shown in Table 9.",
                        "Explain the suitability of each characteristic of an electric steamer. Determine the most effective electric steamer to use to cook large quantities of food more quickly, efficiently, and safely."
                      ],
                      "malay": [
                        "Rajah 9.2 menunjukkan sebuah pengukus elektrik tanpa penutup.",
                        "Anda dikehendaki mengkaji ciri-ciri sebuah pengukus elektrik seperti yang ditunjukkan dalam Jadual 9.",
                        "Terangkan kesesuaian setiap ciri pengukus elektrik. Tentukan pengukus elektrik paling berkesan untuk digunakan bagi memasak makanan yang banyak dengan lebih cepat, cekap, dan selamat."
                      ]
                    }}
                    "sub_questions": [],
                    "marks": 10
                  }},
                  {{
                    "question_alphabet": "(d)",
                    "question_text": {{
                      "english": [
                        "A chicken is cooked in an electric steamer. 0.8 kg of water at a temperature of 30 oC turns into steam.",
                        "[Specific heat capacity of water, c = 4.20 × 103 J kg−1 oC−1]",
                        "[Specific latent heat of vaporization of water, lv = 2.26 × 106 J kg−1]"],
                      "malay": [
                        "Seekor ayam dimasak di dalam sebuah pengukus elektrik. Sebanyak 0.8 kg air pada suhu 30 oC bertukar menjadi wap.",
                        "[Muatan haba tentu air, c = 4.20 × 103 J kg−1 oC−1]",
                        "[Haba pendam tentu pengewapan air, lv = 2.26 × 106 J kg−1]"
                      ]
                    }}
                    "sub_questions": [
                        {{
                            "sub_question_numeral": "(i)",
                            "sub_question_text": {{
                              "english": ["Calculate the heat energy absorbed to raise the temperature of the water from 30 oC to 100 oC."],
                              "malay": ["Hitung tenaga haba yang diserap untuk meningkatkan suhu air tersebut daripada 30 oC ke 100 oC."]
                            }}
                            "marks": 3
                        }},
                        {{
                            "sub_question_numeral": "(ii)",
                            "sub_question_text": {{
                              "english": ["Calculate the amount of energy absorbed to change the water into steam."],
                              "malay": ["Hitung jumlah tenaga yang diserap untuk mengubah air tersebut menjadi wap."]
                            }}
                            "marks": 2
                        }}
                    ]
                  }}
                ]
              }}
              // ... other questions
            ]
        }}

        CONTENT CONSTRAINTS:
        - Ignore tables
        - Preserve complete question semantics"""""

def prompt2():
  return f"""""Extract questions from this document and put them in a JSON object in this format:
      VERY IMPORTANT, PLEASE EXTRACT CAREFULLY HERE. CHECK IF THERE ARE ANY OF THESE:

      1. Strict Numbering Format:
        - Main Questions: "1", "2", "3" (Number)
        - Questions: "(a)", "(b)", "(c)" (Alphabet)
        - Sub-Questions: "(i)", "(ii)", "(iii)" (Numeral)

      2. Diagram References:
        - If a question mentions a diagram (e.g., "Based on Diagram X..."), add this as a new item in the respective array (`main_question_text`, `question_text`, or `sub_question_text`).
        - Do NOT skip any mention of diagrams, images, or references, even if repeated.

      3. Instructions to Students:
        - Capture any student instructions, such as "Tick for the correct answer," "State your answer in the box," or "Draw a diagram."
        - These should be added as separate items within `main_question_text`, `question_text`, or `sub_question_text` arrays.

      4. Equations and Tables:
        - Include scientific equations as separate items in the relevant text arrays.
        - For tables or data (e.g., "Table X shows..."), mention "Table Reference" explicitly and include its description in the text.

      5. Page Breaks:
        - If a question continues after a page break, ensure it is captured as part of the same question unless a new number, alphabet, or numeral indicates otherwise.

      6. Language Separation:
        - Store questions in both `malay` and `english` arrays.
        - Do not mix languages in a single string.

      7. Question Structure:
        - Ensure every main question has a number, every question has an alphabet, and every sub-question has a numeral.
        - If no clear separation exists, merge it into the previous question or sub-question.
      
      8. CONTENT CONSTRAINTS:
        - Ignore tables
        - Preserve complete question semantics

      EXAMPLE INPUT (PDF Content):
      "3. Rajah 3 menunjukkan planet Zuhrah yang mengorbit mengelilingi Matahari. Luas yang dicakupi oleh AOB dan COD adalah sama dalam selang masa yang sama.
          [ r1 = 1.08 x 1011 m dan jisim Matahari, M = 1.989 x 1030 kg]
          Diagram 3 shows the planet Venus orbiting around the Sun. The  area  sweeps  out  by  AOB  and  COD  is  equal  in  the  same  time  interval.
          [ r1 = 1.08 x 1011 m and mass of the Sun, M = 1.989 x 1030 kg]

        [[DIAGRAM 3 IMAGE]]
        Rajah 3
        Diagram 3

        (a) Nyatakan hukum fizik yang terlibat.
            State physics law involved. [1 mark]
        (b) (i) Tentukan nilai laju linear planet Zuhrah di titik X.
                Determine the value of the linear speed of the Venus at point X [2 marks]
        (ii) Nyatakan perubahan laju linear Zuhrah apabila bergerak dari titik C ke D.
            State the change in linear speed of the Venus when moving from point C to D. [1 mark]
        (c) Jelaskan jawapan anda dalam 3(b)(ii).
            Explain your answer in 3(b)(ii). [2 mark]
        

        
        7. Rajah 7.1 menunjukkan satu bongkah kaca dengan indek biasan 1.47 berada dalam takungan minyak.
          Diagram 7.1 shows a glass block with refractive index of 1.47 placed in oil reservoir.

        [[DIAGRAM 7.1 IMAGE]]
        Rajah 7.1
        Diagram 7.1

        Rajah 7.2 menunjukkan gambarajah sinar bagi alur cahaya yang merambat dari minyak ke bongkah kaca dari pandangan atas.
        Diagram 7.2 shows a ray diagram of light travel from oil to the glass block from top view.

        [[DIAGRAM 7.2 IMAGE]]
        Rajah 7.2
        Diagram 7.2

        (a) Apakah yang dimaksudkan dengan indeks biasan?
            What is meant by refractive index? [1 mark]
        (b) Lengkapkan alur sinar cahaya apabila memasuki blok kaca tersebut dan labelkan sudut biasan, r.
            Complete the beam of light when entering the glass block and label the angle of refraction, r. [1 mark]
        (c) Hitung nilai sudut biasan, apabila indeks biasan blok kaca ialah 1.47
            Calculate the value of the angle of refraction, when the index of refraction of the glass block is 1.47 [2 mark]
        (d) Rajah 7.3 menunjukkan susunan radas yang digunakan untuk membuat helah silap mata agar rod kaca kelihatan hilang apabila diletakkan di belakang bikar.
            Diagram 7.3 shows the arrangement of the apparatus used to create the magic trick of making the glass rod appear to disappear when placed behind the beaker.

        [[DIAGRAM 7.3 IMAGE]]
        Rajah 7.3
        Diagram 7.3

        Jadual 7 menunjukkan ciri-ciri yang berbeza bagi susunan radas yang digunakan untuk menghasilkan silap mata tersebut.
        Table 7 shows the different characteristics of the arrangement of apparatus used to produce the trick.

        [[TABLE 7]]
        Table 7

        Berdasarkan Jadual 7, nyatakan ciri-ciri yang sesuai untuk membuatkan rod kaca hilang dari pandangan.
        Based on Table 7, state the appropriate characteristics to make the glass rod disappear from view
        (i) Jenis rod
            Type of rod
        ............................................................ (answer_space)
        Sebab/Reason
        ............................................................ (answer_space) [2 marks]

        (ii) Indek biasan minyak
            Refractive index of the oil
        ............................................................ (answer_space)
        Sebab/Reason
        ............................................................ (answer_space) [2 marks]

        (e) Berdasarkan jawapan anda dalam 7(d)(i) dan 7(d)(ii), pilih model yang paling sesuai untuk mencipta satu helah silap mata yang sempurna.
            Based on your answers in 7(d)(i) and 7(d)(ii), choose the most appropriate model to create a perfect magic trick [1 mark]


        9. Rajah 9.1 menunjukkan sebahagian daripada komponen sistem penyejukan sebuah peti sejuk yang menggunakan agen penyejuk yang mempunyai haba pendam tentu yang tinggi. Anak panah menunjukkan aliran agen penyejuk dari pemampat ke gegelung kondenser dan kembali ke pemampat.
          Diagram 9.1 shows some of the components of the cooling system of a refrigerator using cooling agent with high specific latent heat. Arrows indicate the flow of cooling agent from the compressor to the condenser coil and back to the compressor.

        [[DIAGRAM 9.1 IMAGE]]
        Diagram 9.1

        (a) Apakah yang dimaksudkan dengan haba pendam tentu?
            What is meant by specific latent heat? [1 mark]
        (b) Berdasarkan Rajah 9.1 dan konsep fizik yang sesuai, terangkan bagaimana sistem penyejukan dalam peti sejuk berfungsi.
            Based on Diagram 9.1 and appropriate physics concepts, explain how the cooling system in a refrigerator works. [3 marks]
        (c) Rajah 9.2 menunjukkan sebuah pengukus elektrik tanpa penutup.
            Diagram 9.2 shows an electric steamer without a lid. 

        [[DIAGRAM 9.2 IMAGE]]
        Rajah 9.2
        Diagram 9.2

        Anda dikehendaki mengkaji ciri-ciri sebuah pengukus elektrik seperti yang ditunjukkan dalam Jadual 9.
        You are required to study the characteristics of an electric steamer as shown in Table 9.

        [[TABLE 9]]
        Jadual 9
        Table 9

        Terangkan kesesuaian setiap ciri pengukus elektrik. Tentukan pengukus elektrik paling berkesan untuk digunakan bagi memasak makanan yang banyak dengan lebih cepat, cekap, dan selamat.
        Explain the suitability of each characteristic of an electric steamer. Determine the most effective electric steamer to use to cook large quantities of food more quickly, efficiently, and safely. [10 marks]
        (d) Seekor ayam dimasak di dalam sebuah pengukus elektrik. Sebanyak 0.8 kg air pada suhu 30 oC bertukar menjadi wap.
            [Muatan haba tentu air, c = 4.20 × 103 J kg−1 oC−1]
            [Haba pendam tentu pengewapan air, lv = 2.26 × 106 J kg−1]
            A chicken is cooked in an electric steamer. 0.8 kg of water at a temperature of 30 oC turns into steam.
            [Specific heat capacity of water, c = 4.20 × 103 J kg−1 oC−1]
            [Specific latent heat of vaporization of water, lv = 2.26 × 106 J kg−1]
        (i) Hitung tenaga haba yang diserap untuk meningkatkan suhu air tersebut daripada 30 oC ke 100 oC.
            Calculate the heat energy absorbed to raise the temperature of the water from 30 oC to 100 oC. [3 marks]
        (ii) Hitung jumlah tenaga yang diserap untuk mengubah air tersebut menjadi wap.
            Calculate the amount of energy absorbed to change the water into steam. [2 marks]
        "


      EXAMPLE OUTPUT (JSON Object):
      {{
          "result": [
            {{                
              "main_question_number": "3", 
              "main_question_text": {{
                "english":["Diagram 3 shows the planet Venus orbiting around the Sun. The  area  sweeps  out  by  AOB  and  COD  is  equal  in  the  same  time  interval.",
                "[ r1 = 1.08 x 1011 m and mass of the Sun, M = 1.989 x 1030 kg]"],
                "malay": ["Rajah 3 menunjukkan planet Zuhrah yang mengorbit mengelilingi Matahari. Luas yang dicakupi oleh AOB dan COD adalah sama dalam selang masa yang sama.",
                "[ r1 = 1.08 x 1011 m dan jisim Matahari, M = 1.989 x 1030 kg]"]
              }},
              "questions": [
                  {{
                    "question_alphabet": "(a)",
                    "question_text": {{
                        "english": ["State physics law involved."],
                        "malay": ["Nyatakan hukum fizik yang terlibat."],
                    }},
                    "sub_questions": [],
                    "marks": 1
                  }},
                  {{
                    "question_alphabet": "(b)",
                    "question_text": [""],
                    "sub_questions": [
                        {{
                          "sub_question_numeral": "(i)",
                          "sub_question_text": {{
                            "english":["Determine the value of the linear speed of the Venus at point X"],
                            "malay": ["Tentukan nilai laju linear planet Zuhrah di titik X."]
                          }},
                          "marks": 2,
                        }},
                        {{
                          "sub_question_numeral": "(ii)",
                          "sub_question_text": {{
                            "english":["State the change in linear speed of the Venus when moving from point C to D."],
                            "malay": ["Nyatakan perubahan laju linear Zuhrah apabila bergerak dari titik C ke D."]
                          }}
                          "marks": 1,
                        }}
                      ]
                  }},
                  {{
                    "question_alphabet": "c",
                    "question_text": {{
                      "english":["Explain your answer in 3(b)(ii)."],
                      "malay":["Jelaskan jawapan anda dalam 3(b)(ii)."]
                    }}
                    "sub_questions": [],
                    "marks": 2,
                  }}
                ]
            }},
            {{                
              "main_question_number": "7", 
              "main_question_header": {{
                "english":[
                  "Diagram 7.1 shows a glass block with refractive index of 1.47 placed in oil reservoir.",
                  "Diagram 7.2 shows a ray diagram of light travel from oil to the glass block from top view."
                ],
                "malay":[
                  "Rajah 7.1 menunjukkan satu bongkah kaca dengan indek biasan 1.47 berada dalam takungan minyak.",
                  "Rajah 7.2 menunjukkan gambarajah sinar bagi alur cahaya yang merambat dari minyak ke bongkah kaca dari pandangan atas."
                ]
              }},
              "questions": [
                {{
                  "question_alphabet": "(a)",
                  "question_text": {{
                    "english":["What is meant by refractive index?"],
                    "malay":["Apakah yang dimaksudkan dengan indek biasan?"]
                  }},
                  "sub_questions": [],
                  "marks": 1,
                }},
                {{
                  "question_alphabet": "(b)",
                  "question_text": {{
                    "english":["Complete the beam of light when entering the glass block and label the angle of refraction, r."],
                    "malay":["Lengkapkan alur sinar cahaya apabila memasuki blok kaca tersebut dan labelkan sudut biasan, r."]
                  }}
                  "sub_questions": [],
                  "marks": 1
                }},
                {{
                  "question_alphabet": "(c)",
                  "question_text": 
                  {{
                    "english":["Calculate the value of the angle of refraction, when the index of refraction of the glass block is 1.47"],
                    "malay":["Hitung nilai sudut biasan, apabila indeks biasan blok kaca ialah 1.47"]
                  }}
                  "sub_questions": [],
                  "marks": 2
                }},
                {{
                  "question_alphabet": "(d)",
                  "question_text": {{
                    "english":[
                      "Diagram 7.3 shows the arrangement of the apparatus used to create the magic trick of making the glass rod appear to disappear when placed behind the beaker.",
                      "Table 7 shows the different characteristics of the arrangement of apparatus used to produce the trick.",
                      "Based on Table 7, state the appropriate characteristics to make the glass rod disappear from view"
                    ],
                    "malay":[
                      "Rajah 7.3 menunjukkan susunan radas yang digunakan untuk membuat helah silap mata agar rod kaca kelihatan hilang apabila diletakkan di belakang bikar.",
                      "Jadual 7 menunjukkan ciri-ciri yang berbeza bagi susunan radas yang digunakan untuk menghasilkan silap mata tersebut.",
                      "Berdasarkan Jadual 7, nyatakan ciri-ciri yang sesuai untuk membuatkan rod kaca hilang dari pandangan."
                    ]
                  }}
                  "sub_questions": [
                      {{
                          "sub_question_numeral": "(i)",
                          "sub_question_text": {{
                            "english": [
                              "Type of rod",
                              "Reason"
                            ],
                            "malay": [
                              "Jenis rod",
                              "Sebab"
                            ]
                          }}
                          "marks": 2
                      }},
                      {{
                          "sub_question_numeral": "(ii)",
                          "sub_question_text": {{
                            "english": [
                              "Refractive index of the oil",
                              "Reason"
                            ],
                            "malay": [
                              "Indeks biasan minyak",
                              "Sebab"
                            ]
                          }}
                          "marks": 2
                      }}
                  ]
                }},
                {{
                  "question_alphabet": "(e)",
                  "question_text": {{
                    "english":["Based on your answers in 7(d)(i) and 7(d)(ii), choose the most appropriate model to create a perfect magic trick"],
                    "malay":["Berdasarkan jawapan anda dalam 7(d)(i) dan 7(d)(ii), pilih model yang paling sesuai untuk mencipta satu helah silap mata yang sempurna."]
                  }}
                  "marks": 1
                }}
              ]
            }},
            {{                
              "main_question_number": "9", 
              "main_question_header": {{
                "english": ["Diagram 9.1 shows some of the components of the cooling system of a refrigerator using cooling agent with high specific latent heat. Arrows indicate the flow of cooling agent from the compressor to the condenser coil and back to the compressor."],
                "malay": ["Rajah 9.1 menunjukkan sebahagian daripada komponen sistem penyejukan sebuah peti sejuk yang menggunakan agen penyejuk yang mempunyai haba pendam tentu yang tinggi. Anak panah menunjukkan aliran agen penyejuk dari pemampat ke gegelung kondenser dan kembali ke pemampat."]
              }}
              "questions": [
                {{
                  "question_alphabet": "(a)",
                  "question_text": {{
                    "english": ["What is meant by specific latent heat?"],
                    "malay": ["Apakah yang dimaksudkan dengan haba pendam tentu?"]
                  }}
                  "sub_questions": [],
                  "marks": 1,
                }},
                {{
                  "question_alphabet": "(b)",
                  "question_text": {{
                    "english": ["Based on Diagram 9.1 and appropriate physics concepts, explain how the cooling system in a refrigerator works."],
                    "malay": ["Berdasarkan Rajah 9.1 dan konsep fizik yang sesuai, terangkan bagaimana sistem penyejukan dalam peti sejuk berfungsi."]
                  }}
                  "sub_questions": [],
                  "marks": 3
                }},
                {{
                  "question_alphabet": "(c)",
                  "question_text": {{
                    "english": [
                      "Diagram 9.2 shows an electric steamer without a lid.",
                      "You are required to study the characteristics of an electric steamer as shown in Table 9.",
                      "Explain the suitability of each characteristic of an electric steamer. Determine the most effective electric steamer to use to cook large quantities of food more quickly, efficiently, and safely."
                    ],
                    "malay": [
                      "Rajah 9.2 menunjukkan sebuah pengukus elektrik tanpa penutup.",
                      "Anda dikehendaki mengkaji ciri-ciri sebuah pengukus elektrik seperti yang ditunjukkan dalam Jadual 9.",
                      "Terangkan kesesuaian setiap ciri pengukus elektrik. Tentukan pengukus elektrik paling berkesan untuk digunakan bagi memasak makanan yang banyak dengan lebih cepat, cekap, dan selamat."
                    ]
                  }}
                  "sub_questions": [],
                  "marks": 10
                }},
                {{
                  "question_alphabet": "(d)",
                  "question_text": {{
                    "english": [
                      "A chicken is cooked in an electric steamer. 0.8 kg of water at a temperature of 30 oC turns into steam.",
                      "[Specific heat capacity of water, c = 4.20 × 103 J kg−1 oC−1]",
                      "[Specific latent heat of vaporization of water, lv = 2.26 × 106 J kg−1]"],
                    "malay": [
                      "Seekor ayam dimasak di dalam sebuah pengukus elektrik. Sebanyak 0.8 kg air pada suhu 30 oC bertukar menjadi wap.",
                      "[Muatan haba tentu air, c = 4.20 × 103 J kg−1 oC−1]",
                      "[Haba pendam tentu pengewapan air, lv = 2.26 × 106 J kg−1]"
                    ]
                  }}
                  "sub_questions": [
                      {{
                          "sub_question_numeral": "(i)",
                          "sub_question_text": {{
                            "english": ["Calculate the heat energy absorbed to raise the temperature of the water from 30 oC to 100 oC."],
                            "malay": ["Hitung tenaga haba yang diserap untuk meningkatkan suhu air tersebut daripada 30 oC ke 100 oC."]
                          }}
                          "marks": 3
                      }},
                      {{
                          "sub_question_numeral": "(ii)",
                          "sub_question_text": {{
                            "english": ["Calculate the amount of energy absorbed to change the water into steam."],
                            "malay": ["Hitung jumlah tenaga yang diserap untuk mengubah air tersebut menjadi wap."]
                          }}
                          "marks": 2
                      }}
                  ]
                }}
              ]
            }}
          ]
      }}"""""

def prompt3():
  return f"""""Extract questions from this document and put them in a JSON object in the following format:
      VERY IMPORTANT, PLEASE EXTRACT CAREFULLY HERE. CHECK AND FOLLOW THESE INSTRUCTIONS:

      ---

      ### **1. Structure Overview**
      - **Main Question**:
        - Identified by numbers like "1", "2", "3".
        - Includes `main_question_text` for introductory paragraphs (often descriptive containing diagrams, equations, or instructions).
        - Texts MUST be separated into `english` and `malay` arrays. English texts are usually italic fonts.

      - **Questions**:
        - Identified by alphabets like "(a)", "(b)".
        - Includes `question_text` for instructions or descriptions directly related to the question.
        - **DO NOT include sub-question content here.**
        - Sometimes question_text can be empty. Example case: "(c)(i) Sub-question text".
        - Texts MUST be separated into `english` and `malay` arrays. English texts are usually italic fonts.

      - **Sub-Questions**:
        - Identified by numerals like "(i)", "(ii)".
        - Includes `sub_question_text` for specific sub-tasks under the question.
        - Texts MUST be separated into `english` and `malay` arrays. English texts are usually italic fonts.

      ---

      ### **2. Formulas and Equations**:
      - **Include all formulas, equations, or numerical data** exactly as they appear in the document.
      - Treat these elements as part of `main_question_text`, `question_text`, or `sub_question_text` arrays, depending on their context.
      - For example:
        - Input: "Given F = ma, where F is the force..."
        - Output:
          ```json
          {{
            "question_alphabet": "(b)",
            "question_text": {{
              "english": [
                "Given",
                "F = ma, where F is the force, m is the mass, and a is the acceleration."
              ],
              "malay": [
                "Diberikan",
                "F = ma, di mana F ialah daya, m ialah jisim, dan a ialah pecutan."
              ]
            }},
            "sub_questions": [],
            "marks": 2
          }}
          ```

      ---

      ### **3. Key Rules**
      1. **DO NOT DUPLICATE CONTENT**:
        - If a part of the question belongs to a sub-question (e.g., "(i)", "(ii)"), DO NOT include it in `question_text`.
        - `question_text` must ONLY include content directly relevant to the alphabet-level question, excluding any sub-questions.

      2. **Capture Sub-Questions**:
        - If a question includes parts like "(i)" or "(ii)", move those parts to `sub_questions` instead of keeping them in `question_text`.

      3. **Language Separation**:
        - All `main_question_text`, `question_text`, and `sub_question_text` must have separate arrays for `english` and `malay`.

      4. **Group Consecutive Lines of Text**:
        - **Combine consecutive lines of text** into a **single string** within the same array element.
        - Combine consecutive lines of the same language into a single string unless interrupted by:
          - A blank line
          - A new diagram, table, or separator.
        - Only create a new array element if:
          - The paragraph is interrupted by a diagram, table, or significant separator (e.g., blank line or page break).
        - Example:
          - Input:
            ```
            Diagram 3 shows the relationship between force and acceleration.
            F = ma
            where F is the force, m is the mass, and a is the acceleration.
            ```
          - Output:
            ```json
            {{
              "main_question_text": {{
                "english": [
                  "Diagram 3 shows the relationship between force and acceleration. F = ma where F is the force, m is the mass, and a is the acceleration."
                ],
                "malay": [
                  "Rajah 3 menunjukkan hubungan antara daya dan pecutan. F = ma di mana F ialah daya, m ialah jisim, dan a ialah pecutan."
                ]
              }}
            }}
            ```

      5. **Page Break Handling**:
        - If a question continues after a page break, ensure it is treated as the same question unless a new number, alphabet, or numeral starts.

      6. **Diagram or Table Mentions**:
        - Include any diagram or table references (e.g., "On Diagram 2.2...") as part of the respective `main_question_text`, `question_text`, or `sub_question_text`, depending on their context.

      7. **Marks**:
        - Ensure `marks` are assigned only at the correct hierarchy:
          - `marks` for a sub-question are specific to that sub-question.

      8. **Equations/Formulas**:
        - Include formulas as a new item in `question_text` or `sub_question_text`, depending on their location in the PDF.

      9. **Preserve Original Formatting**:
        - Use inline LaTeX-style syntax for equations where needed (e.g., `F = ma`).

      10. **Language-Specific Values**:
        - If numerical data or units are given, include them in both `english` and `malay` arrays.

      ---

      ### **2. Example Scenarios**
      #### Scenario 1: Question with Sub-Questions
      Input:
      "(b) On Diagram 2.2, complete the direction of propagation of water wave in the shallow sea, and draw the wavefronts of the water waves in the shallow sea."
      Expected Output:
      ```json
      {{
        "question_alphabet": "(b)",
        "question_text": {{
          "english": [
            "On Diagram 2.2,"
          ],
          "malay": [
            "Pada Rajah 2.2,"
          ]
        }},
        "sub_questions": [
          {{
            "sub_question_numeral": "(i)",
            "sub_question_text": {{
              "english": [
                "complete the direction of propagation of water wave in the shallow sea."
              ],
              "malay": [
                "lengkapkan arah perambatan gelombang air di laut cetek."
              ]
            }},
            "marks": 1
          }},
          {{
            "sub_question_numeral": "(ii)",
            "sub_question_text": {{
              "english": [
                "draw the wavefronts of the water waves in the shallow sea."
              ],
              "malay": [
                "lukiskan muka gelombang bagi gelombang air di laut cetek."
              ]
            }},
            "marks": 1
          }}
        ],
        "marks": 2
      }}
      ```

      EXAMPLE INPUT (PDF Content):
      "3. Rajah 3 menunjukkan planet Zuhrah yang mengorbit mengelilingi Matahari. Luas yang dicakupi oleh AOB dan COD adalah sama dalam selang masa yang sama.
          [ r1 = 1.08 x 1011 m dan jisim Matahari, M = 1.989 x 1030 kg]
          Diagram 3 shows the planet Venus orbiting around the Sun. The  area  sweeps  out  by  AOB  and  COD  is  equal  in  the  same  time  interval.
          [ r1 = 1.08 x 1011 m and mass of the Sun, M = 1.989 x 1030 kg]

        [[DIAGRAM 3 IMAGE]]
        Rajah 3
        Diagram 3

        (a) Nyatakan hukum fizik yang terlibat.
            State physics law involved. [1 mark]
        (b) (i) Tentukan nilai laju linear planet Zuhrah di titik X.
                Determine the value of the linear speed of the Venus at point X [2 marks]
        (ii) Nyatakan perubahan laju linear Zuhrah apabila bergerak dari titik C ke D.
            State the change in linear speed of the Venus when moving from point C to D. [1 mark]
        (c) Jelaskan jawapan anda dalam 3(b)(ii).
            Explain your answer in 3(b)(ii). [2 mark]
        

        
        7. Rajah 7.1 menunjukkan satu bongkah kaca dengan indek biasan 1.47 berada dalam takungan minyak.
          Diagram 7.1 shows a glass block with refractive index of 1.47 placed in oil reservoir.

        [[DIAGRAM 7.1 IMAGE]]
        Rajah 7.1
        Diagram 7.1

        Rajah 7.2 menunjukkan gambarajah sinar bagi alur cahaya yang merambat dari minyak ke bongkah kaca dari pandangan atas.
        Diagram 7.2 shows a ray diagram of light travel from oil to the glass block from top view.

        [[DIAGRAM 7.2 IMAGE]]
        Rajah 7.2
        Diagram 7.2

        (a) Apakah yang dimaksudkan dengan indeks biasan?
            What is meant by refractive index? [1 mark]
        (b) Lengkapkan alur sinar cahaya apabila memasuki blok kaca tersebut dan labelkan sudut biasan, r.
            Complete the beam of light when entering the glass block and label the angle of refraction, r. [1 mark]
        (c) Hitung nilai sudut biasan, apabila indeks biasan blok kaca ialah 1.47
            Calculate the value of the angle of refraction, when the index of refraction of the glass block is 1.47 [2 mark]
        (d) Rajah 7.3 menunjukkan susunan radas yang digunakan untuk membuat helah silap mata agar rod kaca kelihatan hilang apabila diletakkan di belakang bikar.
            Diagram 7.3 shows the arrangement of the apparatus used to create the magic trick of making the glass rod appear to disappear when placed behind the beaker.

        [[DIAGRAM 7.3 IMAGE]]
        Rajah 7.3
        Diagram 7.3

        Jadual 7 menunjukkan ciri-ciri yang berbeza bagi susunan radas yang digunakan untuk menghasilkan silap mata tersebut.
        Table 7 shows the different characteristics of the arrangement of apparatus used to produce the trick.

        [[TABLE 7]]
        Table 7

        Berdasarkan Jadual 7, nyatakan ciri-ciri yang sesuai untuk membuatkan rod kaca hilang dari pandangan.
        Based on Table 7, state the appropriate characteristics to make the glass rod disappear from view
        (i) Jenis rod
            Type of rod
        ............................................................ (answer_space)
        Sebab/Reason
        ............................................................ (answer_space) [2 marks]

        (ii) Indek biasan minyak
            Refractive index of the oil
        ............................................................ (answer_space)
        Sebab/Reason
        ............................................................ (answer_space) [2 marks]

        (e) Berdasarkan jawapan anda dalam 7(d)(i) dan 7(d)(ii), pilih model yang paling sesuai untuk mencipta satu helah silap mata yang sempurna.
            Based on your answers in 7(d)(i) and 7(d)(ii), choose the most appropriate model to create a perfect magic trick [1 mark]


        9. Rajah 9.1 menunjukkan sebahagian daripada komponen sistem penyejukan sebuah peti sejuk yang menggunakan agen penyejuk yang mempunyai haba pendam tentu yang tinggi. Anak panah menunjukkan aliran agen penyejuk dari pemampat ke gegelung kondenser dan kembali ke pemampat.
          Diagram 9.1 shows some of the components of the cooling system of a refrigerator using cooling agent with high specific latent heat. Arrows indicate the flow of cooling agent from the compressor to the condenser coil and back to the compressor.

        [[DIAGRAM 9.1 IMAGE]]
        Diagram 9.1

        (a) Apakah yang dimaksudkan dengan haba pendam tentu?
            What is meant by specific latent heat? [1 mark]
        (b) Berdasarkan Rajah 9.1 dan konsep fizik yang sesuai, terangkan bagaimana sistem penyejukan dalam peti sejuk berfungsi.
            Based on Diagram 9.1 and appropriate physics concepts, explain how the cooling system in a refrigerator works. [3 marks]
        (c) Rajah 9.2 menunjukkan sebuah pengukus elektrik tanpa penutup.
            Diagram 9.2 shows an electric steamer without a lid. 

        [[DIAGRAM 9.2 IMAGE]]
        Rajah 9.2
        Diagram 9.2

        Anda dikehendaki mengkaji ciri-ciri sebuah pengukus elektrik seperti yang ditunjukkan dalam Jadual 9.
        You are required to study the characteristics of an electric steamer as shown in Table 9.

        [[TABLE 9]]
        Jadual 9
        Table 9

        Terangkan kesesuaian setiap ciri pengukus elektrik. Tentukan pengukus elektrik paling berkesan untuk digunakan bagi memasak makanan yang banyak dengan lebih cepat, cekap, dan selamat.
        Explain the suitability of each characteristic of an electric steamer. Determine the most effective electric steamer to use to cook large quantities of food more quickly, efficiently, and safely. [10 marks]
        (d) Seekor ayam dimasak di dalam sebuah pengukus elektrik. Sebanyak 0.8 kg air pada suhu 30 oC bertukar menjadi wap.
            [Muatan haba tentu air, c = 4.20 × 103 J kg−1 oC−1]
            [Haba pendam tentu pengewapan air, lv = 2.26 × 106 J kg−1]
            A chicken is cooked in an electric steamer. 0.8 kg of water at a temperature of 30 oC turns into steam.
            [Specific heat capacity of water, c = 4.20 × 103 J kg−1 oC−1]
            [Specific latent heat of vaporization of water, lv = 2.26 × 106 J kg−1]
        (i) Hitung tenaga haba yang diserap untuk meningkatkan suhu air tersebut daripada 30 oC ke 100 oC.
            Calculate the heat energy absorbed to raise the temperature of the water from 30 oC to 100 oC. [3 marks]
        (ii) Hitung jumlah tenaga yang diserap untuk mengubah air tersebut menjadi wap.
            Calculate the amount of energy absorbed to change the water into steam. [2 marks]
        "


      EXAMPLE OUTPUT (JSON Object):
      {{
          "result": [
            {{                
              "main_question_number": "3", 
              "main_question_text": {{
                "english":["Diagram 3 shows the planet Venus orbiting around the Sun. The  area  sweeps  out  by  AOB  and  COD  is  equal  in  the  same  time  interval.",
                "[ r1 = 1.08 x 1011 m and mass of the Sun, M = 1.989 x 1030 kg]"],
                "malay": ["Rajah 3 menunjukkan planet Zuhrah yang mengorbit mengelilingi Matahari. Luas yang dicakupi oleh AOB dan COD adalah sama dalam selang masa yang sama.",
                "[ r1 = 1.08 x 1011 m dan jisim Matahari, M = 1.989 x 1030 kg]"]
              }},
              "questions": [
                  {{
                    "question_alphabet": "(a)",
                    "question_text": {{
                        "english": ["State physics law involved."],
                        "malay": ["Nyatakan hukum fizik yang terlibat."],
                    }},
                    "sub_questions": [],
                    "marks": 1
                  }},
                  {{
                    "question_alphabet": "(b)",
                    "question_text": [""],
                    "sub_questions": [
                        {{
                          "sub_question_numeral": "(i)",
                          "sub_question_text": {{
                            "english":["Determine the value of the linear speed of the Venus at point X"],
                            "malay": ["Tentukan nilai laju linear planet Zuhrah di titik X."]
                          }},
                          "marks": 2,
                        }},
                        {{
                          "sub_question_numeral": "(ii)",
                          "sub_question_text": {{
                            "english":["State the change in linear speed of the Venus when moving from point C to D."],
                            "malay": ["Nyatakan perubahan laju linear Zuhrah apabila bergerak dari titik C ke D."]
                          }}
                          "marks": 1,
                        }}
                      ]
                  }},
                  {{
                    "question_alphabet": "c",
                    "question_text": {{
                      "english":["Explain your answer in 3(b)(ii)."],
                      "malay":["Jelaskan jawapan anda dalam 3(b)(ii)."]
                    }}
                    "sub_questions": [],
                    "marks": 2,
                  }}
                ]
            }},
            {{                
              "main_question_number": "7", 
              "main_question_header": {{
                "english":[
                  "Diagram 7.1 shows a glass block with refractive index of 1.47 placed in oil reservoir.",
                  "Diagram 7.2 shows a ray diagram of light travel from oil to the glass block from top view."
                ],
                "malay":[
                  "Rajah 7.1 menunjukkan satu bongkah kaca dengan indek biasan 1.47 berada dalam takungan minyak.",
                  "Rajah 7.2 menunjukkan gambarajah sinar bagi alur cahaya yang merambat dari minyak ke bongkah kaca dari pandangan atas."
                ]
              }},
              "questions": [
                {{
                  "question_alphabet": "(a)",
                  "question_text": {{
                    "english":["What is meant by refractive index?"],
                    "malay":["Apakah yang dimaksudkan dengan indek biasan?"]
                  }},
                  "sub_questions": [],
                  "marks": 1,
                }},
                {{
                  "question_alphabet": "(b)",
                  "question_text": {{
                    "english":["Complete the beam of light when entering the glass block and label the angle of refraction, r."],
                    "malay":["Lengkapkan alur sinar cahaya apabila memasuki blok kaca tersebut dan labelkan sudut biasan, r."]
                  }}
                  "sub_questions": [],
                  "marks": 1
                }},
                {{
                  "question_alphabet": "(c)",
                  "question_text": 
                  {{
                    "english":["Calculate the value of the angle of refraction, when the index of refraction of the glass block is 1.47"],
                    "malay":["Hitung nilai sudut biasan, apabila indeks biasan blok kaca ialah 1.47"]
                  }}
                  "sub_questions": [],
                  "marks": 2
                }},
                {{
                  "question_alphabet": "(d)",
                  "question_text": {{
                    "english":[
                      "Diagram 7.3 shows the arrangement of the apparatus used to create the magic trick of making the glass rod appear to disappear when placed behind the beaker.",
                      "Table 7 shows the different characteristics of the arrangement of apparatus used to produce the trick.",
                      "Based on Table 7, state the appropriate characteristics to make the glass rod disappear from view"
                    ],
                    "malay":[
                      "Rajah 7.3 menunjukkan susunan radas yang digunakan untuk membuat helah silap mata agar rod kaca kelihatan hilang apabila diletakkan di belakang bikar.",
                      "Jadual 7 menunjukkan ciri-ciri yang berbeza bagi susunan radas yang digunakan untuk menghasilkan silap mata tersebut.",
                      "Berdasarkan Jadual 7, nyatakan ciri-ciri yang sesuai untuk membuatkan rod kaca hilang dari pandangan."
                    ]
                  }}
                  "sub_questions": [
                      {{
                          "sub_question_numeral": "(i)",
                          "sub_question_text": {{
                            "english": [
                              "Type of rod",
                              "Reason"
                            ],
                            "malay": [
                              "Jenis rod",
                              "Sebab"
                            ]
                          }}
                          "marks": 2
                      }},
                      {{
                          "sub_question_numeral": "(ii)",
                          "sub_question_text": {{
                            "english": [
                              "Refractive index of the oil",
                              "Reason"
                            ],
                            "malay": [
                              "Indeks biasan minyak",
                              "Sebab"
                            ]
                          }}
                          "marks": 2
                      }}
                  ]
                }},
                {{
                  "question_alphabet": "(e)",
                  "question_text": {{
                    "english":["Based on your answers in 7(d)(i) and 7(d)(ii), choose the most appropriate model to create a perfect magic trick"],
                    "malay":["Berdasarkan jawapan anda dalam 7(d)(i) dan 7(d)(ii), pilih model yang paling sesuai untuk mencipta satu helah silap mata yang sempurna."]
                  }}
                  "marks": 1
                }}
              ]
            }},
            {{                
              "main_question_number": "9", 
              "main_question_header": {{
                "english": ["Diagram 9.1 shows some of the components of the cooling system of a refrigerator using cooling agent with high specific latent heat. Arrows indicate the flow of cooling agent from the compressor to the condenser coil and back to the compressor."],
                "malay": ["Rajah 9.1 menunjukkan sebahagian daripada komponen sistem penyejukan sebuah peti sejuk yang menggunakan agen penyejuk yang mempunyai haba pendam tentu yang tinggi. Anak panah menunjukkan aliran agen penyejuk dari pemampat ke gegelung kondenser dan kembali ke pemampat."]
              }}
              "questions": [
                {{
                  "question_alphabet": "(a)",
                  "question_text": {{
                    "english": ["What is meant by specific latent heat?"],
                    "malay": ["Apakah yang dimaksudkan dengan haba pendam tentu?"]
                  }}
                  "sub_questions": [],
                  "marks": 1,
                }},
                {{
                  "question_alphabet": "(b)",
                  "question_text": {{
                    "english": ["Based on Diagram 9.1 and appropriate physics concepts, explain how the cooling system in a refrigerator works."],
                    "malay": ["Berdasarkan Rajah 9.1 dan konsep fizik yang sesuai, terangkan bagaimana sistem penyejukan dalam peti sejuk berfungsi."]
                  }}
                  "sub_questions": [],
                  "marks": 3
                }},
                {{
                  "question_alphabet": "(c)",
                  "question_text": {{
                    "english": [
                      "Diagram 9.2 shows an electric steamer without a lid.",
                      "You are required to study the characteristics of an electric steamer as shown in Table 9.",
                      "Explain the suitability of each characteristic of an electric steamer. Determine the most effective electric steamer to use to cook large quantities of food more quickly, efficiently, and safely."
                    ],
                    "malay": [
                      "Rajah 9.2 menunjukkan sebuah pengukus elektrik tanpa penutup.",
                      "Anda dikehendaki mengkaji ciri-ciri sebuah pengukus elektrik seperti yang ditunjukkan dalam Jadual 9.",
                      "Terangkan kesesuaian setiap ciri pengukus elektrik. Tentukan pengukus elektrik paling berkesan untuk digunakan bagi memasak makanan yang banyak dengan lebih cepat, cekap, dan selamat."
                    ]
                  }}
                  "sub_questions": [],
                  "marks": 10
                }},
                {{
                  "question_alphabet": "(d)",
                  "question_text": {{
                    "english": [
                      "A chicken is cooked in an electric steamer. 0.8 kg of water at a temperature of 30 oC turns into steam.",
                      "[Specific heat capacity of water, c = 4.20 × 103 J kg−1 oC−1]",
                      "[Specific latent heat of vaporization of water, lv = 2.26 × 106 J kg−1]"],
                    "malay": [
                      "Seekor ayam dimasak di dalam sebuah pengukus elektrik. Sebanyak 0.8 kg air pada suhu 30 oC bertukar menjadi wap.",
                      "[Muatan haba tentu air, c = 4.20 × 103 J kg−1 oC−1]",
                      "[Haba pendam tentu pengewapan air, lv = 2.26 × 106 J kg−1]"
                    ]
                  }}
                  "sub_questions": [
                      {{
                          "sub_question_numeral": "(i)",
                          "sub_question_text": {{
                            "english": ["Calculate the heat energy absorbed to raise the temperature of the water from 30 oC to 100 oC."],
                            "malay": ["Hitung tenaga haba yang diserap untuk meningkatkan suhu air tersebut daripada 30 oC ke 100 oC."]
                          }}
                          "marks": 3
                      }},
                      {{
                          "sub_question_numeral": "(ii)",
                          "sub_question_text": {{
                            "english": ["Calculate the amount of energy absorbed to change the water into steam."],
                            "malay": ["Hitung jumlah tenaga yang diserap untuk mengubah air tersebut menjadi wap."]
                          }}
                          "marks": 2
                      }}
                  ]
                }}
              ]
            }}
          ]
      }}"""""


def configure_model():
  genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
  return genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config={"response_mime_type": "application/json"},
  )

@app.post("/extract_questions")
async def analyse_pdf(file: UploadFile = File(...)):
    try:
        # Check if the uploaded file is a PDF
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        # Read the PDF content (await the asynchronous read)
        pdf_content = await file.read()

        # Encode the PDF content in Base64
        pdf_content_base64 = base64.standard_b64encode(pdf_content).decode("utf-8")

        # Configure the Gemini AI model
        model = configure_model()

        # Define the prompt for question extraction
        prompt = prompt3()

        # Generate content using the Gemini AI model
        print(prompt)
        response = model.generate_content([
            {'mime_type': 'application/pdf', 'data': pdf_content_base64}, 
            prompt
        ])

        if not response:
            raise Exception("Failed to generate response from the AI model.")
        
        print(json.loads(response.text))

        # Return the extracted questions as JSON
        return {
            "status": "success",
            "message": "Success",
            "data": json.loads(response.text)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": str(e),
                "data": None,
            },
        )